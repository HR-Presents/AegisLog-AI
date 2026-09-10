from __future__ import annotations

import shutil
from collections import Counter
from pathlib import Path

from rich import box
from rich.console import Group, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from . import __version__
from .anomaly import score_events
from .incidents import correlate
from .theme import (
    ACCENT,
    ACCENT_SOFT,
    ANOMALY,
    INCIDENT,
    MUTED,
    NEUTRAL,
    SUCCESS,
    WARNING,
    risk_style,
    severity_style,
    severity_text,
)
from .trends import render_trends

_NARROW = 72
_WIDE = 104
_BAR_WIDTH = 18


def _risk(counts: Counter[str]) -> str:
    if counts.get("CRITICAL"):
        return "CRITICAL"
    if counts.get("HIGH"):
        return "HIGH"
    if counts.get("MEDIUM"):
        return "REVIEW"
    return "CLEAR"


def _bar(value: int | float, maximum: int | float, width: int = _BAR_WIDTH, *, style: str = ACCENT) -> Text:
    maximum = max(float(maximum), 1.0)
    filled = 0 if value <= 0 else max(1, round(float(value) / maximum * width))
    filled = min(width, filled)
    text = Text("#" * filled, style=style)
    text.append("." * (width - filled), style=MUTED)
    return text


def _header(title: str, source: str, profile: str, risk: str, *, subtitle: str = "") -> Panel:
    grid = Table.grid(expand=True, padding=(0, 1))
    grid.add_column(ratio=1)
    grid.add_column(no_wrap=True)
    brand = Text("/A\\  AEGISLOG", style=f"bold {ACCENT}")
    brand.append(f"  /  {title}", style=f"bold {NEUTRAL}")
    status = Text()
    status.append(f"VERSION v{__version__}", style=MUTED)
    status.append("   POSTURE ", style=MUTED)
    status.append(risk, style=f"bold {risk_style(risk)}")
    grid.add_row(brand, status)
    source_line = Text("SOURCE  ", style=MUTED)
    source_line.append(source, style=NEUTRAL)
    mode = Text("PROFILE  ", style=MUTED)
    mode.append(profile.upper(), style=f"bold {ACCENT}")
    grid.add_row(source_line, mode)
    if subtitle:
        grid.add_row(Text(subtitle, style=MUTED), Text("LOCAL / READ-ONLY", style=MUTED))
    return Panel(
        grid,
        box=box.ASCII,
        border_style=ACCENT_SOFT,
        padding=(0, 1),
    )


def _metric_strip(metrics: list[tuple[str, str, str, str]], compact: bool) -> Panel:
    if compact:
        table = Table.grid(expand=True, padding=(0, 1))
        table.add_column(ratio=1)
        table.add_column(ratio=1)
        for index in range(0, len(metrics), 2):
            pair = metrics[index : index + 2]
            cells = [_metric_cell(*item) for item in pair]
            if len(cells) == 1:
                cells.append(Text(""))
            table.add_row(*cells)
    else:
        table = Table.grid(expand=True, padding=(0, 1))
        for _ in metrics:
            table.add_column(ratio=1)
        table.add_row(*(_metric_cell(*item) for item in metrics))
    return Panel(
        table,
        title=Text(" LIVE SECURITY METRICS ", style=f"bold {ACCENT}"),
        title_align="left",
        box=box.ASCII,
        border_style=ACCENT_SOFT,
        padding=(0, 1),
    )


def _metric_cell(label: str, value: str, context: str, style: str) -> Text:
    cell = Text(justify="center")
    cell.append(label, style=MUTED)
    cell.append("\n")
    cell.append(value, style=f"bold {style}")
    cell.append("\n")
    cell.append(context, style=MUTED)
    return cell


