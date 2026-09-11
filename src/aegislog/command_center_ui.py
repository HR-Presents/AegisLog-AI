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
from .theme import (
    ACCENT,
    ACCENT_SOFT,
    HIGH,
    INCIDENT,
    MUTED,
    NEUTRAL,
    SECONDARY,
    SKY,
    SUCCESS,
    WARNING,
    severity_style,
    severity_text,
)

_NARROW = 72
_WIDE = 96
_MAX_WIDTH = 118
_ANALYTIC_PALETTE = (ACCENT, SECONDARY, SKY, SUCCESS, WARNING, HIGH)
_SERVICE_PALETTE = (SKY, ACCENT, SUCCESS, SECONDARY, WARNING, HIGH)
_CATEGORY_PALETTE = (SECONDARY, HIGH, WARNING, SKY, SUCCESS, ACCENT)
_SOURCE_PALETTE = (ACCENT, SKY, SECONDARY, SUCCESS, WARNING, HIGH)
_TIMESTAMP = re.compile(
    r"^(?:\d{4}-\d{2}-\d{2}[T ](?P<iso>\d{2}:\d{2})|[A-Z][a-z]{2}\s+\d{1,2}\s+(?P<sys>\d{2}:\d{2}))"
)


def _risk(counts: Counter[str]) -> str:
    if counts.get("CRITICAL"):
        return "CRITICAL"
    if counts.get("HIGH"):
        return "HIGH"
    if counts.get("MEDIUM"):
        return "REVIEW"
    return "CLEAR"


def _frame_width() -> int:
    return min(max(1, shutil.get_terminal_size((80, 24)).columns - 4), _MAX_WIDTH)


def _panel(body: RenderableType, title: str, tone: str = ACCENT, *, padding=(0, 1)) -> Panel:
    return Panel(
        body,
        title=Text(f" {title} ", style=f"bold {tone}"),
        title_align="left",
        box=box.ASCII,
        border_style=ACCENT_SOFT,
        padding=padding,
    )


def _header(title: str, source: str, profile: str, risk: str, *, subtitle: str = "") -> Panel:
    grid = Table.grid(expand=True, padding=(0, 1))
    grid.add_column(ratio=1)
    grid.add_column(no_wrap=True)
    brand = Text("AEGISLOG", style=f"bold {ACCENT}")
    brand.append(f"  //  {title}", style=f"bold {NEUTRAL}")
    brand.append("\n")
    brand.append(subtitle or "LOCAL | READ-ONLY | DETERMINISTIC", style=MUTED)
    right = Text(justify="right")
    right.append(f"POSTURE  {risk}", style=f"bold {WARNING if risk != 'CLEAR' else SUCCESS}")
    right.append("\nPROFILE  ", style=MUTED)
    right.append(profile.upper(), style=f"bold {ACCENT}")
    grid.add_row(brand, right)
    source_line = Text("SOURCE  ", style=MUTED)
    source_line.append(source, style=SKY)
    grid.add_row(source_line, Text("HR-PRESENTS", style=f"bold {ACCENT}"))
    return Panel(grid, box=box.ASCII, border_style=ACCENT, padding=(0, 1), width=_frame_width())


def _metric_cell(label: str, value: str, context: str, style: str) -> Text:
    cell = Text(justify="center")
    cell.append(label, style=MUTED)
    cell.append("\n")
    cell.append(value, style=f"bold {style}")
    cell.append("  ")
    cell.append(context, style=MUTED)
    return cell


def _metric_strip(metrics: list[tuple[str, str, str, str]], compact: bool) -> Panel:
    table = Table.grid(expand=True, padding=(0, 1))
    columns = 2 if compact else len(metrics)
    for _ in range(columns):
        table.add_column(ratio=1)
    if compact:
        for index in range(0, len(metrics), 2):
            cells = [_metric_cell(*item) for item in metrics[index : index + 2]]
            while len(cells) < 2:
                cells.append(Text(""))
            table.add_row(*cells)
    else:
        table.add_row(*(_metric_cell(*item) for item in metrics))
    return _panel(table, "TELEMETRY PULSE // LIVE TICKER", SKY)


