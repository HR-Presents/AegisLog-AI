from __future__ import annotations

import shutil
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
from .realtime import FileCursor, initial_cursor, read_new_lines, read_new_lines_cursor
from .theme import ACCENT, ACCENT_SOFT, ANOMALY, INCIDENT, INFO, MUTED, SUCCESS, WARNING, risk_style, severity_text
from .trends import TrendSnapshot, TrendTracker, render_trends
from .watch_profiles import WatchProfile, filter_events, filter_findings, get_profile

_NARROW_BREAKPOINT = 72


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
    watch_profile: str = "all"
    max_arrival_buckets: int = 4096
    max_seen_fingerprints: int = 4096
    started_at: float = field(default_factory=time.monotonic)
    total_lines: int = 0
    total_bytes: int = 0
    trend_tracker: TrendTracker = field(default_factory=TrendTracker)
    _lines: deque[tuple[str, str]] = field(default_factory=deque)
    _arrivals: deque[tuple[float, int]] = field(default_factory=deque)
    _alerts: deque[LiveAlert] = field(default_factory=lambda: deque(maxlen=15))
    _seen: dict[tuple[str, str, str, str], float] = field(default_factory=dict)
    _sequence: int = 0
    _events_cache: list[Event] = field(default_factory=list)
    _findings_cache: list[Finding] = field(default_factory=list)
    source_counts: Counter[str] = field(default_factory=Counter)

    def __post_init__(self) -> None:
        if self.window_size < 20:
            raise ValueError("window_size must be at least 20")
        if self.max_arrival_buckets < 2:
            raise ValueError("max_arrival_buckets must be at least 2")
        if self.max_seen_fingerprints < 1:
            raise ValueError("max_seen_fingerprints must be positive")
        get_profile(self.watch_profile)
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
            self.total_lines += 1
            self.total_bytes += len(line.encode("utf-8", errors="replace"))
            self.source_counts[label] += 1
        self._record_arrivals(stamp, len(lines))
        self.trend_tracker.ingest(lines, stamp)
        self._trim_arrivals(stamp)
        self._refresh_snapshot()
        self._refresh_alerts(stamp)
        return len(lines)

    def _record_arrivals(self, stamp: float, count: int) -> None:
        if self._arrivals and self._arrivals[-1][0] == stamp:
            previous_stamp, previous_count = self._arrivals.pop()
            self._arrivals.append((previous_stamp, previous_count + count))
        else:
            self._arrivals.append((stamp, count))
        while len(self._arrivals) > self.max_arrival_buckets:
            first_stamp, first_count = self._arrivals.popleft()
            second_stamp, second_count = self._arrivals.popleft()
            self._arrivals.appendleft((second_stamp, first_count + second_count))

    def _trim_arrivals(self, now: float) -> None:
        cutoff = now - self.trend_seconds
        while self._arrivals and self._arrivals[0][0] < cutoff:
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

    def _bound_seen(self) -> None:
        overflow = len(self._seen) - self.max_seen_fingerprints
        if overflow <= 0:
            return
        oldest = sorted(self._seen.items(), key=lambda item: item[1])[:overflow]
        for fp, _ in oldest:
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
        for finding in self.focused_findings:
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
        self._bound_seen()

    @property
    def profile(self) -> WatchProfile:
        return get_profile(self.watch_profile)

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
    def focused_findings(self) -> list[Finding]:
        return filter_findings(self.profile, self.findings)

    @property
    def events(self) -> list[Event]:
        return list(self._events_cache)

    @property
    def focused_events(self) -> list[Event]:
        return filter_events(self.profile, self.events)

    @property
    def alerts(self) -> tuple[LiveAlert, ...]:
        return tuple(self._alerts)

    @property
    def trends(self) -> TrendSnapshot:
        return self.trend_tracker.snapshot()

    @property
    def recent_eps(self) -> float:
        self._trim_arrivals(time.monotonic())
        return sum(count for _, count in self._arrivals) / max(float(self.trend_seconds), 1.0)

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
    return {path: 0 if from_start else path.stat().st_size for path in paths}


