from __future__ import annotations

import re
import shutil
from collections import Counter

from rich import box
from rich.console import Group, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .anomaly import score_events
from .incidents import correlate
from .terminal_charts import donut_chart, horizontal_bar, radar_chart, stacked_composition, unicode_charts_supported, vertical_histogram, wave_chart
from .theme import (
    ACCENT,
    ACCENT_BRIGHT,
    CYAN,
    DIM,
    HIGH,
    INCIDENT,
    LIME,
    MAGENTA,
    MUTED,
    NEUTRAL,
    ORANGE,
    SUCCESS,
    VIOLET,
    WARNING,
    severity_style,
    severity_text,
)

_NARROW, _WIDE, _MAX_WIDTH = 72, 104, 144
_TIME = re.compile(r"^(?:\d{4}-\d{2}-\d{2}[T ](?P<iso>\d{2}:\d{2})|[A-Z][a-z]{2}\s+\d{1,2}\s+(?P<sys>\d{2}:\d{2}))")
_PALETTE = (ACCENT_BRIGHT, CYAN, VIOLET, SUCCESS, WARNING, HIGH)


def _risk(counts: Counter[str]) -> str:
    return "CRITICAL" if counts.get("CRITICAL") else "HIGH" if counts.get("HIGH") else "REVIEW" if counts.get("MEDIUM") else "CLEAR"


def _frame_width() -> int:
    return min(max(1, shutil.get_terminal_size((80, 24)).columns - 2), _MAX_WIDTH)


def _panel(body: RenderableType, title: str, tone: str = ACCENT, *, padding=(0, 1)) -> Panel:
    return Panel(body, title=Text(f" {title} ", style=f"bold {tone}"), title_align="left", box=box.ASCII, border_style=tone, padding=padding)


def _header(title: str, source: str, profile: str, risk: str, subtitle: str) -> Panel:
    grid = Table.grid(expand=True, padding=(0, 1))
    grid.add_column(ratio=1, overflow="fold")
    grid.add_column(no_wrap=True, justify="right")
    brand = Text("AEGISLOG", style=f"bold {NEUTRAL}")
    brand.append(f"  //  {title}", style=f"bold {ACCENT_BRIGHT}")
    posture = Text("POSTURE  ", style=MUTED)
    posture.append(risk, style=f"bold {HIGH if risk in {'HIGH', 'CRITICAL'} else WARNING if risk == 'REVIEW' else SUCCESS}")
    grid.add_row(brand, posture)
    source_line = Text("SOURCE  ", style=MUTED)
    source_line.append(source, style=CYAN)
    profile_line = Text("PROFILE  ", style=MUTED)
    profile_line.append(profile.upper(), style=f"bold {VIOLET}")
    grid.add_row(source_line, profile_line)
    grid.add_row(Text(subtitle, style=MUTED), Text("HR-PRESENTS", style=f"bold {ACCENT}"))
    return Panel(grid, box=box.ASCII, border_style=ACCENT, padding=(0, 1), width=_frame_width())


def _metric(label: str, value: str, context: str, tone: str) -> Text:
    cell = Text(justify="center")
    cell.append(label, style=MUTED)
    cell.append("\n")
    cell.append(value, style=f"bold {tone}")
    cell.append(f"  {context}", style=MUTED)
    return cell


def _metric_strip(metrics: list[tuple[str, str, str, str]], compact: bool) -> Panel:
    table = Table.grid(expand=True, padding=(0, 1))
    columns = 2 if compact else len(metrics)
    for _ in range(columns):
        table.add_column(ratio=1)
    if compact:
        for index in range(0, len(metrics), 2):
            cells = [_metric(*item) for item in metrics[index : index + 2]]
            while len(cells) < 2:
                cells.append(Text(""))
            table.add_row(*cells)
    else:
        table.add_row(*(_metric(*item) for item in metrics))
    return _panel(table, "LIVE SECURITY METRICS // TELEMETRY TICKER", CYAN)


def _bar(value: float, maximum: float, width: int = 16, tone: str = ACCENT) -> Text:
    return horizontal_bar(value, maximum, width=width, tone=tone)


