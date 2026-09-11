from __future__ import annotations

from collections import Counter
from pathlib import Path

from rich import box
from rich.align import Align
from rich.console import Group, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .dashboard import DashboardData, analyze_dashboard
from .theme import ACCENT, ACCENT_SOFT, INCIDENT, MUTED, NEUTRAL, SUCCESS, WARNING, severity_style

_MAX_WIDTH = 118
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


def _panel(content: RenderableType, title: Text | None = None, *, padding: tuple[int, int] = (0, 1), width: int | None = None) -> Panel:
    return Panel(
        content,
        title=title,
        title_align="left",
        box=box.ASCII,
        border_style=ACCENT_SOFT,
        padding=padding,
        width=width,
    )


def _header(data: DashboardData, width: int) -> Panel:
    grid = Table.grid(expand=True, padding=(0, 1))
    grid.add_column(ratio=1)
    grid.add_column(no_wrap=True)
    title = Text("AEGISLOG", style=f"bold {NEUTRAL}")
    title.append("  //  ANALYZE", style=f"bold {ACCENT}")
    grid.add_row(title, Text("ANALYSIS COMPLETE", style=f"bold {SUCCESS}"))
    grid.add_row(
        Text("LOCAL-FIRST  |  READ-ONLY  |  DETERMINISTIC", style=MUTED),
        Text(f"POSTURE  {_risk(data)}", style=WARNING if _risk(data) != "CLEAR" else SUCCESS),
    )
    grid.add_row(Text("HR-PRESENTS", style=f"bold {ACCENT}"), Text("SOURCE UNCHANGED", style=MUTED))
    return _panel(grid, width=width)


def _metric_cards(data: DashboardData) -> Panel:
    elevated = sum(1 for item in data.findings if _rank(item.severity) >= _rank("MEDIUM"))
    entries = (
        ("EVENTS", data.lines, ACCENT),
        ("FINDINGS", len(data.findings), WARNING if data.findings else NEUTRAL),
        ("ELEVATED", elevated, WARNING if elevated else NEUTRAL),
        ("INCIDENTS", len(data.incidents), INCIDENT if data.incidents else NEUTRAL),
        ("ANOMALIES", len(data.anomalies), NEUTRAL),
    )
    table = Table.grid(expand=True, padding=(0, 1))
    for _ in entries:
        table.add_column(ratio=1)
    cells = []
    for label, value, style in entries:
        cell = Text(justify="center")
        cell.append(label, style=MUTED)
        cell.append("\n")
        cell.append(str(value), style=f"bold {style}")
        cells.append(cell)
    table.add_row(*cells)
    return _panel(table, Text(" INVESTIGATION PULSE ", style=f"bold {ACCENT}"))


def _source_block(data: DashboardData) -> Panel:
    source_name = Path(data.source).name or data.source
    grid = Table.grid(expand=True, padding=(0, 1))
    grid.add_column(width=9, no_wrap=True)
    grid.add_column(ratio=1, overflow="fold")
    grid.add_row(Text("SOURCE", style=f"bold {ACCENT}"), Text(source_name, style=NEUTRAL))
    grid.add_row(Text("PATH", style=MUTED), Text(data.source, style=MUTED, overflow="fold"))
    return _panel(grid, Text(" SOURCE CONTEXT ", style=f"bold {ACCENT}"))


def _severity_chart(data: DashboardData) -> Panel:
    values = Counter(item.severity for item in data.findings)
    total = max(1, sum(values.values()))
    maximum = max(values.values(), default=1)
    table = Table.grid(expand=True, padding=(0, 1))
    table.add_column(width=10)
    table.add_column(ratio=1)
    table.add_column(width=10, justify="right")
    for label in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"):
        count = values.get(label, 0)
        if not count:
            continue
        bar_width = 18
        filled = max(1, round((count / maximum) * bar_width))
        bar = Text("=" * filled, style=severity_style(label))
        table.add_row(Text(label, style=severity_style(label)), bar, Text(f"{count}  {count / total * 100:.0f}%", style=MUTED))
    if not values:
        table.add_row(Text("CLEAR", style=SUCCESS), Text("No retained findings", style=MUTED), Text("0", style=MUTED))
    return _panel(table, Text(" SEVERITY PROFILE ", style=f"bold {ACCENT}"))