def _risk(counts: Counter[str]) -> str:
    if counts.get("CRITICAL"):
        return "CRITICAL"
    if counts.get("HIGH"):
        return "HIGH"
    if counts.get("MEDIUM"):
        return "REVIEW"
    return "CLEAR"


def _summary_table(rows: list[tuple[str, str, str, str]], screen_width: int) -> Table:
    compact = screen_width < _NARROW_BREAKPOINT
    table = Table(title="SOC summary", expand=True, border_style=ACCENT_SOFT, show_header=True)
    if compact:
        table.add_column("Metric", min_width=8, ratio=2, style=ACCENT, overflow="fold")
        table.add_column("Value / Context", min_width=12, ratio=4, overflow="fold")
        for label, value, context, style in rows:
            body = Text(value, style=style)
            body.append("\n")
            body.append(context, style=MUTED)
            table.add_row(Text(label), body)
    else:
        table.add_column("Metric", min_width=15, ratio=2, style=ACCENT)
        table.add_column("Value", min_width=8, ratio=1, justify="right")
        table.add_column("Context", min_width=18, ratio=4, style=MUTED, overflow="fold")
        for label, value, context, style in rows:
            table.add_row(Text(label), Text(value, style=style), Text(context))
    return table


def _telemetry_table(sections: tuple[tuple[str, Counter[str]], ...], screen_width: int, limit: int = 6) -> Table:
    compact = screen_width < _NARROW_BREAKPOINT
    table = Table(title="Profile telemetry", expand=True, border_style=ACCENT_SOFT, show_lines=False)
    if compact:
        table.add_column("Telemetry", min_width=10, ratio=1, overflow="fold")
        table.add_column("Count", min_width=5, max_width=7, justify="right", style=ACCENT)
        for label, values in sections:
            items = values.most_common(limit)
            if not items:
                table.add_row(Text(f"{label}: None", style=MUTED), "0")
                continue
            for name, count in items:
                table.add_row(Text(f"{label}: {name}"), str(count))
    else:
        table.add_column("Dimension", min_width=14, ratio=2, style=ACCENT)
        table.add_column("Name", min_width=12, ratio=4, overflow="fold")
        table.add_column("Count", min_width=5, ratio=1, justify="right", style=ACCENT)
        for label, values in sections:
            items = values.most_common(limit)
            if not items:
                table.add_row(label, Text("None", style=MUTED), Text("0", style=MUTED))
                continue
            for index, (name, count) in enumerate(items):
                table.add_row(label if index == 0 else "", Text(str(name)), str(count))
    return table


def _alerts_table(state: MultiSourceState, screen_width: int) -> Table:
    profile = state.profile
    compact = screen_width < _NARROW_BREAKPOINT
    table = Table(title=f"Live security alert feed - {profile.label}", expand=True, show_lines=True, border_style=INCIDENT)
    if compact:
        table.add_column("Alert", min_width=10, ratio=1, overflow="fold")
        for item in state.alerts[:10]:
            body = Text()
            body.append(f"#{item.sequence} ", style=ACCENT)
            body.append_text(severity_text(item.severity))
            body.append(f"  {item.source} / {item.category}\n", style=MUTED)
            body.append(item.title, style="bold white")
            body.append("\n")
            body.append(item.evidence, style=MUTED)
            table.add_row(body)
        if not state.alerts:
            table.add_row(Text(f"No {profile.label.lower()} alerts yet. All sources remain under local monitoring.", style=SUCCESS))
    else:
        table.add_column("#", justify="right", min_width=3, max_width=5, style=ACCENT, no_wrap=True)
        table.add_column("Severity", min_width=8, max_width=10, no_wrap=True)
        table.add_column("Source", min_width=10, ratio=2, overflow="fold")
        table.add_column("Category", min_width=10, ratio=2, overflow="fold")
        table.add_column("Alert", min_width=16, ratio=3, overflow="fold")
        table.add_column("Evidence", min_width=20, ratio=5, overflow="fold")
        for item in state.alerts[:10]:
            table.add_row(str(item.sequence), severity_text(item.severity), Text(item.source), Text(item.category), Text(item.title), Text(item.evidence))
        if not state.alerts:
            table.add_row("-", "-", "-", "-", Text(f"No {profile.label.lower()} alerts yet", style=SUCCESS), Text("All sources remain under local monitoring", style=MUTED))
    return table


