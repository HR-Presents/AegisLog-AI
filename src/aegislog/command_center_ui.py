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
from .theme import ACCENT, ACCENT_BRIGHT, ACCENT_SOFT, CYAN, HIGH, INCIDENT, MUTED, NEUTRAL, SUCCESS, VIOLET, WARNING, severity_style, severity_text

_NARROW, _WIDE, _MAX_WIDTH = 72, 104, 144
_TIME = re.compile(r"^(?:\d{4}-\d{2}-\d{2}[T ](?P<iso>\d{2}:\d{2})|[A-Z][a-z]{2}\s+\d{1,2}\s+(?P<sys>\d{2}:\d{2}))")
_PALETTE = (ACCENT_BRIGHT, CYAN, VIOLET, SUCCESS, WARNING, HIGH)


def _risk(counts: Counter[str]) -> str:
    return "CRITICAL" if counts.get("CRITICAL") else "HIGH" if counts.get("HIGH") else "REVIEW" if counts.get("MEDIUM") else "CLEAR"


def _frame_width() -> int:
    return min(max(1, shutil.get_terminal_size((80, 24)).columns - 2), _MAX_WIDTH)


def _panel(body: RenderableType, title: str, tone: str = ACCENT, *, padding=(0, 1)) -> Panel:
    return Panel(body, title=Text(f" {title} ", style=f"bold {tone}"), title_align="left", box=box.ASCII, border_style=ACCENT_SOFT, padding=padding)


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
    filled = 0 if value <= 0 else max(1, round(value / max(maximum, 1) * width))
    result = Text("#" * min(width, filled), style=tone)
    result.append("." * max(0, width - filled), style="#45536A")
    return result


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
    return _panel(table, title, WARNING if semantic else ACCENT)


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
    maximum = max(value for _, value in items)
    height = 6
    heights = [max(1, round(value / maximum * height)) for _, value in items]
    chart = Table.grid(padding=0)
    chart.add_column(width=5, justify="right")
    chart.add_column()
    for level in range(height, 0, -1):
        scale = str(round(maximum * level / height)) if level in {height, 1} else ""
        row = Text()
        for index, item_height in enumerate(heights):
            row.append("##" if item_height >= level else "  ", style=_PALETTE[index % len(_PALETTE)])
            row.append(" ")
        chart.add_row(Text(scale, style=MUTED), row)
    axis = Text("--" * len(items), style=ACCENT_SOFT)
    labels = Text(" ".join(label[-5:] for label, _ in items), style=MUTED, no_wrap=True, overflow="ellipsis")
    values = Text(" ".join(f"{value:>2}" for _, value in items), style=NEUTRAL, no_wrap=True, overflow="ellipsis")
    return _panel(Group(chart, Text("     ").append_text(axis), labels, values, Text(note, style=MUTED)), "EVENT TREND // VOLUME OVER TIME", CYAN)


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
        text.append(char, style=VIOLET if char == "|" else CYAN if char == "#" else ACCENT_SOFT)
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
        (_two(_event_cadence(state.lines), severity_panel), service_panel, _trend_matrix(trend, profile.trend_metrics))
        if width >= _WIDE
        else (_event_cadence(state.lines), severity_panel, service_panel, _trend_matrix(trend, profile.trend_metrics))
    )
    sections.extend(
        (
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
        (_two(_event_cadence(state.raw_lines), severity_panel), category_panel)
        if width >= _WIDE
        else (_event_cadence(state.raw_lines), severity_panel, category_panel)
    )
    sections.extend(
        (
            _trend_matrix(trend, profile.trend_metrics),
            _finding_panel(list(state.alerts), profile.label),
            _panel(Text(f"ACTIVE  |  {state.total_bytes:,} bytes  |  {len(state.sources)} sources  |  no remediation", style=MUTED), "SOC STATUS", SUCCESS),
        )
    )
    return Group(*sections)


__all__ = ["render_realtime_command_center", "render_multisource_command_center"]
