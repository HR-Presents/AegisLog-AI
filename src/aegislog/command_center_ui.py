from __future__ import annotations

import shutil
from collections import Counter

from rich import box
from rich.console import Group, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .anomaly import score_events
from .incidents import correlate
from .theme import ACCENT, ACCENT_SOFT, INCIDENT, MUTED, NEUTRAL, SUCCESS, WARNING, severity_text
from .trends import render_trends

_NARROW = 72
_WIDE = 104
_MAX_WIDTH = 144


def _risk(counts: Counter[str]) -> str:
    if counts.get("CRITICAL"):
        return "CRITICAL"
    if counts.get("HIGH"):
        return "HIGH"
    if counts.get("MEDIUM"):
        return "REVIEW"
    return "CLEAR"


def _frame_width() -> int:
    return min(max(1, shutil.get_terminal_size((80, 24)).columns - 2), _MAX_WIDTH)


def _header(title: str, source: str, profile: str, risk: str, *, subtitle: str = "") -> Panel:
    grid = Table.grid(expand=True, padding=(0, 1))
    grid.add_column(ratio=1)
    grid.add_column(no_wrap=True)
    brand = Text("AEGISLOG", style=f"bold {NEUTRAL}")
    brand.append(f"  //  {title}", style=f"bold {ACCENT}")
    grid.add_row(brand, Text(f"POSTURE  {risk}", style=NEUTRAL))
    source_line = Text("SOURCE  ", style=MUTED)
    source_line.append(source, style=NEUTRAL)
    mode = Text("PROFILE  ", style=MUTED)
    mode.append(profile.upper(), style=f"bold {ACCENT}")
    grid.add_row(source_line, mode)
    grid.add_row(Text(subtitle or "LOCAL-FIRST / READ-ONLY / DETERMINISTIC", style=MUTED), Text("MADE BY HR-PRESENTS", style=f"bold {ACCENT}"))
    return Panel(grid, box=box.ASCII, border_style=ACCENT_SOFT, padding=(0, 1), width=_frame_width())


def _metric_strip(metrics: list[tuple[str, str, str, str]], compact: bool) -> Panel:
    table = Table.grid(expand=True, padding=(0, 1))
    columns = 2 if compact else len(metrics)
    for _ in range(columns):
        table.add_column(ratio=1)
    if compact:
        for index in range(0, len(metrics), 2):
            cells = [_metric_cell(*item) for item in metrics[index:index + 2]]
            while len(cells) < 2:
                cells.append(Text(""))
            table.add_row(*cells)
    else:
        table.add_row(*(_metric_cell(*item) for item in metrics))
    return Panel(table, title=Text(" LIVE SECURITY METRICS ", style=f"bold {ACCENT}"), title_align="left", box=box.ASCII, border_style=ACCENT_SOFT, padding=(0, 1))


def _metric_cell(label: str, value: str, context: str, style: str) -> Text:
    cell = Text(justify="center")
    cell.append(label, style=MUTED)
    cell.append("\n")
    cell.append(value, style=f"bold {NEUTRAL}")
    cell.append("\n")
    cell.append(context, style=MUTED)
    return cell


def _distribution(title: str, values: Counter[str], *, compact: bool, semantic: bool = False) -> Panel:
    items = values.most_common(6)
    if not items:
        return Panel(Text("No matching activity in the current rolling window.", style=SUCCESS), title=Text(f" {title} ", style=f"bold {ACCENT}"), title_align="left", box=box.ASCII, border_style=ACCENT_SOFT)
    table = Table.grid(expand=True, padding=(0, 1))
    table.add_column(ratio=1, overflow="crop")
    table.add_column(width=8, justify="right", no_wrap=True)
    for label, count in items:
        table.add_row(Text(str(label).upper(), style=NEUTRAL), Text(str(count), style=f"bold {NEUTRAL}"))
    return Panel(table, title=Text(f" {title} ", style=f"bold {ACCENT}"), title_align="left", box=box.ASCII, border_style=ACCENT_SOFT, padding=(0, 1))


