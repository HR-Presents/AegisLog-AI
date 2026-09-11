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
_BLOCKS = "▏▎▍▌▋▊▉█"


def _risk(counts: Counter[str]) -> str:
    if counts.get("CRITICAL"): return "CRITICAL"
    if counts.get("HIGH"): return "HIGH"
    if counts.get("MEDIUM"): return "REVIEW"
    return "CLEAR"


def _frame_width() -> int:
    return min(max(1, shutil.get_terminal_size((80, 24)).columns - 2), _MAX_WIDTH)


def _header(title: str, source: str, profile: str, risk: str, *, subtitle: str = "") -> Panel:
    grid = Table.grid(expand=True, padding=(0, 1)); grid.add_column(ratio=1); grid.add_column(no_wrap=True)
    brand = Text("AEGISLOG", style=f"bold {NEUTRAL}"); brand.append(f"  ◇  {title}", style=f"bold {ACCENT}")
    grid.add_row(brand, Text(f"POSTURE  {risk}", style=WARNING if risk != "CLEAR" else SUCCESS))
    source_line = Text("SOURCE  ", style=MUTED); source_line.append(source, style=NEUTRAL)
    mode = Text("PROFILE  ", style=MUTED); mode.append(profile.upper(), style=f"bold {ACCENT}")
    grid.add_row(source_line, mode); grid.add_row(Text(subtitle or "LOCAL-FIRST  ·  READ-ONLY  ·  DETERMINISTIC", style=MUTED), Text("HR-PRESENTS", style=f"bold {ACCENT}"))
    return Panel(grid, box=box.ROUNDED, border_style=ACCENT_SOFT, padding=(0, 1), width=_frame_width())


def _metric_cell(label: str, value: str, context: str, style: str) -> Text:
    cell = Text(justify="center"); cell.append(label, style=MUTED); cell.append("\n"); cell.append(value, style=f"bold {style}"); cell.append("\n"); cell.append(context, style=MUTED); return cell


def _metric_strip(metrics: list[tuple[str, str, str, str]], compact: bool) -> Panel:
    table = Table.grid(expand=True, padding=(0, 1)); columns = 2 if compact else len(metrics)
    for _ in range(columns): table.add_column(ratio=1)
    if compact:
        for index in range(0, len(metrics), 2):
            cells = [_metric_cell(*item) for item in metrics[index:index + 2]]
            while len(cells) < 2: cells.append(Text(""))
            table.add_row(*cells)
    else: table.add_row(*(_metric_cell(*item) for item in metrics))
    return Panel(table, title=Text(" TELEMETRY PULSE ", style=f"bold {ACCENT}"), title_align="left", box=box.ROUNDED, border_style=ACCENT_SOFT, padding=(0, 1))


def _mini_bar(count: int, maximum: int, width: int = 18, *, style: str = ACCENT) -> Text:
    maximum = max(1, maximum); units = (count / maximum) * width; full = int(units); frac = units - full
    text = Text("█" * full, style=style)
    if full < width and frac > 0: text.append(_BLOCKS[min(7, int(frac * 8))], style=style)
    text.append(" " * max(0, width - len(text.plain)), style=MUTED); return text


def _distribution(title: str, values: Counter[str], *, compact: bool, semantic: bool = False) -> Panel:
    items = values.most_common(6)
    if not items: return Panel(Text("No matching activity in this window.", style=MUTED), title=Text(f" {title} ", style=f"bold {ACCENT}"), title_align="left", box=box.ROUNDED, border_style=ACCENT_SOFT)
    maximum = max(count for _, count in items); total = max(1, sum(values.values()))
    table = Table.grid(expand=True, padding=(0, 1)); table.add_column(ratio=1, overflow="crop"); table.add_column(width=20); table.add_column(width=9, justify="right")
    for label, count in items:
        pct = count / total * 100; style = WARNING if semantic and str(label).upper() in {"MEDIUM", "HIGH", "CRITICAL"} else ACCENT
        table.add_row(Text(str(label).upper(), style=NEUTRAL), _mini_bar(count, maximum, style=style), Text(f"{count}  {pct:>3.0f}%", style=MUTED))
    return Panel(table, title=Text(f" {title} ", style=f"bold {ACCENT}"), title_align="left", box=box.ROUNDED, border_style=ACCENT_SOFT, padding=(0, 1))


