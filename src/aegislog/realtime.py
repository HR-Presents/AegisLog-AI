from __future__ import annotations

import hashlib
import os
import time
from collections import Counter, deque
from dataclasses import dataclass, field
from pathlib import Path

from rich.align import Align
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
_MAX_READ_BYTES = 4_000_000
_MAX_PENDING_LINE_BYTES = 1_000_000


@dataclass(frozen=True)
class FileCursor:
    offset: int
    identity: tuple[int, int]
    prefix_digest: str
    pending: bytes = b""
    pending_truncated: bool = False
    dropped_bytes: int = 0
    source_available: bool = True
    reset_reason: str | None = None


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


def _bounded_complete_lines(
    data: bytes,
    pending: bytes,
    pending_truncated: bool,
    dropped_bytes: int,
) -> tuple[list[str], bytes, bool, int]:
    """Return only newline-complete lines while bounding a partial line by bytes."""
    lines: list[str] = []

    if pending_truncated:
        newline = data.find(b"\n")
        if newline < 0:
            return lines, pending, True, dropped_bytes + len(data)
        dropped_bytes += newline
        lines.append((pending + b" [TRUNCATED]\n").decode("utf-8", errors="replace"))
        data = data[newline + 1 :]
        pending = b""
        pending_truncated = False

    buffer = pending + data
    while True:
        newline = buffer.find(b"\n")
        if newline < 0:
            break
        raw_line = buffer[: newline + 1]
        buffer = buffer[newline + 1 :]
        if len(raw_line) > _MAX_PENDING_LINE_BYTES:
            keep = raw_line[:_MAX_PENDING_LINE_BYTES].rstrip(b"\r\n")
            dropped_bytes += max(0, len(raw_line) - len(keep) - 1)
            raw_line = keep + b" [TRUNCATED]\n"
        lines.append(raw_line.decode("utf-8", errors="replace"))

    if len(buffer) > _MAX_PENDING_LINE_BYTES:
        dropped_bytes += len(buffer) - _MAX_PENDING_LINE_BYTES
        return lines, buffer[:_MAX_PENDING_LINE_BYTES], True, dropped_bytes
    return lines, buffer, False, dropped_bytes


@dataclass
class RealtimeState:
    source: str
    window_size: int = 500
    alert_ttl_seconds: int = 300
    watch_profile: str = "all"
    max_window_bytes: int = 5_000_000
    max_line_bytes: int = 1_000_000
    started_at: float = field(default_factory=time.monotonic)
    total_lines: int = 0
    total_bytes: int = 0
    last_activity_at: float | None = None
    truncated_lines: int = 0
    dropped_window_lines: int = 0
    trend_tracker: TrendTracker = field(default_factory=TrendTracker)
    _lines: deque[str] = field(default_factory=deque)
    _window_bytes: int = 0
    _recent_findings: deque[Finding] = field(default_factory=lambda: deque(maxlen=12))
    _seen_fingerprints: dict[tuple[str, str, str], float] = field(default_factory=dict)
    _events_cache: list[Event] = field(default_factory=list)
    _findings_cache: list[Finding] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.window_size < 20:
            raise ValueError("window_size must be at least 20")
        if self.max_window_bytes < 1 or self.max_line_bytes < 1:
            raise ValueError("live byte limits must be positive")
        get_profile(self.watch_profile)
        original = list(self._lines)
        self._lines = deque()
        self._window_bytes = 0
        for line in original:
            self._append_bounded(line)

    @staticmethod
    def _finding_key(finding: Finding) -> tuple[str, str, str]:
        return (finding.severity, finding.category, finding.title)

    def _normalize_line(self, line: str) -> tuple[str, int]:
        encoded = line.encode("utf-8", errors="replace")
        original_bytes = len(encoded)
        if original_bytes <= self.max_line_bytes:
            return line, original_bytes
        self.truncated_lines += 1
        clipped = encoded[: self.max_line_bytes].decode("utf-8", errors="replace")
        return clipped + " [TRUNCATED]\n", original_bytes

    def _append_bounded(self, line: str) -> str:
        normalized, original_bytes = self._normalize_line(line)
        retained_bytes = len(normalized.encode("utf-8", errors="replace"))
        self._lines.append(normalized)
        self._window_bytes += retained_bytes
        self.total_bytes += original_bytes
        while len(self._lines) > self.window_size or self._window_bytes > self.max_window_bytes:
            dropped = self._lines.popleft()
            self._window_bytes -= len(dropped.encode("utf-8", errors="replace"))
            self.dropped_window_lines += 1
        return normalized

    def ingest(self, lines: list[str], now: float | None = None) -> int:
        if not lines:
            return 0
        stamp = time.monotonic() if now is None else now
        self.last_activity_at = stamp
        normalized: list[str] = []
        for line in lines:
            normalized.append(self._append_bounded(line))
            self.total_lines += 1
        self.trend_tracker.ingest(normalized, stamp)
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
    def rolling_bytes(self) -> int:
        return self._window_bytes

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


def _summary_table(rows: list[tuple[str, str, str]]) -> Table:
    table = Table(
        title="Live summary",
        title_style=f"bold {ACCENT}",
        expand=True,
        border_style=ACCENT_SOFT,
    )
    table.add_column("Metric", min_width=14, ratio=2)
    table.add_column("Value", min_width=10, ratio=1, justify="right", style=ACCENT)
    table.add_column("Context", min_width=18, ratio=4, overflow="fold")
    for metric, value, context in rows:
        table.add_row(metric, value, context)
    return table


