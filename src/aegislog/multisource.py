from __future__ import annotations

import time
from collections import Counter, deque
from dataclasses import dataclass, field
from pathlib import Path

from rich.align import Align
from rich.columns import Columns
from rich.console import Group, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from . import __version__
from .anomaly import score_events
from .engine import Finding, analyze_lines
from .incidents import correlate
from .parsers import parse_line
from .realtime import read_new_lines


@dataclass(frozen=True)
class SourceCursor:
    path: Path
    offset: int = 0


@dataclass(frozen=True)
class LiveAlert:
    sequence: int
    severity: str
    category: str
    source: str
    title: str
    evidence: str


@dataclass
class MultiSourceState:
    sources: tuple[Path, ...]
    window_size: int = 1000
    trend_seconds: int = 60
    started_at: float = field(default_factory=time.monotonic)
    total_lines: int = 0
    total_bytes: int = 0
    _lines: deque[tuple[str, str]] = field(default_factory=deque)
    _arrivals: deque[float] = field(default_factory=deque)
    _alerts: deque[LiveAlert] = field(default_factory=lambda: deque(maxlen=15))
    _seen: set[tuple[str, str, str, str]] = field(default_factory=set)
    _sequence: int = 0
    source_counts: Counter[str] = field(default_factory=Counter)

    def __post_init__(self) -> None:
        if self.window_size < 20:
            raise ValueError("window_size must be at least 20")
        self._lines = deque(self._lines, maxlen=self.window_size)

    def ingest(self, source: Path, lines: list[str], now: float | None = None) -> int:
        if not lines:
            return 0
        stamp = time.monotonic() if now is None else now
        label = source.name
        for line in lines:
            self._lines.append((label, line))
            self._arrivals.append(stamp)
            self.total_lines += 1
            self.total_bytes += len(line.encode("utf-8", errors="replace"))
            self.source_counts[label] += 1
        self._trim_arrivals(stamp)
        self._refresh_alerts(label)
        return len(lines)

    def _trim_arrivals(self, now: float) -> None:
        cutoff = now - self.trend_seconds
        while self._arrivals and self._arrivals[0] < cutoff:
            self._arrivals.popleft()

    def _refresh_alerts(self, source: str) -> None:
        for finding in self.findings:
            fp = (finding.severity, finding.category, finding.title, finding.evidence)
            if fp in self._seen:
                continue
            self._seen.add(fp)
            self._sequence += 1
            self._alerts.appendleft(
                LiveAlert(self._sequence, finding.severity, finding.category, source, finding.title, finding.evidence)
            )

    @property
    def raw_lines(self) -> list[str]:
        return [line for _, line in self._lines]

    @property
    def findings(self) -> list[Finding]:
        return analyze_lines(self.raw_lines)

    @property
    def events(self):
        return [parse_line(line) for line in self.raw_lines]

    @property
    def alerts(self) -> tuple[LiveAlert, ...]:
        return tuple(self._alerts)

    @property
    def recent_eps(self) -> float:
        self._trim_arrivals(time.monotonic())
        return len(self._arrivals) / max(float(self.trend_seconds), 1.0)

    @property
    def lifetime_eps(self) -> float:
        return self.total_lines / max(time.monotonic() - self.started_at, 0.001)


def initial_offsets(paths: tuple[Path, ...], from_start: bool) -> dict[Path, int]:
    return {path: 0 if from_start else path.stat().st_size for path in paths}


def poll_sources(paths: tuple[Path, ...], offsets: dict[Path, int]) -> tuple[list[tuple[Path, list[str]]], dict[Path, int]]:
    batches: list[tuple[Path, list[str]]] = []
    updated = dict(offsets)
    for path in paths:
        if not path.exists() or not path.is_file():
            continue
        lines, offset = read_new_lines(path, updated.get(path, 0))
        updated[path] = offset
        if lines:
            batches.append((path, lines))
    return batches, updated


def _risk(counts: Counter[str]) -> str:
    if counts.get("CRITICAL"):
        return "CRITICAL"
    if counts.get("HIGH"):
        return "HIGH"
    if counts.get("MEDIUM"):
        return "REVIEW"
    return "CLEAR"


def _metric(title: str, value: str, subtitle: str = "") -> Panel:
    body = Text(value, justify="center", style="bold")
    if subtitle:
        body.append(f"\n{subtitle}", style="dim")
    return Panel(Align.center(body), title=title, padding=(0, 1))


def _counter(title: str, values: Counter[str], limit: int = 6) -> Table:
    table = Table(title=title, expand=True)
    table.add_column("Name")
    table.add_column("Count", justify="right")
    for name, count in values.most_common(limit):
        table.add_row(Text(str(name)), str(count))
    if not values:
        table.add_row("None", "0")
    return table


def _alerts_table(state: MultiSourceState) -> Table:
    table = Table(title="Live security alert feed", expand=True, show_lines=True)
    table.add_column("#", justify="right", width=5)
    table.add_column("Severity", width=10)
    table.add_column("Source", width=18)
    table.add_column("Category", width=18)
    table.add_column("Alert", width=34)
    table.add_column("Evidence")
    for item in state.alerts[:10]:
        table.add_row(str(item.sequence), item.severity, Text(item.source), Text(item.category), Text(item.title), Text(item.evidence))
    if not state.alerts:
        table.add_row("-", "-", "-", "-", "Waiting for high-signal activity", "New detections appear here automatically")
    return table


def render_multisource(state: MultiSourceState) -> RenderableType:
    events = state.events
    findings = state.findings
    severity = Counter(item.severity for item in findings)
    categories = Counter(item.category for item in findings)
    levels = Counter((event.level or "unknown").upper() for event in events if event.message)
    services = Counter(event.service or "unknown" for event in events if event.message)
    incidents = correlate(findings)
    anomalies = score_events(events)
    sources = ", ".join(path.name for path in state.sources)
    header = Panel(
        Align.center(Text(f"AEGISLOG AI  v{__version__}\nMULTI-SOURCE REAL-TIME SOC\n{sources}", style="bold")),
        subtitle="Unified live correlation • local/read-only • Ctrl+C to stop",
    )
    metrics = Columns(
        [
            _metric("Sources", str(len(state.sources)), f"{len(state._lines):,}/{state.window_size:,} rolling lines"),
            _metric("Events", f"{state.total_lines:,}"),
            _metric("Live EPS", f"{state.recent_eps:.2f}/s", f"lifetime {state.lifetime_eps:.2f}/s"),
            _metric("Findings", str(len(findings))),
            _metric("Incidents", str(len(incidents))),
            _metric("Anomalies", str(len(anomalies))),
            _metric("Risk", _risk(severity)),
        ],
        equal=True,
        expand=True,
    )
    overview = Columns(
        [
            _counter("Events by source", state.source_counts),
            _counter("Finding categories", categories),
            _counter("Log levels", levels),
            _counter("Top services", services),
        ],
        equal=True,
        expand=True,
    )
    status = Panel(
        Text(
            f"{state.total_bytes:,} bytes ingested. Correlation runs across all monitored sources in one rolling window. "
            f"Live EPS uses the most recent {state.trend_seconds}s of arrivals."
        ),
        title="Monitoring status",
    )
    return Group(header, metrics, overview, _alerts_table(state), status)