def _distribution(title: str, values: Counter[str], *, compact: bool, semantic: bool = False) -> Panel:
    items = values.most_common(6)
    if not items:
        return Panel(
            Text("No matching activity in the current rolling window.", style=SUCCESS),
            title=Text(f" {title} ", style=f"bold {ACCENT}"),
            title_align="left",
            box=box.ASCII,
            border_style=ACCENT_SOFT,
        )
    maximum = max(count for _, count in items)
    table = Table.grid(expand=True, padding=(0, 1))
    table.add_column(width=16 if not compact else 12, overflow="ellipsis")
    if not compact:
        table.add_column(width=_BAR_WIDTH)
    table.add_column(width=7, justify="right")
    for label, count in items:
        style = severity_style(label) if semantic else ACCENT
        cells: list[RenderableType] = [Text(str(label).upper(), style=f"bold {style}")]
        if not compact:
            cells.append(_bar(count, maximum, style=style))
        cells.append(Text(str(count), style=f"bold {style}"))
        table.add_row(*cells)
    return Panel(
        table,
        title=Text(f" {title} ", style=f"bold {ACCENT}"),
        title_align="left",
        box=box.ASCII,
        border_style=ACCENT_SOFT,
        padding=(0, 1),
    )


def _recent_findings(findings, profile_label: str, *, compact: bool) -> Panel:
    table = Table(expand=True, box=None, padding=(0, 1))
    if compact:
        table.add_column("FINDING", ratio=1, overflow="fold")
    else:
        table.add_column("SEV", width=9)
        table.add_column("CATEGORY", width=14, overflow="ellipsis")
        table.add_column("FINDING", width=28, overflow="fold")
        table.add_column("EVIDENCE", ratio=1, overflow="fold")
    for finding in findings[:8]:
        if compact:
            body = Text()
            body.append_text(severity_text(finding.severity))
            body.append(f"  {finding.category.upper()}\n", style=MUTED)
            body.append(finding.title, style=f"bold {NEUTRAL}")
            body.append("\n")
            body.append(finding.evidence, style=MUTED)
            table.add_row(body)
        else:
            table.add_row(
                severity_text(finding.severity),
                Text(finding.category),
                Text(finding.title, style=NEUTRAL),
                Text(finding.evidence, style=MUTED),
            )
    if not findings:
        if compact:
            table.add_row(Text(f"No {profile_label.lower()} findings yet. Monitoring remains active.", style=SUCCESS))
        else:
            table.add_row("-", "-", Text("No matching findings", style=SUCCESS), Text("Monitoring remains active", style=MUTED))
    return Panel(
        table,
        title=Text(" RECENT SECURITY FINDINGS ", style=f"bold {ACCENT}"),
        title_align="left",
        box=box.ASCII,
        border_style=ACCENT_SOFT,
        padding=(0, 0),
    )