def _recent_findings(findings, profile_label: str, *, compact: bool) -> Panel:
    table = Table(expand=True, box=None, padding=(0, 1))
    if compact:
        table.add_column("FINDING", ratio=1, overflow="fold")
    else:
        table.add_column("SEV", width=9)
        table.add_column("CATEGORY", width=14, overflow="crop")
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
            table.add_row(severity_text(finding.severity), Text(finding.category, style=MUTED), Text(finding.title, style=NEUTRAL), Text(finding.evidence, style=MUTED))
    if not findings:
        if compact:
            table.add_row(Text(f"No {profile_label.lower()} findings yet. Monitoring remains active.", style=SUCCESS))
        else:
            table.add_row("-", "-", Text("No matching findings", style=SUCCESS), Text("Monitoring remains active", style=MUTED))
    return Panel(table, title=Text(" RECENT SECURITY FINDINGS ", style=f"bold {ACCENT}"), title_align="left", box=box.ASCII, border_style=ACCENT_SOFT, padding=(0, 0))


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
    metrics = [("EVENTS", f"{state.total_lines:,}", f"window {state.rolling_count:,}", ACCENT), ("RATE", f"{state.lines_per_second:.1f}/s", activity, ACCENT), ("FINDINGS", str(len(findings)), "profile-focused", WARNING), ("INCIDENTS", str(len(incidents)), "correlated", INCIDENT), ("ANOMALIES", str(len(anomalies)), "event-scored", ACCENT), ("SPIKES", str(spikes), f"{trend.window_seconds}s baseline", WARNING)]
    sections: list[RenderableType] = [_header("LIVE MONITOR", state.source, profile.label, risk, subtitle="LOCAL / READ-ONLY / Ctrl+C STOPS MONITORING"), Text(""), _metric_strip(metrics, compact), Text("")]
    if width >= _WIDE:
        pair = Table.grid(expand=True, padding=(0, 2)); pair.add_column(ratio=1); pair.add_column(ratio=1)
        pair.add_row(_distribution("SEVERITY DISTRIBUTION", severities, compact=compact, semantic=True), _distribution("SERVICE ACTIVITY", services, compact=compact))
        sections.append(pair)
    else:
        sections.extend((_distribution("SEVERITY DISTRIBUTION", severities, compact=compact, semantic=True), Text(""), _distribution("SERVICE ACTIVITY", services, compact=compact)))
    sections.extend((Text(""), render_trends(trend, profile.trend_metrics), Text(""), _recent_findings(list(state.recent_findings), profile.label, compact=compact), Text(""), Panel(Text(f"Read-only monitoring active. {state.total_bytes:,} bytes ingested; {state.truncated_lines} oversized lines truncated; {state.dropped_window_lines} old lines evicted. No remediation is performed.", style=MUTED), title=Text(" LIVE STATUS ", style=f"bold {ACCENT}"), title_align="left", box=box.ASCII, border_style=ACCENT_SOFT)))
    return Group(*sections)


def _source_activity(state, *, compact: bool) -> Panel:
    rows = [(path.name, state.source_counts.get(path.name, 0), path.exists() and path.is_file()) for path in state.sources]
    table = Table(expand=True, box=None, padding=(0, 1))
    table.add_column("SOURCE", ratio=2, overflow="crop")
    table.add_column("STATUS", width=10, no_wrap=True)
    table.add_column("EVENTS", width=8, justify="right")
    for name, count, available in rows:
        table.add_row(Text(name, style=NEUTRAL), Text("READY" if available else "MISSING", style=SUCCESS if available else WARNING), Text(str(count), style=f"bold {NEUTRAL}"))
    return Panel(table, title=Text(" SOURCE ACTIVITY ", style=f"bold {ACCENT}"), title_align="left", box=box.ASCII, border_style=ACCENT_SOFT, padding=(0, 0))