def _top_findings(data: DashboardData, limit: int = 4) -> Panel:
    ordered = sorted(data.findings, key=lambda item: (-_rank(item.severity), item.category, item.title))
    body: list[RenderableType] = []
    if not ordered:
        body.append(Text("No rule-backed findings retained.", style=SUCCESS))
    for index, item in enumerate(ordered[:limit]):
        if index:
            body.append(Text(""))
        line = Text()
        line.append(f"{item.severity:<8}", style=f"bold {severity_style(item.severity)}")
        line.append(item.title, style=f"bold {NEUTRAL}")
        line.append("\n          ")
        line.append(" ".join(item.evidence.split()), style=MUTED)
        body.append(line)
    if len(ordered) > limit:
        body.append(Text(f"\n+ {len(ordered) - limit} more in the local report", style=MUTED))
    return _panel(Group(*body), Text(" PRIORITY FINDINGS ", style=f"bold {ACCENT}"))


def _investigation_focus(data: DashboardData) -> Panel:
    incidents = sorted(data.incidents, key=lambda item: (-_rank(item.severity), -item.count, item.title))
    findings = sorted(data.findings, key=lambda item: (-_rank(item.severity), item.title))
    grid = Table.grid(expand=True, padding=(0, 1))
    grid.add_column(width=9, no_wrap=True)
    grid.add_column(ratio=1, overflow="fold")
    if incidents:
        item = incidents[0]
        primary = Text(f"INC-{item.id.upper()[:8]}", style=f"bold {INCIDENT}")
        primary.append("  " + item.title, style=NEUTRAL)
        grid.add_row(Text("FOCUS", style=f"bold {ACCENT}"), primary)
        grid.add_row(Text("ACTION", style=MUTED), Text("Review correlated evidence and surrounding telemetry.", style=NEUTRAL))
    elif findings:
        item = findings[0]
        grid.add_row(Text("FOCUS", style=f"bold {ACCENT}"), Text(item.title, style=NEUTRAL))
        grid.add_row(Text("ACTION", style=MUTED), Text(item.recommendation, style=NEUTRAL))
    else:
        grid.add_row(Text("FOCUS", style=f"bold {ACCENT}"), Text("No elevated investigation target", style=SUCCESS))
        grid.add_row(Text("ACTION", style=MUTED), Text("Preserve telemetry and review coverage as needed.", style=NEUTRAL))
    return _panel(grid, Text(" INVESTIGATION FOCUS ", style=f"bold {ACCENT}"))


def _next(data: DashboardData) -> Panel:
    grid = Table.grid(expand=True, padding=(0, 1))
    grid.add_column(width=12, no_wrap=True)
    grid.add_column(ratio=1)
    grid.add_row(Text("incidents", style=f"bold {ACCENT}"), Text("View correlated incidents", style=MUTED))
    grid.add_row(Text("investigate", style=f"bold {ACCENT}"), Text("Open incident evidence", style=MUTED))
    grid.add_row(Text("report", style=f"bold {ACCENT}"), Text("Open full HTML investigation report", style=MUTED))
    return _panel(grid, Text(" NEXT ACTIONS ", style=f"bold {ACCENT}"))


def render_dashboard(data: DashboardData, *, screen_width: int | None = None) -> RenderableType:
    width = min(max(70, screen_width or 100), _MAX_WIDTH)
    body: list[RenderableType] = [_header(data, width), Text(""), _metric_cards(data), Text(""), _source_block(data), Text("")]
    if width >= 104:
        overview = Table.grid(expand=True, padding=(0, 2))
        overview.add_column(ratio=1)
        overview.add_column(ratio=1)
        overview.add_row(_severity_chart(data), _investigation_focus(data))
        body.extend((overview, Text("")))
        layout = Table.grid(expand=True, padding=(0, 2))
        layout.add_column(ratio=2)
        layout.add_column(ratio=1)
        layout.add_row(_top_findings(data), _next(data))
        body.append(layout)
    else:
        body.extend((_severity_chart(data), Text(""), _top_findings(data), Text(""), _investigation_focus(data), Text(""), _next(data)))
    body.extend((Text(""), Text("Analysis complete  |  evidence retained in local HTML report  |  source unchanged", style=MUTED)))
    return Align.left(Group(*body), width=width, pad=False)


__all__ = ["DashboardData", "analyze_dashboard", "render_dashboard"]
