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


@dataclass
class RealtimeState:
    source: str
    window_size: int = 500
    started_at: float = field(default_factory=time.monotonic)
    total_lines: int = 0
    total_bytes: int = 0
    _lines: deque[str] = field(default_factory=deque)
    _recent_findings: deque[Finding] = field(default_factory=lambda: deque(maxlen=12))
    _seen_fingerprints: set[tuple[str, str, str, str]] = field(default_factory=set)

    def __post_init__(self) -> None:
        if self.window_size < 20:
            raise ValueError("window_size must be at least 20")
        self._lines = deque(self._lines, maxlen=self.window_size)

    def ingest(self, lines: list[str]) -> int:
        if not lines:
            return 0
        for line in lines:
            self._lines.append(line)
            self.total_lines += 1
            self.total_bytes += len(line.encode("utf-8", errors="replace"))
        for finding in analyze_lines(list(self._lines)):
            fp = (finding.severity, finding.category, finding.title, finding.evidence)
            if fp not in self._seen_fingerprints:
                self._recent_findings.appendleft(finding)
                self._seen_fingerprints.add(fp)
        return len(lines)

    @property
    def lines(self) -> list[str]:
        return list(self._lines)

    @property
    def events(self) -> list[Event]:
        return [parse_line(line) for line in self._lines]

    @property
    def findings(self) -> list[Finding]:
        return analyze_lines(self.lines)

    @property
    def elapsed(self) -> float:
        return max(time.monotonic() - self.started_at, 0.001)

    @property
    def lines_per_second(self) -> float:
        return self.total_lines / self.elapsed


def _risk(severities: Counter[str]) -> str:
    if severities.get("CRITICAL"):
        return "CRITICAL"
    if severities.get("HIGH"):
        return "HIGH"
    if severities.get("MEDIUM"):
        return "REVIEW"
    return "CLEAR"


def _metric(title: str, value: str, subtitle: str = "") -> Panel:
    text = Text(value, justify="center", style="bold")
    if subtitle:
        text.append(f"\n{subtitle}", style="dim")
    return Panel(Align.center(text), title=title, padding=(0, 1))


def _counter_table(title: str, values: Counter[str], limit: int = 6) -> Table:
    table = Table(title=title, expand=True)
    table.add_column("Name")
    table.add_column("Count", justify="right")
    for name, count in values.most_common(limit):
        table.add_row(Text(str(name)), str(count))
    if not values:
        table.add_row("None", "0")
    return table


def _recent_table(findings: list[Finding]) -> Table:
    table = Table(title="Recent high-signal findings", expand=True, show_lines=True)
    table.add_column("Severity", width=10)
    table.add_column("Category", width=18)
    table.add_column("Finding", width=34)
    table.add_column("Evidence")
    for finding in findings[:8]:
        table.add_row(finding.severity, Text(finding.category), Text(finding.title), Text(finding.evidence))
    if not findings:
        table.add_row("-", "-", "Waiting for detectable activity", "AegisLog is monitoring new log lines")
    return table


def render_realtime(state: RealtimeState) -> RenderableType:
    events = state.events
    findings = state.findings
    severities = Counter(item.severity for item in findings)
    categories = Counter(item.category for item in findings)
    levels = Counter((event.level or "unknown").upper() for event in events if event.message)
    services = Counter(event.service or "unknown" for event in events if event.message)
    incidents = correlate(findings)
    anomalies = score_events(events)
    critical = severities.get("CRITICAL", 0)
    high = severities.get("HIGH", 0)
    medium = severities.get("MEDIUM", 0)

    header = Panel(
        Align.center(Text(f"AEGISLOG AI  v{__version__}\nREAL-TIME DEFENSIVE MONITOR\n{state.source}", style="bold")),
        subtitle="Live file monitoring • rolling correlation • Ctrl+C to stop",
    )
    metrics = Columns(
        [
            _metric("Lines received", f"{state.total_lines:,}", f"window {len(state.lines):,}/{state.window_size:,}"),
            _metric("Event rate", f"{state.lines_per_second:.1f}/s"),
            _metric("Active findings", str(len(findings)), f"{critical} critical • {high} high • {medium} medium"),
            _metric("Incidents", str(len(incidents))),
            _metric("Anomalies", str(len(anomalies))),
            _metric("Risk", _risk(severities)),
        ],
        equal=True,
        expand=True,
    )
    overview = Columns(
        [
            _counter_table("Finding categories", categories),
            _counter_table("Log levels", levels),
            _counter_table("Top services", services),
        ],
        equal=True,
        expand=True,
    )
    status = Panel(
        Text(
            f"Monitoring is read-only. {state.total_bytes:,} bytes ingested in {state.elapsed:.1f}s. "
            "New lines are analyzed automatically with rolling correlation and anomaly scoring."
        ),
        title="Live status",
    )
    return Group(header, metrics, overview, _recent_table(list(state._recent_findings)), status)


def read_new_lines(path: Path, offset: int) -> tuple[list[str], int]:
    """Read only lines appended since offset; recover safely after truncation."""
    size = path.stat().st_size
    if size < offset:
        offset = 0
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        handle.seek(offset)
        lines = handle.readlines()
        new_offset = handle.tell()
    return lines, new_offset