def _recent_findings(findings, profile_label: str, *, compact: bool) -> Panel:
    table = Table(expand=True, box=None, padding=(0, 1))
    if compact: table.add_column("FINDING", ratio=1, overflow="fold")
    else:
        table.add_column("SEV", width=9); table.add_column("CATEGORY", width=14, overflow="crop"); table.add_column("FINDING", width=28, overflow="fold"); table.add_column("EVIDENCE", ratio=1, overflow="fold")
    for finding in findings[:8]:
        if compact:
            body = Text(); body.append_text(severity_text(finding.severity)); body.append(f"  {finding.category.upper()}\n", style=MUTED); body.append(finding.title, style=f"bold {NEUTRAL}"); body.append("\n"); body.append(finding.evidence, style=MUTED); table.add_row(body)
        else: table.add_row(severity_text(finding.severity), Text(finding.category, style=MUTED), Text(finding.title, style=NEUTRAL), Text(finding.evidence, style=MUTED))
    if not findings:
        if compact: table.add_row(Text(f"No {profile_label.lower()} findings yet. Monitoring remains active.", style=SUCCESS))
        else: table.add_row("-", "-", Text("No matching findings", style=SUCCESS), Text("Monitoring remains active", style=MUTED))
    return Panel(table, title=Text(" FINDING STREAM ", style=f"bold {ACCENT}"), title_align="left", box=box.ROUNDED, border_style=ACCENT_SOFT, padding=(0, 0))


def render_realtime_command_center(state) -> RenderableType:
    width = _frame_width(); compact = width < _NARROW; profile = state.profile; events = state.focused_events; findings = state.focused_findings
    severities = Counter(item.severity for item in findings); services = Counter(event.service or "unknown" for event in events if event.message); incidents = correlate(findings); anomalies = score_events(events); trend = state.trends
    allowed_metrics = set(profile.trend_metrics); spikes = sum(1 for item in trend.metrics if item.name in allowed_metrics and item.state == "SPIKE"); risk = _risk(severities); age = state.activity_age; activity = "waiting" if age is None else "receiving" if age < 2 else f"{age:.0f}s ago"
    metrics = [("EVENTS", f"{state.total_lines:,}", f"window {state.rolling_count:,}", ACCENT), ("RATE", f"{state.lines_per_second:.1f}/s", activity, NEUTRAL), ("FINDINGS", str(len(findings)), "profile-focused", WARNING if findings else NEUTRAL), ("INCIDENTS", str(len(incidents)), "correlated", INCIDENT if incidents else NEUTRAL), ("ANOMALIES", str(len(anomalies)), "event-scored", NEUTRAL), ("SPIKES", str(spikes), f"{trend.window_seconds}s baseline", WARNING if spikes else NEUTRAL)]
    sections: list[RenderableType] = [_header("LIVE MONITOR", state.source, profile.label, risk, subtitle="LOCAL  ·  READ-ONLY  ·  Ctrl+C STOPS MONITORING"), Text(""), _metric_strip(metrics, compact), Text("")]
    if width >= _WIDE:
        pair = Table.grid(expand=True, padding=(0, 2)); pair.add_column(ratio=1); pair.add_column(ratio=1); pair.add_row(_distribution("SEVERITY MIX", severities, compact=compact, semantic=True), _distribution("SERVICE LOAD", services, compact=compact)); sections.append(pair)
    else: sections.extend((_distribution("SEVERITY MIX", severities, compact=compact, semantic=True), Text(""), _distribution("SERVICE LOAD", services, compact=compact)))
    sections.extend((Text(""), render_trends(trend, profile.trend_metrics), Text(""), _recent_findings(list(state.recent_findings), profile.label, compact=compact), Text(""), Panel(Text(f"Monitoring active  ·  {state.total_bytes:,} bytes ingested  ·  {state.truncated_lines} oversized lines  ·  {state.dropped_window_lines} evicted  ·  no remediation", style=MUTED), title=Text(" SENSOR STATUS ", style=f"bold {ACCENT}"), title_align="left", box=box.ROUNDED, border_style=ACCENT_SOFT)))
    return Group(*sections)


def _source_activity(state, *, compact: bool) -> Panel:
    rows = [(path.name, state.source_counts.get(path.name, 0), path.exists() and path.is_file()) for path in state.sources]; maximum = max([r[1] for r in rows] or [1])
    table = Table(expand=True, box=None, padding=(0, 1)); table.add_column("SOURCE", ratio=2, overflow="crop"); table.add_column("ACTIVITY", width=20); table.add_column("STATUS", width=10, no_wrap=True); table.add_column("EVENTS", width=8, justify="right")
    for name, count, available in rows: table.add_row(Text(name, style=NEUTRAL), _mini_bar(count, maximum), Text("READY" if available else "MISSING", style=SUCCESS if available else WARNING), Text(str(count), style=f"bold {NEUTRAL}"))
    return Panel(table, title=Text(" SOURCE PULSE ", style=f"bold {ACCENT}"), title_align="left", box=box.ROUNDED, border_style=ACCENT_SOFT, padding=(0, 0))


