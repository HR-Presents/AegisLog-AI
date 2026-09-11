from __future__ import annotations

from pathlib import Path

from rich import box
from rich.align import Align
from rich.console import Group, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .dashboard import DashboardData, analyze_dashboard
from .theme import ACCENT, ACCENT_SOFT, INCIDENT, MUTED, NEUTRAL, SUCCESS, severity_style

_MAX_WIDTH = 144
_SEVERITY_RANK = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "INFO": 0}


def _rank(value: str) -> int:
    return _SEVERITY_RANK.get(value.upper(), 0)


def _risk(data: DashboardData) -> str:
    severities = {item.severity for item in data.findings}
    severities.update(item.severity for item in data.incidents)
    for name in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
        if name in severities:
            return "REVIEW" if name == "MEDIUM" else name
    return "CLEAR"


def _header(data: DashboardData, width: int) -> Panel:
    grid = Table.grid(expand=True, padding=(0, 1))
    grid.add_column(ratio=1)
    grid.add_column(no_wrap=True)
    title = Text("AEGISLOG", style=f"bold {NEUTRAL}")
    title.append("  //  ANALYZE LOG", style=f"bold {ACCENT}")
    status = Text("ANALYSIS COMPLETE", style=f"bold {SUCCESS}")
    grid.add_row(title, status)
    grid.add_row(Text("LOCAL-FIRST  |  READ-ONLY  |  DETERMINISTIC", style=MUTED), Text(f"POSTURE  {_risk(data)}", style=NEUTRAL))
    grid.add_row(Text("MADE BY HR-PRESENTS", style=f"bold {ACCENT}"), Text("SOURCE UNCHANGED", style=MUTED))
    return Panel(grid, box=box.ASCII, border_style=ACCENT_SOFT, padding=(0, 1), width=width)


def _metrics(data: DashboardData) -> Text:
    elevated = sum(1 for item in data.findings if _rank(item.severity) >= _rank("MEDIUM"))
    row = Text()
    entries = (("EVENTS", data.lines), ("FINDINGS", len(data.findings)), ("ELEVATED", elevated), ("INCIDENTS", len(data.incidents)), ("ANOMALIES", len(data.anomalies)))
    for index, (label, value) in enumerate(entries):
        if index:
            row.append("   |   ", style=MUTED)
        row.append(label + " ", style=f"bold {ACCENT}")
        row.append(str(value), style=f"bold {NEUTRAL}")
    return row


def _source_block(data: DashboardData) -> Panel:
    source_name = Path(data.source).name or data.source
    grid = Table.grid(expand=True, padding=(0, 1))
    grid.add_column(width=9, no_wrap=True)
    grid.add_column(ratio=1, overflow="fold")
    grid.add_row(Text("SOURCE", style=f"bold {ACCENT}"), Text(source_name, style=NEUTRAL))
    grid.add_row(Text("PATH", style=MUTED), Text(data.source, style=MUTED, overflow="fold"))
    grid.add_row(Text("METRICS", style=MUTED), _metrics(data))
    return Panel(grid, title=Text(" INVESTIGATION SUMMARY ", style=f"bold {ACCENT}"), title_align="left", box=box.ASCII, border_style=ACCENT_SOFT, padding=(0, 1))


def _top_findings(data: DashboardData, limit: int = 3) -> Panel:
    ordered = sorted(data.findings, key=lambda item: (-_rank(item.severity), item.category, item.title))
    body: list[RenderableType] = []
    if not ordered:
        body.append(Text("No rule-backed findings retained.", style=SUCCESS))
    for index, item in enumerate(ordered[:limit]):
        if index:
            body.append(Text(""))
        line = Text()
        line.append(f"[{item.severity}] ", style=f"bold {severity_style(item.severity)}")
        line.append(item.title, style=f"bold {NEUTRAL}")
        evidence = " ".join(item.evidence.split())
        if len(evidence) > 110:
            evidence = evidence[:107].rstrip() + "..."
        line.append("\n    ")
        line.append(evidence, style=MUTED)
        body.append(line)
    if len(ordered) > limit:
        body.append(Text(f"\n+ {len(ordered) - limit} more finding(s) in the local HTML report.", style=MUTED))
    return Panel(Group(*body), title=Text(" TOP FINDINGS ", style=f"bold {ACCENT}"), title_align="left", box=box.ASCII, border_style=ACCENT_SOFT, padding=(0, 1))


