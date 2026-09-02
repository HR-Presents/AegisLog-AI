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
from .theme import ACCENT, ACCENT_SOFT, ANOMALY, INCIDENT, MUTED, SUCCESS, risk_style, severity_text
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
    last_activity_at: float | None = None
    trend_tracker: TrendTracker = field(default_factory=TrendTracker)
    _lines: deque[str] = field(default_factory=deque)
    _recent_findings: deque[Finding] = field(default_factory=lambda: deque(maxlen=12))
    _seen_fingerprints: dict[tuple[str, str, str], float] = field(default_factory=dict)
    _events_cache: list[Event] = field(default_factory=list)
    _findings_cache: list[Finding] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.window_size < 20:
            raise ValueError("window_size must be at least 20")
        get_profile(self.watch_profile)
        self._lines = deque(self._lines, maxlen=self.window_size)

    @staticmethod
    def _finding_key(finding: Finding) -> tuple[str, str, str]:
        return (finding.severity, finding.category, finding.title)

    def ingest(self, lines: list[str], now: float | None = None) -> int:
        if not lines:
            return 0
        stamp = time.monotonic() if now is None else now
        self.last_activity_at = stamp
        for line in lines:
            self._lines.append(line)
            self.total_lines += 1
            self.total_bytes += len(line.encode("utf-8", errors="replace"))
        self.trend_tracker.ingest(lines, stamp)
        self._refresh_snapshot()
        self._expire_seen(stamp)
        for finding in self._findings_cache:
            key = self._finding_key(finding)
            self._recent_findings = deque(
                (item for item in self._recent_findings if self._finding_key(item) != key),
                maxlen=12,
            )
            self._recent_findings.appendleft(finding)
            self._seen_fingerprints[key] = stamp
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

    @property
    def activity_age(self) -> float | None:
        if self.last_activity_at is None:
            return None
        return max(time.monotonic() - self.last_activity_at, 0.0)


def _risk(severities: Counter[str]) -> str:
    if severities.get("CRITICAL"):
        return "CRITICAL"
    if severities.get("HIGH"):
        return "HIGH"
    if severities.get("MEDIUM"):
        return "REVIEW"
    return "CLEAR"


def _metric(title: str, value: str, subtitle: str = "", *, value_style: str = "bold", border_style: str = ACCENT_SOFT) -> Panel:
    text = Text(value, justify="center", style=value_style)
    if subtitle:
        text.append(f"\n{subtitle}", style=MUTED)
    return Panel(Align.center(text), title=title, title_align="left", border_style=border_style, padding=(0, 1))


def _counter_table(title: str, values: Counter[str], limit: int = 6) -> Table:
    table = Table(title=title, title_style=f"bold {ACCENT}", expand=True, border_style=ACCENT_SOFT)
    table.add_column("Name")
    table.add_column("Count", justify="right", style=ACCENT)
    for name, count in values.most_common(limit):
        table.add_row(Text(str(name)), str(count))
    if not values:
        table.add_row(Text("None", style=MUTED), "0")
    return table


def _recent_table(findings: list[Finding], profile: WatchProfile) -> Table:
    table = Table(
        title=f"Recent findings — {profile.label}",
        title_style=f"bold {ACCENT}",
        expand=True,
        show_lines=True,
        border_style=ACCENT_SOFT,
    )
    table.add_column("Severity", width=10)
    table.add_column("Category", width=18)
    table.add_column("Finding", width=34)
    table.add_column("Evidence")
    for finding in findings[:8]:
        table.add_row(severity_text(finding.severity), Text(finding.category), Text(finding.title), Text(finding.evidence))
    if not findings:
        table.add_row(
            "-",
            "-",
            Text(f"No {profile.label.lower()} profile matches yet", style=SUCCESS),
            Text("Waiting for matching activity; all incoming lines are still analyzed locally", style=MUTED),
        )
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
    activity_age = state.activity_age
    if activity_age is None:
        activity = "waiting for new lines"
    elif activity_age < 2:
        activity = "receiving now"
    else:
        activity = f"last activity {activity_age:.0f}s ago"

    header_text = Text(justify="center")
    header_text.append("AEGISLOG AI", style=f"bold {ACCENT}")
    header_text.append(f"  v{__version__}\n", style=MUTED)
    header_text.append("REAL-TIME DEFENSIVE MONITOR\n", style="bold white")
    header_text.append(state.source, style=ACCENT_SOFT)
    header_text.append("\nPROFILE: ", style=MUTED)
    header_text.append(profile.label.upper(), style=f"bold {ACCENT}")
    header = Panel(
        Align.center(header_text),
        border_style=ACCENT,
        subtitle=f"{profile.description} • Ctrl+C to stop",
        subtitle_align="right",
    )

    risk = _risk(severities)
    metrics = Columns(
        [
            _metric("Lines received", f"{state.total_lines:,}", f"window {state.rolling_count:,}/{state.window_size:,}", value_style=f"bold {ACCENT}"),
            _metric("Average rate", f"{state.lines_per_second:.1f}/s", activity, value_style="bold white"),
            _metric("Rate spikes", str(focused_spikes), f"{trend.window_seconds}s rolling baseline", value_style="bold yellow" if focused_spikes else f"bold {SUCCESS}", border_style="yellow" if focused_spikes else SUCCESS),
            _metric("Profile findings", str(len(findings)), f"{critical} critical • {high} high • {medium} medium", value_style="bold white"),
            _metric("Incidents", str(len(incidents)), value_style=f"bold {INCIDENT}", border_style=INCIDENT),
            _metric("Anomalies", str(len(anomalies)), value_style=f"bold {ANOMALY}", border_style=ANOMALY),
            _metric("Risk", risk, value_style=f"bold {risk_style(risk)}", border_style=risk_style(risk)),
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
    if state.total_lines == 0:
        mode_note = "Waiting for NEW lines appended after monitoring started. Existing file contents are intentionally skipped unless --from-start is used. "
        status_style = "yellow"
    else:
        mode_note = "Following new appended lines. "
        status_style = SUCCESS
    status_text = Text(mode_note, style=status_style)
    status_text.append(
        f"Monitoring is read-only. {state.total_bytes:,} bytes ingested in {state.elapsed:.1f}s. "
        f"The {profile.label} profile changes terminal emphasis only; all input remains locally analyzed and no remediation is performed.",
        style="white",
    )
    status = Panel(status_text, title="Live status", title_align="left", border_style=status_style)
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