def render_multisource(state: MultiSourceState) -> RenderableType:
    screen_width = shutil.get_terminal_size((80, 24)).columns
    profile = state.profile
    events = state.focused_events
    findings = state.focused_findings
    trend = state.trends
    severity = Counter(item.severity for item in findings)
    categories = Counter(item.category for item in findings)
    levels = Counter((event.level or "unknown").upper() for event in events if event.message)
    services = Counter(event.service or "unknown" for event in events if event.message)
    incidents = correlate(findings)
    anomalies = score_events(events)
    sources = ", ".join(path.name for path in state.sources)
    allowed_metrics = set(profile.trend_metrics)
    focused_spikes = sum(1 for item in trend.metrics if item.name in allowed_metrics and item.state == "SPIKE")
    risk = _risk(severity)

    header_text = Text(f"AEGISLOG  v{__version__}", style=f"bold {ACCENT}")
    header_text.append("\nMULTI-SOURCE REAL-TIME SOC", style="bold white")
    header_text.append(f"\n{sources}", style=ACCENT_SOFT)
    header_text.append(f"\nPROFILE: {profile.label.upper()}", style=INFO)
    subtitle = "Ctrl+C to stop" if screen_width < _NARROW_BREAKPOINT else f"{profile.description} | local/read-only | Ctrl+C to stop"
    header = Panel(Align.center(header_text), subtitle=subtitle, border_style=ACCENT)

    summary = _summary_table(
        [
            ("Sources", str(len(state.sources)), f"{state.rolling_count:,}/{state.window_size:,} rolling lines", f"bold {ACCENT}"),
            ("Events", f"{state.total_lines:,}", "events ingested", f"bold {ACCENT}"),
            ("Live EPS", f"{state.recent_eps:.2f}/s", f"lifetime {state.lifetime_eps:.2f}/s", f"bold {INFO}"),
            ("Rate spikes", str(focused_spikes), f"{trend.window_seconds}s profile baseline", f"bold {WARNING}" if focused_spikes else f"bold {SUCCESS}"),
            ("Profile findings", str(len(findings)), "focused detections", f"bold {WARNING}" if findings else f"bold {SUCCESS}"),
            ("Incidents", str(len(incidents)), "correlated findings", f"bold {INCIDENT}" if incidents else f"bold {SUCCESS}"),
            ("Anomalies", str(len(anomalies)), "behavioral deviations", f"bold {ANOMALY}" if anomalies else f"bold {SUCCESS}"),
            ("Risk", risk, "current local assessment", f"bold {risk_style(risk)}"),
        ],
        screen_width,
    )
    telemetry = _telemetry_table((("Events by source", state.source_counts), ("Categories", categories), ("Log levels", levels), ("Services", services)), screen_width)
    status_text = Text()
    status_text.append(f"{state.total_bytes:,} bytes ingested. ", style=ACCENT)
    status_text.append(f"The {profile.label} profile changes terminal emphasis only. ")
    status_text.append(f"Correlation remains local/read-only and rate baselines use the most recent {state.trend_seconds}s of arrivals.", style=MUTED)
    status = Panel(status_text, title="Monitoring status", border_style=SUCCESS)
    return Group(header, summary, telemetry, render_trends(trend, profile.trend_metrics), _alerts_table(state, screen_width), status)