def _distribution(title: str, values: Counter[str], *, semantic: bool = False) -> Panel:
    items = values.most_common(6)
    if not items:
        return _panel(Text("No matching activity in the current window.", style=MUTED), title)
    maximum, total = max(count for _, count in items), max(1, sum(values.values()))
    table = Table.grid(expand=True, padding=(0, 1))
    table.add_column(ratio=1, overflow="ellipsis")
    table.add_column(width=16)
    table.add_column(width=9, justify="right")
    for index, (label, count) in enumerate(items):
        tone = severity_style(str(label)) if semantic else _PALETTE[index % len(_PALETTE)]
        table.add_row(Text(str(label).upper(), style=tone), _bar(count, maximum, tone=tone), Text(f"{count}  {count / total:>4.0%}", style=tone))
    composition = {str(label): count for label, count in items}
    visual = donut_chart(composition) if semantic else stacked_composition(composition, width=34)
    return _panel(Group(visual, Text(""), table), title + (" // DONUT" if semantic else " // COMPOSITION"), MAGENTA if semantic else LIME)


def _event_cadence(lines: list[str]) -> Panel:
    buckets: Counter[str] = Counter()
    for line in lines:
        match = _TIME.match(line.strip())
        if match:
            buckets[match.group("iso") or match.group("sys")] += 1
    if len(buckets) >= 2:
        items, note = list(buckets.items())[-10:], "timestamp buckets"
    else:
        size = max(1, (len(lines) + 7) // 8)
        items = [(f"{start + 1}-{min(len(lines), start + size)}", min(size, len(lines) - start)) for start in range(0, len(lines), size)][:8]
        note = "event-position buckets"
    if not items:
        return _panel(Text("Waiting for events.", style=MUTED), "EVENT CADENCE")
    return _panel(Group(vertical_histogram(items, height=7), Text(note, style=MUTED)), "EVENT TREND // VOLUME HISTOGRAM", CYAN)


def _activity_wave(lines: list[str]) -> Panel:
    weights: list[float] = []
    for line in lines:
        lowered = line.lower()
        weight = 5.0 if "critical" in lowered else 4.0 if "error" in lowered or "failed" in lowered else 2.5 if "warn" in lowered or "block" in lowered else 1.0
        weights.append(weight)
    if not weights:
        weights = [0.0]
    bucket_size = max(1, (len(weights) + 11) // 12)
    energy = [sum(weights[index : index + bucket_size]) for index in range(0, len(weights), bucket_size)][:12]
    return _panel(wave_chart(energy, width=48, height=7, tone=MAGENTA, fill=False), "THREAT WAVE // SEVERITY ENERGY", MAGENTA)


def _threat_radar(lines: list[str], findings, incidents, anomalies, services: Counter[str]) -> Panel:
    severity_weights = {"CRITICAL": 5, "HIGH": 4, "MEDIUM": 3, "LOW": 2, "INFO": 1}
    alert_pressure = sum(severity_weights.get(item.severity.upper(), 1) for item in findings)
    dimensions = {
        "alert": alert_pressure,
        "auth": sum("auth" in line.lower() or "password" in line.lower() for line in lines),
        "errors": sum("error" in line.lower() or "failed" in line.lower() for line in lines),
        "incidents": len(incidents),
        "anomalies": len(anomalies),
        "services": len(services),
    }
    return _panel(radar_chart(dimensions, width=31, height=10, tone=ORANGE), "THREAT RADAR // SIGNAL PROFILE", ORANGE)


def _flow_panel(source_count: int, event_count: int, finding_count: int, incident_count: int) -> Panel:
    arrow = "━━▶" if unicode_charts_supported() else "==>"
    grid = Table.grid(expand=True, padding=(0, 1))
    for ratio in (2, 1, 2, 1, 2, 1, 2):
        grid.add_column(ratio=ratio, justify="center")
    grid.add_row(
        Text(f"SOURCES\n{source_count}", style=f"bold {CYAN}", justify="center"),
        Text(arrow, style=LIME),
        Text(f"EVENTS\n{event_count:,}", style=f"bold {LIME}", justify="center"),
        Text(arrow, style=ORANGE),
        Text(f"FINDINGS\n{finding_count}", style=f"bold {ORANGE}", justify="center"),
        Text(arrow, style=MAGENTA),
        Text(f"INCIDENTS\n{incident_count}", style=f"bold {MAGENTA}", justify="center"),
    )
    return _panel(grid, "DETECTION FLOW // CORRELATION DIAGRAM", LIME)


def _compare_bar(current: float, baseline: float, width: int = 14) -> Text:
    maximum = max(current, baseline, 1.0)
    current_width = round(current / maximum * width)
    baseline_position = min(width - 1, max(0, round(baseline / maximum * (width - 1))))
    plot = ["."] * width
    for index in range(current_width):
        plot[index] = "#"
    plot[baseline_position] = "|"
    text = Text()
    for char in plot:
        text.append(char, style=VIOLET if char == "|" else CYAN if char == "#" else DIM)
    return text


def _trend_matrix(snapshot, metric_names: tuple[str, ...]) -> Panel:
    allowed = set(metric_names)
    metrics = [item for item in snapshot.metrics if item.name in allowed]
    table = Table.grid(expand=True, padding=(0, 1))
    table.add_column("SIGNAL", ratio=1)
    table.add_column("CURRENT # / BASE |", width=16)
    table.add_column("RATE", width=9, justify="right")
    table.add_column("BASE", width=8, justify="right")
    table.add_column("DELTA", width=7, justify="right")
    table.add_column("STATE", width=9)
    for item in metrics:
        tone = HIGH if item.state == "SPIKE" else WARNING if item.state == "ELEVATED" else SUCCESS
        ratio = f"{item.deviation_ratio:.1f}x" if item.deviation_ratio < 100 else ">99x"
        table.add_row(
            item.name,
            _compare_bar(item.current_per_minute, item.baseline_per_minute),
            f"{item.current_per_minute:.1f}/m",
            f"{item.baseline_per_minute:.1f}/m",
            ratio,
            Text(item.state, style=f"bold {tone}"),
        )
    if not metrics:
        table.add_row("No profile signals", _compare_bar(0, 0), "0.0/m", "0.0/m", "1.0x", Text("NORMAL", style=SUCCESS))
    return _panel(table, f"SIGNAL TREND // RATE & BASELINE INTELLIGENCE // {snapshot.window_seconds}s", VIOLET)


def _finding_panel(findings, profile_label: str) -> Panel:
    table = Table(expand=True, box=None, padding=(0, 1))
    table.add_column("SEV", width=9)
    table.add_column("CATEGORY", width=15, overflow="ellipsis")
    table.add_column("DETECTION / EVIDENCE", ratio=1, overflow="fold")
    for item in findings[:6]:
        detail = Text(item.title, style=f"bold {NEUTRAL}")
        detail.append("\n" + item.evidence, style=MUTED)
        table.add_row(severity_text(item.severity), Text(item.category.upper(), style=CYAN), detail)
    if not findings:
        table.add_row("-", "-", Text(f"No {profile_label.lower()} findings in this window.", style=SUCCESS))
    return _panel(table, "INVESTIGATION QUEUE // LIVE EVIDENCE", WARNING, padding=(0, 0))


def _two(left: RenderableType, right: RenderableType) -> Table:
    table = Table.grid(expand=True, padding=(0, 1))
    table.add_column(ratio=1)
    table.add_column(ratio=1)
    table.add_row(left, right)
    return table


def render_realtime_command_center(state) -> RenderableType:
    width, profile, events, findings = _frame_width(), state.profile, state.focused_events, state.focused_findings
    compact = width < _NARROW
    severities = Counter(item.severity for item in findings)
    services = Counter(event.service or "unknown" for event in events if event.message)
    incidents = correlate(findings)
    anomalies = score_events(events)
    trend = state.trends
    spikes = sum(item.state == "SPIKE" for item in trend.metrics if item.name in set(profile.trend_metrics))
    age = state.activity_age
    activity = "waiting" if age is None else "receiving" if age < 2 else f"{age:.0f}s ago"
    metrics = [
        ("EVENTS", f"{state.total_lines:,}", f"window {state.rolling_count:,}", ACCENT_BRIGHT),
        ("RATE", f"{state.lines_per_second:.1f}/s", activity, CYAN),
        ("FINDINGS", str(len(findings)), "profile", WARNING),
        ("INCIDENTS", str(len(incidents)), "correlated", INCIDENT),
        ("ANOMALIES", str(len(anomalies)), "scored", VIOLET),
        ("SPIKES", str(spikes), f"{trend.window_seconds}s", HIGH),
    ]
    sections: list[RenderableType] = [
        _header("LIVE MONITOR", state.source, profile.label, _risk(severities), "LOCAL / READ-ONLY / CTRL+C STOPS MONITORING"),
        _metric_strip(metrics, compact),
    ]
    severity_panel, service_panel = _distribution("SEVERITY DISTRIBUTION", severities, semantic=True), _distribution("SERVICE ACTIVITY", services)
    sections.extend(
        (
            _two(_event_cadence(state.lines), severity_panel),
            service_panel,
            _activity_wave(state.lines),
            _threat_radar(state.lines, findings, incidents, anomalies, services),
            _trend_matrix(trend, profile.trend_metrics),
        )
        if width >= _WIDE
        else (
            _event_cadence(state.lines),
            severity_panel,
            service_panel,
            _activity_wave(state.lines),
            _threat_radar(state.lines, findings, incidents, anomalies, services),
            _trend_matrix(trend, profile.trend_metrics),
        )
    )
    sections.extend(
        (
            _flow_panel(1, state.total_lines, len(findings), len(incidents)),
            _finding_panel(list(state.recent_findings), profile.label),
            _panel(
                Text(
                    f"ACTIVE  |  {state.total_bytes:,} bytes  |  {state.truncated_lines} truncated  |  {state.dropped_window_lines} evicted  |  no remediation",
                    style=MUTED,
                ),
                "SENSOR HEALTH",
                SUCCESS,
            ),
        )
    )
    return Group(*sections)


def _source_activity(state) -> Panel:
    rows = [(path.name, state.source_counts.get(path.name, 0), path.exists() and path.is_file()) for path in state.sources]
    maximum = max([count for _, count, _ in rows] or [1])
    table = Table.grid(expand=True, padding=(0, 1))
    table.add_column("SOURCE", ratio=1, overflow="ellipsis")
    table.add_column("LOAD", width=16)
    table.add_column("STATUS", width=9)
    table.add_column("EVENTS", width=7, justify="right")
    for index, (name, count, available) in enumerate(rows):
        tone = _PALETTE[index % len(_PALETTE)]
        table.add_row(
            Text(name, style=tone),
            _bar(count, maximum, tone=tone),
            Text("READY" if available else "MISSING", style=SUCCESS if available else WARNING),
            str(count),
        )
    return _panel(table, "SOURCE ACTIVITY // INGESTION PULSE", CYAN)


def render_multisource_command_center(state) -> RenderableType:
    width, profile, findings = _frame_width(), state.profile, state.focused_findings
    compact = width < _NARROW
    severities = Counter(item.severity for item in findings)
    categories = Counter(item.category for item in findings)
    incidents = correlate(findings)
    anomalies = score_events(state.events)
    services = Counter(event.service or "unknown" for event in state.events if event.message)
    trend = state.trends
    spikes = sum(item.state == "SPIKE" for item in trend.metrics if item.name in set(profile.trend_metrics))
    metrics = [
        ("SOURCES", str(len(state.sources)), f"window {state.rolling_count:,}", ACCENT_BRIGHT),
        ("EVENTS", f"{state.total_lines:,}", "all sources", CYAN),
        ("LIVE RATE", f"{state.recent_eps:.2f}/s", "recent", CYAN),
        ("FINDINGS", str(len(findings)), "profile", WARNING),
        ("INCIDENTS", str(len(incidents)), "correlated", INCIDENT),
        ("SPIKES", str(spikes), f"{trend.window_seconds}s", HIGH),
    ]
    sections: list[RenderableType] = [
        _header(
            "MULTI-SOURCE", ", ".join(path.name for path in state.sources), profile.label, _risk(severities), "LOCAL / READ-ONLY / CROSS-SOURCE CORRELATION"
        ),
        _metric_strip(metrics, compact),
        _source_activity(state),
    ]
    severity_panel = _distribution("SEVERITY DISTRIBUTION", severities, semantic=True)
    category_panel = _distribution("FINDINGS BY CATEGORY", categories)
    sections.extend(
        (
            _two(_event_cadence(state.raw_lines), severity_panel),
            category_panel,
            _activity_wave(state.raw_lines),
            _threat_radar(state.raw_lines, findings, incidents, anomalies, services),
        )
        if width >= _WIDE
        else (
            _event_cadence(state.raw_lines),
            severity_panel,
            category_panel,
            _activity_wave(state.raw_lines),
            _threat_radar(state.raw_lines, findings, incidents, anomalies, services),
        )
    )
    sections.extend(
        (
            _trend_matrix(trend, profile.trend_metrics),
            _flow_panel(len(state.sources), state.total_lines, len(findings), len(incidents)),
            _finding_panel(list(state.alerts), profile.label),
            _panel(Text(f"ACTIVE  |  {state.total_bytes:,} bytes  |  {len(state.sources)} sources  |  no remediation", style=MUTED), "SOC STATUS", SUCCESS),
        )
    )
    return Group(*sections)


__all__ = ["render_realtime_command_center", "render_multisource_command_center"]
