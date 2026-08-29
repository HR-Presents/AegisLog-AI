from __future__ import annotations

import hashlib
import os
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
from .trends import TrendSnapshot, TrendTracker, render_trends
from .watch_profiles import WatchProfile, filter_events, filter_findings, get_profile

_PREFIX_BYTES = 128


@dataclass(frozen=True)
class FileCursor:
    offset: int
    identity: tuple[int, int]
    prefix_digest: str


def _file_identity(path: Path) -> tuple[int, int]:
    stat = path.stat()
    return (int(stat.st_dev), int(stat.st_ino))


def _prefix_digest(path: Path, length: int) -> str:
    if length <= 0:
        return ""
    with path.open("rb") as handle:
        data = handle.read(min(length, _PREFIX_BYTES))
    return hashlib.sha256(data).hexdigest()


def initial_cursor(path: Path, from_start: bool = False) -> FileCursor:
    size = path.stat().st_size
    offset = 0 if from_start else size
    return FileCursor(offset, _file_identity(path), _prefix_digest(path, offset))


@dataclass
class RealtimeState:
    source: str
    window_size: int = 500
    alert_ttl_seconds: int = 300
    watch_profile: str = "all"
    started_at: float = field(default_factory=time.monotonic)
    total_lines: int = 0
    total_bytes: int = 0
    trend_tracker: TrendTracker = field(default_factory=TrendTracker)
    _lines: deque[str] = field(default_factory=deque)
    _recent_findings: deque[Finding] = field(default_factory=lambda: deque(maxlen=12))
    _seen_fingerprints: dict[tuple[str, str, str, str], float] = field(default_factory=dict)
    _events_cache: list[Event] = field(default_factory=list)
    _findings_cache: list[Finding] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.window_size < 20:
            raise ValueError("window_size must be at least 20")
        get_profile(self.watch_profile)
        self._lines = deque(self._lines, maxlen=self.window_size)

    def ingest(self, lines: list[str], now: float | None = None) -> int:
        if not lines:
            return 0
        stamp = time.monotonic() if now is None else now
        for line in lines:
            self._lines.append(line)
            self.total_lines += 1
            self.total_bytes += len(line.encode("utf-8", errors="replace"))
        self.trend_tracker.ingest(lines, stamp)
        self._refresh_snapshot()
        self._expire_seen(stamp)
        for finding in self._findings_cache:
            fp = (finding.severity, finding.category, finding.title, finding.evidence)
            if fp not in self._seen_fingerprints:
                self._recent_findings.appendleft(finding)
            self._seen_fingerprints[fp] = stamp
        return len(lines)

    def _refresh_snapshot(self) -> None:
        raw = list(self._lines)
        self._events_cache = [parse_line(line) for line in raw]
        self._findings_cache = analyze_lines(raw)

    def _expire_seen(self, now: float) -> None:
        cutoff = now - max(self.alert_ttl_seconds, 1)
        expired = [fp for fp, seen_at in self._seen_fingerprints.items() if seen_at < cutoff]
        for fp in expired:
            self._seen_fingerprints.pop(fp, None)

    @property
    def profile(self) -> WatchProfile:
        return get_profile(self.watch_profile)

    @property
    def lines(self) -> list[str]:
        return list(self._lines)

    @property
    def rolling_count(self) -> int:
        return len(self._lines)

    @property
    def recent_findings(self) -> tuple[Finding, ...]:
        return tuple(filter_findings(self.profile, list(self._recent_findings)))

    @property
    def events(self) -> list[Event]:
        return list(self._events_cache)

    @property
    def focused_events(self) -> list[Event]:
        return filter_events(self.profile, self.events)

    @property
    def findings(self) -> list[Finding]:
        return list(self._findings_cache)

    @property
    def focused_findings(self) -> list[Finding]:
        return filter_findings(self.profile, self.findings)

    @property
    def trends(self) -> TrendSnapshot:
        return self.trend_tracker.snapshot()

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