def _mini_bar(count: float, maximum: float, width: int = 14, *, style: str = ACCENT) -> Text:
    maximum = max(1.0, maximum)
    filled = max(1, round((count / maximum) * width)) if count > 0 else 0
    text = Text("=" * min(width, filled), style=style)
    text.append("." * max(0, width - filled), style="#45515a")
    return text


def _distribution(
    title: str,
    values: Counter[str],
    *,
    compact: bool,
    semantic: bool = False,
    palette: tuple[str, ...] | None = None,
    title_style: str = ACCENT,
) -> Panel:
    items = values.most_common(5)
    if not items:
        return _panel(Text("No matching activity in this window.", style=MUTED), title, title_style)
    maximum = max(count for _, count in items)
    total = max(1, sum(values.values()))
    colors = palette or _ANALYTIC_PALETTE
    table = Table.grid(expand=True, padding=(0, 1))
    table.add_column(ratio=1, overflow="crop")
    table.add_column(width=14)
    table.add_column(width=8, justify="right")
    for index, (label, count) in enumerate(items):
        pct = count / total * 100
        style = severity_style(str(label)) if semantic else colors[index % len(colors)]
        table.add_row(
            Text(str(label).upper(), style=style if semantic else NEUTRAL),
            _mini_bar(count, maximum, style=style),
            Text(f"{count} {pct:>3.0f}%", style=style if not semantic else MUTED),
        )
    return _panel(table, title, title_style)