def _analyst_focus(data: DashboardData) -> Panel:
    incidents = sorted(data.incidents, key=lambda item: (-_rank(item.severity), -item.count, item.title))
    findings = sorted(data.findings, key=lambda item: (-_rank(item.severity), item.title))
    grid = Table.grid(expand=True, padding=(0, 1))
    grid.add_column(width=9, no_wrap=True)
    grid.add_column(ratio=1, overflow="fold")
    if incidents:
        item = incidents[0]
        incident_id = f"INC-{item.id.upper()[:8]}"
        primary = Text(incident_id, style=f"bold {INCIDENT}")
        primary.append("  " + item.title, style=NEUTRAL)
        grid.add_row(Text("PRIMARY", style=f"bold {ACCENT}"), primary)
        grid.add_row(Text("ACTION", style=MUTED), Text("Review correlated evidence and surrounding telemetry.", style=NEUTRAL))
    elif findings:
        item = findings[0]
        grid.add_row(Text("PRIMARY", style=f"bold {ACCENT}"), Text(item.title, style=NEUTRAL))
        grid.add_row(Text("ACTION", style=MUTED), Text(item.recommendation, style=NEUTRAL))
    else:
        grid.add_row(Text("PRIMARY", style=f"bold {ACCENT}"), Text("No elevated investigation target", style=SUCCESS))
        grid.add_row(Text("ACTION", style=MUTED), Text("Preserve source telemetry and review coverage as needed.", style=NEUTRAL))
    return Panel(grid, title=Text(" ANALYST FOCUS ", style=f"bold {ACCENT}"), title_align="left", box=box.ASCII, border_style=ACCENT_SOFT, padding=(0, 1))


def _next(data: DashboardData) -> Panel:
    grid = Table.grid(expand=True, padding=(0, 1))
    grid.add_column(width=12, no_wrap=True)
    grid.add_column(ratio=1)
    grid.add_row(Text("incidents", style=f"bold {ACCENT}"), Text("View correlated incidents", style=MUTED))
    grid.add_row(Text("investigate", style=f"bold {ACCENT}"), Text("Open incident evidence", style=MUTED))
    grid.add_row(Text("report", style=f"bold {ACCENT}"), Text("Open the full HTML investigation report", style=MUTED))
    return Panel(grid, title=Text(" NEXT ACTIONS ", style=f"bold {ACCENT}"), title_align="left", box=box.ASCII, border_style=ACCENT_SOFT, padding=(0, 1))


def render_dashboard(data: DashboardData, *, screen_width: int | None = None) -> RenderableType:
    width = min(max(70, screen_width or 100), _MAX_WIDTH)
    body: list[RenderableType] = [_header(data, width), Text(""), _source_block(data), Text("")]
    if width >= 104:
        layout = Table.grid(expand=True, padding=(0, 2))
        layout.add_column(ratio=2)
        layout.add_column(ratio=1)
        layout.add_row(_top_findings(data), Group(_analyst_focus(data), Text(""), _next(data)))
        body.append(layout)
    else:
        body.extend((_top_findings(data), Text(""), _analyst_focus(data), Text(""), _next(data)))
    body.extend((Text(""), Text("Analysis complete. Full evidence remains in the local HTML report. Source unchanged.", style=f"bold {SUCCESS}")))
    return Align.left(Group(*body), width=width, pad=False)


__all__ = ["DashboardData", "analyze_dashboard", "render_dashboard"]
