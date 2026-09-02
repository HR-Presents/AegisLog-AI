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
from .theme import ACCENT, ACCENT_SOFT, ANOMALY, INCIDENT, INFO, MUTED, SUCCESS, WARNING, risk_style, severity_text
from .trends import TrendSnapshot, TrendTracker, render_trends
from .watch_profiles import WatchProfile, filter_events, filter_findings, get_profile


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
            raise ValueError("max_seen_fingerprints must be at least 1")
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


def _metric(title: str, value: str, subtitle: str = "", value_style: str = "bold", border_style: str = ACCENT_SOFT) -> Panel:
    body = Text(value, justify="center", style=value_style)
    if subtitle:
        body.append(f"\n{subtitle}", style=MUTED)
    return Panel(Align.center(body), title=title, padding=(0, 1), border_style=border_style)


def _counter(title: str, values: Counter[str], limit: int = 6) -> Table:
    table = Table(title=title, expand=True, border_style=ACCENT_SOFT)
    table.add_column("Name")
    table.add_column("Count", justify="right", style=ACCENT)
    for name, count in values.most_common(limit):
        table.add_row(Text(str(name)), str(count))
    if not values:
        table.add_row(Text("None", style=MUTED), Text("0", style=MUTED))
    return table


def _alerts_table(state: MultiSourceState) -> Table:
    profile = state.profile
    table = Table(
        title=f"Live security alert feed — {profile.label}",
        expand=True,
        show_lines=True,
        border_style=INCIDENT,
    )
    table.add_column("#", justify="right", width=5, style=ACCENT)
    table.add_column("Severity", width=10)
    table.add_column("Source", width=18)
    table.add_column("Category", width=18)
    table.add_column("Alert", width=34)
    table.add_column("Evidence")
    for item in state.alerts[:10]:
        table.add_row(
            str(item.sequence),
            severity_text(item.severity),
            Text(item.source),
            Text(item.category),
            Text(item.title),
            Text(item.evidence),
        )
    if not state.alerts:
        table.add_row(
            Text("-", style=MUTED),
            Text("-", style=MUTED),
            Text("-", style=MUTED),
            Text("-", style=MUTED),
            Text(f"No {profile.label.lower()} alerts yet", style=SUCCESS),
            Text("All sources remain under local monitoring", style=MUTED),
        )
    return table


def render_multisource(state: MultiSourceState) -> RenderableType:
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

    header_text = Text(f"AEGISLOG AI  v{__version__}", style=f"bold {ACCENT}")
    header_text.append("\nMULTI-SOURCE REAL-TIME SOC", style="bold white")
    header_text.append(f"\n{sources}", style=ACCENT_SOFT)
    header_text.append(f"\nPROFILE: {profile.label.upper()}", style=INFO)
    header = Panel(
        Align.center(header_text),
        subtitle=f"{profile.description} • local/read-only • Ctrl+C to stop",
        border_style=ACCENT,
    )
    metrics = Columns(
        [
            _metric("Sources", str(len(state.sources)), f"{state.rolling_count:,}/{state.window_size:,} rolling lines", f"bold {ACCENT}"),
            _metric("Events", f"{state.total_lines:,}", value_style=f"bold {ACCENT}"),
            _metric("Live EPS", f"{state.recent_eps:.2f}/s", f"lifetime {state.lifetime_eps:.2f}/s", f"bold {INFO}"),
            _metric(
                "Rate spikes",
                str(focused_spikes),
                f"{trend.window_seconds}s profile baseline",
                f"bold {WARNING}" if focused_spikes else f"bold {SUCCESS}",
                WARNING if focused_spikes else SUCCESS,
            ),
            _metric("Profile findings", str(len(findings)), value_style=f"bold {WARNING}" if findings else f"bold {SUCCESS}"),
            _metric("Incidents", str(len(incidents)), value_style=f"bold {INCIDENT}" if incidents else f"bold {SUCCESS}", border_style=INCIDENT if incidents else SUCCESS),
            _metric("Anomalies", str(len(anomalies)), value_style=f"bold {ANOMALY}" if anomalies else f"bold {SUCCESS}", border_style=ANOMALY if anomalies else SUCCESS),
            _metric("Risk", risk, value_style=f"bold {risk_style(risk)}", border_style=risk_style(risk)),
        ],
        equal=True,
        expand=True,
    )
    overview = Columns(
        [
            _counter("Events by source", state.source_counts),
            _counter("Profile categories", categories),
            _counter("Profile log levels", levels),
            _counter("Profile services", services),
        ],
        equal=True,
        expand=True,
    )
    status_text = Text()
    status_text.append(f"{state.total_bytes:,} bytes ingested. ", style=ACCENT)
    status_text.append(f"The {profile.label} profile changes terminal emphasis only. ")
    status_text.append(
        f"Correlation remains local/read-only and rate baselines use the most recent {state.trend_seconds}s of arrivals.",
        style=MUTED,
    )
    status = Panel(status_text, title="Monitoring status", border_style=SUCCESS)
    return Group(header, metrics, overview, render_trends(trend, profile.trend_metrics), _alerts_table(state), status)