def _recent_table(findings: list[Finding], profile: WatchProfile) -> Table:
    table = Table(title=f"Recent findings — {profile.label}", expand=True, show_lines=True)
    table.add_column("Severity", width=10)
    table.add_column("Category", width=18)
    table.add_column("Finding", width=34)
    table.add_column("Evidence")
    for finding in findings[:8]:
        table.add_row(finding.severity, Text(finding.category), Text(finding.title), Text(finding.evidence))
    if not findings:
        table.add_row("-", "-", f"No {profile.label.lower()} profile matches yet", "AegisLog continues monitoring all incoming lines")
    return table


def render_realtime(state: RealtimeState) -> RenderableType:
    profile = state.profile
    events = state.focused_events
    findings = state.focused_findings
    trend = state.trends
    severities = Counter(item.severity for item in findings)
    categories = Counter(item.category for item in findings)
    levels = Counter((event.level or "unknown").upper() for event in events if event.message)
    services = Counter(event.service or "unknown" for event in events if event.message)
    incidents = correlate(findings)
    anomalies = score_events(events)
    critical = severities.get("CRITICAL", 0)
    high = severities.get("HIGH", 0)
    medium = severities.get("MEDIUM", 0)
    allowed_metrics = set(profile.trend_metrics)
    focused_spikes = sum(1 for item in trend.metrics if item.name in allowed_metrics and item.state == "SPIKE")

    header = Panel(
        Align.center(Text(f"AEGISLOG AI  v{__version__}\nREAL-TIME DEFENSIVE MONITOR\n{state.source}\nPROFILE: {profile.label.upper()}", style="bold")),
        subtitle=f"{profile.description} • Ctrl+C to stop",
    )
    metrics = Columns(
        [
            _metric("Lines received", f"{state.total_lines:,}", f"window {state.rolling_count:,}/{state.window_size:,}"),
            _metric("Event rate", f"{state.lines_per_second:.1f}/s"),
            _metric("Rate spikes", str(focused_spikes), f"{trend.window_seconds}s profile baseline"),
            _metric("Profile findings", str(len(findings)), f"{critical} critical • {high} high • {medium} medium"),
            _metric("Incidents", str(len(incidents))),
            _metric("Anomalies", str(len(anomalies))),
            _metric("Risk", _risk(severities)),
        ],
        equal=True,
        expand=True,
    )
    overview = Columns(
        [
            _counter_table("Profile categories", categories),
            _counter_table("Profile log levels", levels),
            _counter_table("Profile services", services),
        ],
        equal=True,
        expand=True,
    )
    status = Panel(
        Text(
            f"Monitoring is read-only. {state.total_bytes:,} bytes ingested in {state.elapsed:.1f}s. "
            f"The {profile.label} profile changes terminal emphasis only; all input remains locally analyzed and no remediation is performed."
        ),
        title="Live status",
    )
    return Group(
        header,
        metrics,
        overview,
        render_trends(trend, profile.trend_metrics),
        _recent_table(list(state.recent_findings), profile),
        status,
    )


def read_new_lines_cursor(path: Path, cursor: FileCursor) -> tuple[list[str], FileCursor]:
    """Read appended UTF-8 text using byte offsets and detect truncation or replacement."""
    identity = _file_identity(path)
    size = path.stat().st_size
    current_prefix = _prefix_digest(path, cursor.offset)
    offset = cursor.offset
    replaced = identity != cursor.identity or (cursor.prefix_digest and current_prefix != cursor.prefix_digest)
    if replaced or size < offset:
        offset = 0
    with path.open("rb") as handle:
        handle.seek(offset, os.SEEK_SET)
        data = handle.read()
        new_offset = handle.tell()
    text = data.decode("utf-8", errors="replace")
    new_prefix = _prefix_digest(path, new_offset)
    return text.splitlines(keepends=True), FileCursor(new_offset, identity, new_prefix)


def read_new_lines(path: Path, offset: int) -> tuple[list[str], int]:
    """Backward-compatible byte-safe appended-line reader using a numeric offset."""
    cursor = FileCursor(offset, _file_identity(path), _prefix_digest(path, offset))
    lines, cursor = read_new_lines_cursor(path, cursor)
    return lines, cursor.offset