def render_realtime_command_center(state) -> RenderableType:
    """Render the existing RealtimeState as a data-aware terminal command center."""
    width = shutil.get_terminal_size((80, 24)).columns
    compact = width < _NARROW
    profile = state.profile
    events = state.focused_events
    findings = state.focused_findings
    severities = Counter(item.severity for item in findings)
    categories = Counter(item.category for item in findings)
    services = Counter(event.service or "unknown" for event in events if event.message)
    incidents = correlate(findings)
    anomalies = score_events(events)
    trend = state.trends
    allowed_metrics = set(profile.trend_metrics)
    spikes = sum(1 for item in trend.metrics if item.name in allowed_metrics and item.state == "SPIKE")
    risk = _risk(severities)
    age = state.activity_age
    activity = "waiting" if age is None else "receiving" if age < 2 else f"{age:.0f}s ago"

    metrics = [
        ("EVENTS", f"{state.total_lines:,}", f"window {state.rolling_count:,}", ACCENT),
        ("RATE", f"{state.lines_per_second:.1f}/s", activity, ACCENT),
        ("FINDINGS", str(len(findings)), "profile-focused", WARNING if findings else SUCCESS),
        ("INCIDENTS", str(len(incidents)), "correlated", INCIDENT),
        ("ANOMALIES", str(len(anomalies)), "event-scored", ANOMALY),
        ("SPIKES", str(spikes), f"{trend.window_seconds}s baseline", WARNING if spikes else SUCCESS),
    ]

    sections: list[RenderableType] = [
        _header("LIVE MONITOR", state.source, profile.label, risk, subtitle="Ctrl+C stops monitoring"),
        Text(""),
        _metric_strip(metrics, compact),
        Text(""),
    ]
    if width >= _WIDE:
        pair = Table.grid(expand=True, padding=(0, 1))
        pair.add_column(ratio=1)
        pair.add_column(ratio=1)
        pair.add_row(
            _distribution("SEVERITY DISTRIBUTION", severities, compact=compact, semantic=True),
            _distribution("SERVICE ACTIVITY", services, compact=compact),
        )
        sections.append(pair)
    else:
        sections.extend((
            _distribution("SEVERITY DISTRIBUTION", severities, compact=compact, semantic=True),
            Text(""),
            _distribution("SERVICE ACTIVITY", services, compact=compact),
        ))
    sections.extend((
        Text(""),
        render_trends(trend, profile.trend_metrics),
        Text(""),
        _recent_findings(list(state.recent_findings), profile.label, compact=compact),
        Text(""),
        Panel(
            Text(
                f"Read-only monitoring active. {state.total_bytes:,} bytes ingested; "
                f"{state.truncated_lines} oversized lines truncated; {state.dropped_window_lines} old lines evicted. "
                "No remediation is performed.",
                style=MUTED,
            ),
            title=Text(" LIVE STATUS ", style=f"bold {SUCCESS if risk == 'CLEAR' else WARNING}"),
            title_align="left",
            box=box.ASCII,
            border_style=SUCCESS if risk == "CLEAR" else WARNING,
        ),
    ))
    return Group(*sections)


def _source_activity(state, *, compact: bool) -> Panel:
    rows = [(path.name, state.source_counts.get(path.name, 0), path.exists() and path.is_file()) for path in state.sources]
    maximum = max((count for _, count, _ in rows), default=1)
    table = Table(expand=True, box=None, padding=(0, 1))
    table.add_column("SOURCE", ratio=2, overflow="ellipsis")
    table.add_column("STATUS", width=10, no_wrap=True)
    if not compact:
        table.add_column("ACTIVITY", width=_BAR_WIDTH)
    table.add_column("EVENTS", width=8, justify="right")
    for name, count, available in rows:
        cells: list[RenderableType] = [
            Text(name, style=NEUTRAL),
            Text("READY" if available else "MISSING", style=SUCCESS if available else WARNING),
        ]
        if not compact:
            cells.append(_bar(count, maximum))
        cells.append(Text(str(count), style=f"bold {ACCENT}"))
        table.add_row(*cells)
    return Panel(
        table,
        title=Text(" SOURCE ACTIVITY ", style=f"bold {ACCENT}"),
        title_align="left",
        box=box.ASCII,
        border_style=ACCENT_SOFT,
        padding=(0, 0),
    )


def _alerts(state, *, compact: bool) -> Panel:
    table = Table(expand=True, box=None, padding=(0, 1))
    if compact:
        table.add_column("ALERT", ratio=1, overflow="fold")
    else:
        table.add_column("#", width=4, justify="right", style=ACCENT)
        table.add_column("SEV", width=9)
        table.add_column("SOURCE", width=15, overflow="ellipsis")
        table.add_column("CATEGORY", width=14, overflow="ellipsis")
        table.add_column("ALERT / EVIDENCE", ratio=1, overflow="fold")
    for item in state.alerts[:10]:
        if compact:
            body = Text(f"#{item.sequence} ", style=ACCENT)
            body.append_text(severity_text(item.severity))
            body.append(f"  {item.source} / {item.category}\n", style=MUTED)
            body.append(item.title, style=f"bold {NEUTRAL}")
            body.append("\n")
            body.append(item.evidence, style=MUTED)
            table.add_row(body)
        else:
            detail = Text(item.title, style=NEUTRAL)
            detail.append("\n")
            detail.append(item.evidence, style=MUTED)
            table.add_row(str(item.sequence), severity_text(item.severity), item.source, item.category, detail)
    if not state.alerts:
        if compact:
            table.add_row(Text("No profile-matching alerts yet. All sources remain under local monitoring.", style=SUCCESS))
        else:
            table.add_row("-", "-", "-", "-", Text("No profile-matching alerts yet", style=SUCCESS))
    return Panel(
        table,
        title=Text(" LIVE SECURITY ALERT FEED ", style=f"bold {INCIDENT}"),
        title_align="left",
        box=box.ASCII,
        border_style=INCIDENT,
        padding=(0, 0),
    )


