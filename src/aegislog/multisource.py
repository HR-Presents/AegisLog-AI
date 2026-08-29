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
from .parsers import Event, parse_line
from .realtime import FileCursor, initial_cursor, read_new_lines, read_new_lines_cursor
from .trends import TrendSnapshot, TrendTracker, render_trends


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
    alert_ttl_seconds: int = 300
    started_at: float = field(default_factory=time.monotonic)
    total_lines: int = 0
    total_bytes: int = 0
    trend_tracker: TrendTracker = field(default_factory=TrendTracker)
    _lines: deque[tuple[str, str]] = field(default_factory=deque)
    _arrivals: deque[float] = field(default_factory=deque)
    _alerts: deque[LiveAlert] = field(default_factory=lambda: deque(maxlen=15))
    _seen: dict[tuple[str, str, str, str], float] = field(default_factory=dict)
    _sequence: int = 0
    _events_cache: list[Event] = field(default_factory=list)
    _findings_cache: list[Finding] = field(default_factory=list)
    source_counts: Counter[str] = field(default_factory=Counter)

    def __post_init__(self) -> None:
        if self.window_size < 20:
            raise ValueError("window_size must be at least 20")
        self._lines = deque(self._lines, maxlen=self.window_size)
        if self.trend_tracker.window_seconds != self.trend_seconds:
            self.trend_tracker = TrendTracker(window_seconds=self.trend_seconds)

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
        self.trend_tracker.ingest(lines, stamp)
        self._trim_arrivals(stamp)
        self._refresh_snapshot()
        self._refresh_alerts(stamp)
        return len(lines)

    def _trim_arrivals(self, now: float) -> None:
        cutoff = now - self.trend_seconds
        while self._arrivals and self._arrivals[0] < cutoff:
            self._arrivals.popleft()

    def _refresh_snapshot(self) -> None:
        raw = [line for _, line in self._lines]
        self._events_cache = [parse_line(line) for line in raw]
        self._findings_cache = analyze_lines(raw)

    def _expire_seen(self, now: float) -> None:
        cutoff = now - max(self.alert_ttl_seconds, 1)
        expired = [fp for fp, seen_at in self._seen.items() if seen_at < cutoff]
        for fp in expired:
            self._seen.pop(fp, None)

    def _source_for_finding(self, finding: Finding) -> str:
        evidence = finding.evidence.strip().lower()
        title = finding.title.strip().lower()
        for label, line in reversed(self._lines):
            candidate = line.lower()
            if evidence and evidence in candidate:
                return label
            if title and title in candidate:
                return label
        return "correlated"

    def _refresh_alerts(self, now: float) -> None:
        self._expire_seen(now)
        for finding in self._findings_cache:
            fp = (finding.severity, finding.category, finding.title, finding.evidence)
            if fp not in self._seen:
                self._sequence += 1
                self._alerts.appendleft(
                    LiveAlert(
                        self._sequence,
                        finding.severity,
                        finding.category,
                        self._source_for_finding(finding),
                        finding.title,
                        finding.evidence,
                    )
                )
            self._seen[fp] = now

    @property
    def raw_lines(self) -> list[str]:
        return [line for _, line in self._lines]

    @property
    def rolling_count(self) -> int:
        return len(self._lines)

    @property
    def findings(self) -> list[Finding]:
        return list(self._findings_cache)

    @property
    def events(self) -> list[Event]:
        return list(self._events_cache)

    @property
    def alerts(self) -> tuple[LiveAlert, ...]:
        return tuple(self._alerts)

    @property
    def trends(self) -> TrendSnapshot:
        return self.trend_tracker.snapshot()

    @property
    def recent_eps(self) -> float:
        self._trim_arrivals(time.monotonic())
        return len(self._arrivals) / max(float(self.trend_seconds), 1.0)

    @property
    def lifetime_eps(self) -> float:
        return self.total_lines / max(time.monotonic() - self.started_at, 0.001)


def initial_cursors(paths: tuple[Path, ...], from_start: bool) -> dict[Path, FileCursor]:
    return {path: initial_cursor(path, from_start=from_start) for path in paths}


def poll_sources(
    paths: tuple[Path, ...], cursors: dict[Path, FileCursor] | dict[Path, int]
) -> tuple[list[tuple[Path, list[str]]], dict[Path, FileCursor] | dict[Path, int]]:
    batches: list[tuple[Path, list[str]]] = []
    updated = dict(cursors)
    legacy = all(isinstance(value, int) for value in updated.values())
    for path in paths:
        if not path.exists() or not path.is_file():
            continue
        if legacy:
            offset = int(updated.get(path, 0))
            lines, offset = read_new_lines(path, offset)
            updated[path] = offset
        else:
            cursor = updated.get(path)
            if not isinstance(cursor, FileCursor):
                cursor = initial_cursor(path, from_start=True)
            lines, cursor = read_new_lines_cursor(path, cursor)
            updated[path] = cursor
        if lines:
            batches.append((path, lines))
    return batches, updated


def initial_offsets(paths: tuple[Path, ...], from_start: bool) -> dict[Path, int]:
    """Compatibility helper retained for callers that only need starting byte offsets."""
    return {path: 0 if from_start else path.stat().st_size for path in paths}


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
    trend = state.trends
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
            _metric("Sources", str(len(state.sources)), f"{state.rolling_count:,}/{state.window_size:,} rolling lines"),
            _metric("Events", f"{state.total_lines:,}"),
            _metric("Live EPS", f"{state.recent_eps:.2f}/s", f"lifetime {state.lifetime_eps:.2f}/s"),
            _metric("Rate spikes", str(trend.spike_count), f"{trend.window_seconds}s baseline"),
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
            f"Live EPS and rate baselines use the most recent {state.trend_seconds}s of arrivals."
        ),
        title="Monitoring status",
    )
    return Group(header, metrics, overview, render_trends(trend), _alerts_table(state), status)