def _telemetry_table(sections: list[tuple[str, Counter[str]]], limit: int = 6) -> Table:
    table = Table(
        title="Profile telemetry",
        title_style=f"bold {ACCENT}",
        expand=True,
        border_style=ACCENT_SOFT,
    )
    table.add_column("Dimension", min_width=12, ratio=2)
    table.add_column("Name", min_width=16, ratio=4, overflow="fold")
    table.add_column("Count", min_width=6, max_width=8, justify="right", style=ACCENT)
    for dimension, values in sections:
        if values:
            for name, count in values.most_common(limit):
                table.add_row(dimension, str(name), str(count))
                dimension = ""
        else:
            table.add_row(dimension, Text("None", style=MUTED), "0")
    return table


def _recent_table(findings: list[Finding], profile: WatchProfile) -> Table:
    table = Table(
        title=f"Recent findings - {profile.label}",
        title_style=f"bold {ACCENT}",
        expand=True,
        show_lines=True,
        border_style=ACCENT_SOFT,
    )
    table.add_column("Severity", min_width=8, max_width=10, no_wrap=True)
    table.add_column("Category", min_width=10, ratio=2, overflow="fold")
    table.add_column("Finding", min_width=16, ratio=3, overflow="fold")
    table.add_column("Evidence", min_width=20, ratio=5, overflow="fold")
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
        subtitle=f"{profile.description} | Ctrl+C to stop",
        subtitle_align="right",
    )

    risk = _risk(severities)
    summary = _summary_table(
        [
            ("Lines received", f"{state.total_lines:,}", f"window {state.rolling_count:,}/{state.window_size:,}"),
            ("Average rate", f"{state.lines_per_second:.1f}/s", activity),
            ("Rate spikes", str(focused_spikes), f"{trend.window_seconds}s rolling baseline"),
            ("Profile findings", str(len(findings)), f"{critical} critical | {high} high | {medium} medium"),
            ("Incidents", str(len(incidents)), "correlated findings"),
            ("Anomalies", str(len(anomalies)), "event-level anomaly score"),
            ("Risk", risk, "current profile-focused risk state"),
        ]
    )
    telemetry = _telemetry_table(
        [
            ("Categories", categories),
            ("Log levels", levels),
            ("Services", services),
        ]
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
        f"Rolling analysis retains {state.rolling_bytes:,}/{state.max_window_bytes:,} bytes; "
        f"{state.truncated_lines} oversized lines truncated and {state.dropped_window_lines} old lines evicted. "
        f"The {profile.label} profile changes terminal emphasis only; all input remains locally analyzed and no remediation is performed.",
        style="white",
    )
    status = Panel(status_text, title="Live status", title_align="left", border_style=status_style)
    return Group(
        header,
        summary,
        telemetry,
        render_trends(trend, profile.trend_metrics),
        _recent_table(list(state.recent_findings), profile),
        status,
    )


def read_new_lines_cursor(path: Path, cursor: FileCursor) -> tuple[list[str], FileCursor]:
    """Read bounded appended bytes, retaining partial lines and detecting source resets/loss."""
    try:
        identity = _file_identity(path)
        size = path.stat().st_size
    except FileNotFoundError:
        return [], FileCursor(
            cursor.offset,
            cursor.identity,
            cursor.prefix_digest,
            cursor.pending,
            cursor.pending_truncated,
            cursor.dropped_bytes,
            False,
            "source_missing",
        )

    offset = cursor.offset
    pending = cursor.pending
    pending_truncated = cursor.pending_truncated
    reset_reason: str | None = None
    current_prefix = _prefix_digest(path, min(cursor.offset, size))
    replaced = identity != cursor.identity or (cursor.prefix_digest and current_prefix != cursor.prefix_digest)
    if not cursor.source_available:
        offset = 0
        pending = b""
        pending_truncated = False
        reset_reason = "source_recovered"
    elif replaced:
        offset = 0
        pending = b""
        pending_truncated = False
        reset_reason = "source_replaced"
    elif size < offset:
        offset = 0
        pending = b""
        pending_truncated = False
        reset_reason = "source_truncated"

    with path.open("rb") as handle:
        handle.seek(offset, os.SEEK_SET)
        data = handle.read(_MAX_READ_BYTES)
        new_offset = handle.tell()

    lines, pending, pending_truncated, dropped_bytes = _bounded_complete_lines(
        data,
        pending,
        pending_truncated,
        cursor.dropped_bytes,
    )
    new_prefix = _prefix_digest(path, new_offset)
    return lines, FileCursor(
        new_offset,
        identity,
        new_prefix,
        pending,
        pending_truncated,
        dropped_bytes,
        True,
        reset_reason,
    )


def read_new_lines(path: Path, offset: int) -> tuple[list[str], int]:
    """Backward-compatible appended-line reader; incomplete trailing data is retried next call."""
    cursor = FileCursor(offset, _file_identity(path), _prefix_digest(path, offset))
    lines, cursor = read_new_lines_cursor(path, cursor)
    if cursor.pending and not cursor.pending_truncated:
        return lines, cursor.offset - len(cursor.pending)
    return lines, cursor.offset