def render_multisource_command_center(state) -> RenderableType:
    """Render MultiSourceState using real source counts, rates, alerts, and correlations."""
    width = shutil.get_terminal_size((80, 24)).columns
    compact = width < _NARROW
    profile = state.profile
    events = state.focused_events
    findings = state.focused_findings
    severities = Counter(item.severity for item in findings)
    categories = Counter(item.category for item in findings)
    incidents = correlate(findings)
    anomalies = score_events(events)
    trend = state.trends
    allowed_metrics = set(profile.trend_metrics)
    spikes = sum(1 for item in trend.metrics if item.name in allowed_metrics and item.state == "SPIKE")
    risk = _risk(severities)
    source_names = ", ".join(path.name for path in state.sources)

    metrics = [
        ("SOURCES", str(len(state.sources)), f"window {state.rolling_count:,}", ACCENT),
        ("EVENTS", f"{state.total_lines:,}", "all sources", ACCENT),
        ("LIVE RATE", f"{state.recent_eps:.2f}/s", "recent EPS", ACCENT),
        ("FINDINGS", str(len(findings)), "profile-focused", WARNING if findings else SUCCESS),
        ("INCIDENTS", str(len(incidents)), "correlated", INCIDENT),
        ("SPIKES", str(spikes), f"{trend.window_seconds}s baseline", WARNING if spikes else SUCCESS),
    ]

    sections: list[RenderableType] = [
        _header("MULTI-SOURCE", source_names, profile.label, risk, subtitle="Cross-source correlation / Ctrl+C stops monitoring"),
        Text(""),
        _metric_strip(metrics, compact),
        Text(""),
        _source_activity(state, compact=compact),
        Text(""),
    ]
    if width >= _WIDE:
        pair = Table.grid(expand=True, padding=(0, 1))
        pair.add_column(ratio=1)
        pair.add_column(ratio=1)
        pair.add_row(
            _distribution("SEVERITY DISTRIBUTION", severities, compact=compact, semantic=True),
            _distribution("FINDINGS BY CATEGORY", categories, compact=compact),
        )
        sections.append(pair)
    else:
        sections.extend((
            _distribution("SEVERITY DISTRIBUTION", severities, compact=compact, semantic=True),
            Text(""),
            _distribution("FINDINGS BY CATEGORY", categories, compact=compact),
        ))
    sections.extend((
        Text(""),
        render_trends(trend, profile.trend_metrics),
        Text(""),
        _alerts(state, compact=compact),
        Text(""),
        Panel(
            Text(
                f"Read-only multi-source monitoring active. {state.total_bytes:,} bytes ingested across "
                f"{len(state.sources)} sources. No remediation is performed.",
                style=MUTED,
            ),
            title=Text(" SOC STATUS ", style=f"bold {SUCCESS if risk == 'CLEAR' else WARNING}"),
            title_align="left",
            box=box.ASCII,
            border_style=SUCCESS if risk == "CLEAR" else WARNING,
        ),
    ))
    return Group(*sections)


__all__ = ["render_realtime_command_center", "render_multisource_command_center"]