def _alerts(state, *, compact: bool) -> Panel:
    table = Table(expand=True, box=None, padding=(0, 1))
    if compact: table.add_column("ALERT", ratio=1, overflow="fold")
    else:
        table.add_column("ID", width=5, justify="right", style=MUTED); table.add_column("SEV", width=9); table.add_column("SOURCE", width=15, overflow="crop"); table.add_column("CATEGORY", width=14, overflow="crop"); table.add_column("ALERT / EVIDENCE", ratio=1, overflow="fold")
    for item in state.alerts[:10]:
        if compact:
            body = Text(f"{item.sequence:02d} ", style=MUTED); body.append_text(severity_text(item.severity)); body.append(f"  {item.source} / {item.category}\n", style=MUTED); body.append(item.title, style=f"bold {NEUTRAL}"); body.append("\n"); body.append(item.evidence, style=MUTED); table.add_row(body)
        else:
            detail = Text(item.title, style=NEUTRAL); detail.append("\n"); detail.append(item.evidence, style=MUTED); table.add_row(f"{item.sequence:02d}", severity_text(item.severity), item.source, item.category, detail)
    if not state.alerts:
        if compact: table.add_row(Text("No profile-matching alerts yet. All sources remain under local monitoring.", style=SUCCESS))
        else: table.add_row("-", "-", "-", "-", Text("No profile-matching alerts yet", style=SUCCESS))
    return Panel(table, title=Text(" ALERT STREAM ", style=f"bold {ACCENT}"), title_align="left", box=box.ROUNDED, border_style=ACCENT_SOFT, padding=(0, 0))


def render_multisource_command_center(state) -> RenderableType:
    width = _frame_width(); compact = width < _NARROW; profile = state.profile; findings = state.focused_findings; severities = Counter(item.severity for item in findings); categories = Counter(item.category for item in findings); incidents = correlate(findings); trend = state.trends
    allowed_metrics = set(profile.trend_metrics); spikes = sum(1 for item in trend.metrics if item.name in allowed_metrics and item.state == "SPIKE"); risk = _risk(severities); source_names = ", ".join(path.name for path in state.sources)
    metrics = [("SOURCES", str(len(state.sources)), f"window {state.rolling_count:,}", ACCENT), ("EVENTS", f"{state.total_lines:,}", "all sources", NEUTRAL), ("LIVE RATE", f"{state.recent_eps:.2f}/s", "recent EPS", NEUTRAL), ("FINDINGS", str(len(findings)), "profile-focused", WARNING if findings else NEUTRAL), ("INCIDENTS", str(len(incidents)), "correlated", INCIDENT if incidents else NEUTRAL), ("SPIKES", str(spikes), f"{trend.window_seconds}s baseline", WARNING if spikes else NEUTRAL)]
    sections: list[RenderableType] = [_header("MULTI-SOURCE", source_names, profile.label, risk, subtitle="LOCAL  ·  READ-ONLY  ·  CROSS-SOURCE CORRELATION"), Text(""), _metric_strip(metrics, compact), Text(""), _source_activity(state, compact=compact), Text("")]
    if width >= _WIDE:
        pair = Table.grid(expand=True, padding=(0, 2)); pair.add_column(ratio=1); pair.add_column(ratio=1); pair.add_row(_distribution("SEVERITY MIX", severities, compact=compact, semantic=True), _distribution("FINDINGS BY CATEGORY", categories, compact=compact)); sections.append(pair)
    else: sections.extend((_distribution("SEVERITY MIX", severities, compact=compact, semantic=True), Text(""), _distribution("FINDINGS BY CATEGORY", categories, compact=compact)))
    sections.extend((Text(""), render_trends(trend, profile.trend_metrics), Text(""), _alerts(state, compact=compact), Text(""), Panel(Text(f"Multi-source monitoring active  ·  {state.total_bytes:,} bytes ingested across {len(state.sources)} sources  ·  no remediation", style=MUTED), title=Text(" SOC STATUS ", style=f"bold {ACCENT}"), title_align="left", box=box.ROUNDED, border_style=ACCENT_SOFT)))
    return Group(*sections)


__all__ = ["render_realtime_command_center", "render_multisource_command_center"]