def _alerts(state, *, compact: bool) -> Panel:
    table = Table(expand=True, box=None, padding=(0, 1))
    if compact:
        table.add_column("ALERT", ratio=1, overflow="fold")
    else:
        table.add_column("ID", width=5, justify="right", style=MUTED)
        table.add_column("SEV", width=9)
        table.add_column("SOURCE", width=15, overflow="crop")
        table.add_column("CATEGORY", width=14, overflow="crop")
        table.add_column("ALERT / EVIDENCE", ratio=1, overflow="fold")
    for item in state.alerts[:10]:
        if compact:
            body = Text(f"{item.sequence:02d} ", style=MUTED); body.append_text(severity_text(item.severity)); body.append(f"  {item.source} / {item.category}\n", style=MUTED); body.append(item.title, style=f"bold {NEUTRAL}"); body.append("\n"); body.append(item.evidence, style=MUTED); table.add_row(body)
        else:
            detail = Text(item.title, style=NEUTRAL); detail.append("\n"); detail.append(item.evidence, style=MUTED); table.add_row(f"{item.sequence:02d}", severity_text(item.severity), item.source, item.category, detail)
    if not state.alerts:
        if compact: table.add_row(Text("No profile-matching alerts yet. All sources remain under local monitoring.", style=SUCCESS))
        else: table.add_row("-", "-", "-", "-", Text("No profile-matching alerts yet", style=SUCCESS))
    return Panel(table, title=Text(" LIVE SECURITY ALERT FEED ", style=f"bold {ACCENT}"), title_align="left", box=box.ASCII, border_style=ACCENT_SOFT, padding=(0, 0))


def render_multisource_command_center(state) -> RenderableType:
    width = _frame_width(); compact = width < _NARROW; profile = state.profile; findings = state.focused_findings
    severities = Counter(item.severity for item in findings); categories = Counter(item.category for item in findings); incidents = correlate(findings); trend = state.trends
    allowed_metrics = set(profile.trend_metrics); spikes = sum(1 for item in trend.metrics if item.name in allowed_metrics and item.state == "SPIKE"); risk = _risk(severities); source_names = ", ".join(path.name for path in state.sources)
    metrics = [("SOURCES", str(len(state.sources)), f"window {state.rolling_count:,}", ACCENT), ("EVENTS", f"{state.total_lines:,}", "all sources", ACCENT), ("LIVE RATE", f"{state.recent_eps:.2f}/s", "recent EPS", ACCENT), ("FINDINGS", str(len(findings)), "profile-focused", WARNING), ("INCIDENTS", str(len(incidents)), "correlated", INCIDENT), ("SPIKES", str(spikes), f"{trend.window_seconds}s baseline", WARNING)]
    sections: list[RenderableType] = [_header("MULTI-SOURCE", source_names, profile.label, risk, subtitle="LOCAL / READ-ONLY / CROSS-SOURCE CORRELATION"), Text(""), _metric_strip(metrics, compact), Text(""), _source_activity(state, compact=compact), Text("")]
    if width >= _WIDE:
        pair = Table.grid(expand=True, padding=(0, 2)); pair.add_column(ratio=1); pair.add_column(ratio=1); pair.add_row(_distribution("SEVERITY DISTRIBUTION", severities, compact=compact, semantic=True), _distribution("FINDINGS BY CATEGORY", categories, compact=compact)); sections.append(pair)
    else:
        sections.extend((_distribution("SEVERITY DISTRIBUTION", severities, compact=compact, semantic=True), Text(""), _distribution("FINDINGS BY CATEGORY", categories, compact=compact)))
    sections.extend((Text(""), render_trends(trend, profile.trend_metrics), Text(""), _alerts(state, compact=compact), Text(""), Panel(Text(f"Read-only multi-source monitoring active. {state.total_bytes:,} bytes ingested across {len(state.sources)} sources. No remediation is performed.", style=MUTED), title=Text(" SOC STATUS ", style=f"bold {ACCENT}"), title_align="left", box=box.ASCII, border_style=ACCENT_SOFT)))
    return Group(*sections)


__all__ = ["render_realtime_command_center", "render_multisource_command_center"]