def _event_flow(raw_lines: list[str], *, title: str = "EVENT FLOW") -> Panel:
    buckets: Counter[str] = Counter()
    for raw in raw_lines:
        match = _TIMESTAMP.match(raw.strip())
        if match:
            buckets[match.group("iso") or match.group("sys")] += 1
    items = list(buckets.items())[-10:]
    axis_note = "timestamp buckets"
    if len(items) < 2:
        total = len(raw_lines)
        if total:
            size = max(1, (total + 7) // 8)
            items = [
                (f"{start + 1}-{min(total, start + size)}", min(size, total - start))
                for start in range(0, total, size)
            ][:8]
            axis_note = "real event positions"
    if not items:
        return _panel(Text("Waiting for events.", style=MUTED), title, SKY)
    maximum = max(value for _, value in items)
    chart_height = 4
    heights = [max(1, round(value / maximum * chart_height)) for _, value in items]
    rows: list[Text] = []
    for level in range(chart_height, 0, -1):
        row = Text()
        for index, height in enumerate(heights):
            active = height >= level
            row.append("==" if active else "  ", style=_ANALYTIC_PALETTE[index % len(_ANALYTIC_PALETTE)] if active else MUTED)
            row.append(" ")
        rows.append(row)
    labels = Text(" ".join(label[-5:] for label, _ in items), style=MUTED, no_wrap=True, overflow="crop")
    rows.extend((labels, Text(axis_note, style=MUTED)))
    return _panel(Group(*rows), title, SKY)


def _signal_matrix(snapshot, metric_names: tuple[str, ...] | None = None) -> Panel:
    allowed = set(metric_names or ())
    metrics = [item for item in snapshot.metrics if not allowed or item.name in allowed]
    table = Table.grid(expand=True, padding=(0, 1))
    table.add_column("SIGNAL", ratio=1, overflow="crop")
    table.add_column("CURRENT", width=14)
    table.add_column("BASE", width=8, justify="right")
    table.add_column("DELTA", width=7, justify="right")
    table.add_column("STATE", width=9)
    if not metrics:
        table.add_row("No profile metrics", Text("-" * 14, style=MUTED), "0.0", "1.0x", Text("NORMAL", style=SUCCESS))
    for item in metrics:
        maximum = max(item.current_per_minute, item.baseline_per_minute, 1.0)
        state_style = HIGH if item.state == "SPIKE" else WARNING if item.state == "ELEVATED" else SUCCESS
        ratio = f"{item.deviation_ratio:.1f}x" if item.deviation_ratio < 100 else ">99x"
        table.add_row(
            Text(item.name, style=NEUTRAL),
            _mini_bar(item.current_per_minute, maximum, style=state_style if item.state != "NORMAL" else ACCENT),
            Text(f"{item.baseline_per_minute:.1f}", style=SECONDARY),
            Text(ratio, style=state_style if item.state != "NORMAL" else MUTED),
            Text(item.state, style=f"bold {state_style}"),
        )
    return _panel(table, f"RATE & BASELINE // SIGNAL TREND // {snapshot.window_seconds}s", SECONDARY)


def _recent_findings(findings, profile_label: str, *, compact: bool) -> Panel:
    table = Table(expand=True, box=None, padding=(0, 1))
    if compact:
        table.add_column("FINDING", ratio=1, overflow="fold")
    else:
        table.add_column("SEV", width=8)
        table.add_column("CATEGORY", width=13, overflow="crop")
        table.add_column("FINDING / EVIDENCE", ratio=1, overflow="fold")
    for finding in findings[:4]:
        if compact:
            body = Text()
            body.append_text(severity_text(finding.severity))
            body.append(f"  {finding.category.upper()}\n", style=MUTED)
            body.append(finding.title, style=f"bold {NEUTRAL}")
            body.append("\n")
            body.append(finding.evidence, style=MUTED)
            table.add_row(body)
        else:
            detail = Text(finding.title, style=f"bold {NEUTRAL}")
            detail.append("\n")
            detail.append(finding.evidence, style=MUTED)
            table.add_row(
                severity_text(finding.severity),
                Text(finding.category.upper(), style=SKY),
                detail,
            )
    if not findings:
        table.add_row(Text(f"No {profile_label.lower()} findings yet. Monitoring remains active.", style=SUCCESS))
    return _panel(table, "FINDING STREAM // EVIDENCE BOARD", WARNING, padding=(0, 0))


def _status_panel(text: str, *, title: str) -> Panel:
    return _panel(Text(text, style=MUTED), title, SUCCESS)


def _frame(sections: list[RenderableType], width: int) -> RenderableType:
    frame = Table(show_header=False, box=None, padding=0, width=width)
    frame.add_column(width=width)
    for section in sections:
        frame.add_row(section)
    return frame


def render_realtime_command_center(state) -> RenderableType:
    width = _frame_width()
    compact = width < _NARROW
    profile = state.profile
    events = state.focused_events
    findings = state.focused_findings
    severities = Counter(item.severity for item in findings)
    services = Counter(event.service or "unknown" for event in events if event.message)
    incidents = correlate(findings)
    anomalies = score_events(events)
    trend = state.trends
    allowed_metrics = set(profile.trend_metrics)
    spikes = sum(1 for item in trend.metrics if item.name in allowed_metrics and item.state == "SPIKE")
    risk = _risk(severities)
    age = state.activity_age
    activity = "waiting" if age is None else "receiving" if age < 2 else f"{age:.0f}s ago"
    rate = "warming" if age is not None and age < 2 and state.total_lines == state.rolling_count else f"{state.lines_per_second:.1f}/s"
    metrics = [
        ("EVENTS", f"{state.total_lines:,}", f"win {state.rolling_count:,}", ACCENT),
        ("RATE", rate, activity, SKY),
        ("FINDINGS", str(len(findings)), "focused", WARNING if findings else NEUTRAL),
        ("INCIDENTS", str(len(incidents)), "corr", INCIDENT if incidents else NEUTRAL),
        ("ANOMALIES", str(len(anomalies)), "scored", SECONDARY if anomalies else NEUTRAL),
        ("SPIKES", str(spikes), f"{trend.window_seconds}s", HIGH if spikes else NEUTRAL),
    ]
    sections: list[RenderableType] = [
        _header(
            "LIVE MONITOR",
            state.source,
            profile.label,
            risk,
            subtitle="LOCAL | READ-ONLY | Ctrl+C STOPS MONITORING",
        ),
        _metric_strip(metrics, compact),
    ]
    if width >= _WIDE:
        row_one = Table.grid(expand=True, padding=(0, 1))
        row_one.add_column(ratio=1)
        row_one.add_column(ratio=1)
        row_one.add_row(
            _event_flow(state.lines, title="EVENT FLOW"),
            _distribution("SEVERITY MIX", severities, compact=compact, semantic=True, title_style=WARNING),
        )
        sections.append(row_one)
        row_two = Table.grid(expand=True, padding=(0, 1))
        row_two.add_column(ratio=1)
        row_two.add_column(ratio=1)
        row_two.add_row(
            _distribution(
                "SERVICE LOAD",
                services,
                compact=compact,
                palette=_SERVICE_PALETTE,
                title_style=SKY,
            ),
            _signal_matrix(trend, profile.trend_metrics),
        )
        sections.append(row_two)
    else:
        sections.extend(
            (
                _event_flow(state.lines, title="EVENT FLOW"),
                _distribution("SEVERITY MIX", severities, compact=compact, semantic=True, title_style=WARNING),
                _distribution(
                    "SERVICE LOAD",
                    services,
                    compact=compact,
                    palette=_SERVICE_PALETTE,
                    title_style=SKY,
                ),
                _signal_matrix(trend, profile.trend_metrics),
            )
        )
    sections.extend(
        (
            _recent_findings(list(state.recent_findings), profile.label, compact=compact),
            _status_panel(
                f"ACTIVE | {state.total_bytes:,} bytes | {state.truncated_lines} oversized | "
                f"{state.dropped_window_lines} evicted | no remediation",
                title="SENSOR HEALTH",
            ),
        )
    )
    return _frame(sections, width)


def _source_activity(state, *, compact: bool) -> Panel:
    rows = [
        (path.name, state.source_counts.get(path.name, 0), path.exists() and path.is_file())
        for path in state.sources
    ]
    maximum = max([row[1] for row in rows] or [1])
    table = Table(expand=True, box=None, padding=(0, 1))
    table.add_column("SOURCE", ratio=2, overflow="crop")
    table.add_column("ACTIVITY", width=14)
    table.add_column("STATUS", width=9, no_wrap=True)
    table.add_column("EVENTS", width=7, justify="right")
    for index, (name, count, available) in enumerate(rows):
        tone = _SOURCE_PALETTE[index % len(_SOURCE_PALETTE)]
        table.add_row(
            Text(name, style=tone),
            _mini_bar(count, maximum, style=tone),
            Text("READY" if available else "MISSING", style=SUCCESS if available else WARNING),
            Text(str(count), style=f"bold {tone}"),
        )
    return _panel(table, "SOURCE PULSE // LIVE SOURCES", ACCENT, padding=(0, 0))


def _alerts(state, *, compact: bool) -> Panel:
    table = Table(expand=True, box=None, padding=(0, 1))
    if compact:
        table.add_column("ALERT", ratio=1, overflow="fold")
    else:
        table.add_column("ID", width=4, justify="right", style=MUTED)
        table.add_column("SEV", width=8)
        table.add_column("SOURCE", width=13, overflow="crop")
        table.add_column("ALERT / EVIDENCE", ratio=1, overflow="fold")
    for item in state.alerts[:5]:
        if compact:
            body = Text(f"{item.sequence:02d} ", style=MUTED)
            body.append_text(severity_text(item.severity))
            body.append(f"  {item.source} / {item.category}\n", style=MUTED)
            body.append(item.title, style=f"bold {NEUTRAL}")
            body.append("\n")
            body.append(item.evidence, style=MUTED)
            table.add_row(body)
        else:
            detail = Text(item.title, style=f"bold {NEUTRAL}")
            detail.append(f"  [{item.category}]", style=SECONDARY)
            detail.append("\n")
            detail.append(item.evidence, style=MUTED)
            table.add_row(
                f"{item.sequence:02d}",
                severity_text(item.severity),
                item.source,
                detail,
            )
    if not state.alerts:
        table.add_row(Text("No profile-matching alerts yet. All sources remain under local monitoring.", style=SUCCESS))
    return _panel(table, "ALERT STREAM // CORRELATION FEED", HIGH, padding=(0, 0))


def render_multisource_command_center(state) -> RenderableType:
    width = _frame_width()
    compact = width < _NARROW
    profile = state.profile
    findings = state.focused_findings
    severities = Counter(item.severity for item in findings)
    categories = Counter(item.category for item in findings)
    incidents = correlate(findings)
    trend = state.trends
    allowed_metrics = set(profile.trend_metrics)
    spikes = sum(1 for item in trend.metrics if item.name in allowed_metrics and item.state == "SPIKE")
    risk = _risk(severities)
    source_names = ", ".join(path.name for path in state.sources)
    metrics = [
        ("SOURCES", str(len(state.sources)), f"win {state.rolling_count:,}", ACCENT),
        ("EVENTS", f"{state.total_lines:,}", "all", SKY),
        ("LIVE RATE", f"{state.recent_eps:.2f}/s", "recent", SUCCESS),
        ("FINDINGS", str(len(findings)), "focused", WARNING if findings else NEUTRAL),
        ("INCIDENTS", str(len(incidents)), "corr", INCIDENT if incidents else NEUTRAL),
        ("SPIKES", str(spikes), f"{trend.window_seconds}s", HIGH if spikes else NEUTRAL),
    ]
    sections: list[RenderableType] = [
        _header(
            "MULTI-SOURCE SOC",
            source_names,
            profile.label,
            risk,
            subtitle="LOCAL | READ-ONLY | CROSS-SOURCE CORRELATION",
        ),
        _metric_strip(metrics, compact),
    ]
    if width >= _WIDE:
        top = Table.grid(expand=True, padding=(0, 1))
        top.add_column(ratio=1)
        top.add_column(ratio=1)
        top.add_row(_source_activity(state, compact=compact), _event_flow(state.raw_lines, title="CROSS-SOURCE EVENT FLOW"))
        sections.append(top)
        middle = Table.grid(expand=True, padding=(0, 1))
        middle.add_column(ratio=1)
        middle.add_column(ratio=1)
        middle.add_row(
            _distribution("SEVERITY MIX", severities, compact=compact, semantic=True, title_style=WARNING),
            _distribution(
                "FINDINGS BY CATEGORY",
                categories,
                compact=compact,
                palette=_CATEGORY_PALETTE,
                title_style=SECONDARY,
            ),
        )
        sections.append(middle)
        sections.append(_signal_matrix(trend, profile.trend_metrics))
    else:
        sections.extend(
            (
                _source_activity(state, compact=compact),
                _event_flow(state.raw_lines, title="CROSS-SOURCE EVENT FLOW"),
                _distribution("SEVERITY MIX", severities, compact=compact, semantic=True, title_style=WARNING),
                _distribution(
                    "FINDINGS BY CATEGORY",
                    categories,
                    compact=compact,
                    palette=_CATEGORY_PALETTE,
                    title_style=SECONDARY,
                ),
                _signal_matrix(trend, profile.trend_metrics),
            )
        )
    sections.extend(
        (
            _alerts(state, compact=compact),
            _status_panel(
                f"ACTIVE | {state.total_bytes:,} bytes | {len(state.sources)} sources | "
                f"{state.recent_eps:.2f} recent EPS | no remediation",
                title="SOC HEALTH",
            ),
        )
    )
    return _frame(sections, width)


__all__ = ["render_realtime_command_center", "render_multisource_command_center"]
