from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from rich import box
from rich.console import Group, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .dashboard import DashboardData, analyze_dashboard
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
)

_MAX_WIDTH = 118
_WIDE = 96
_SEVERITY_RANK = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "INFO": 0}
_PALETTE = (ACCENT, SKY, SECONDARY, SUCCESS, WARNING, HIGH)
_TIMESTAMP = re.compile(r"^(?:\d{4}-\d{2}-\d{2}[T ](?P<iso>\d{2}:\d{2})|[A-Z][a-z]{2}\s+\d{1,2}\s+(?P<sys>\d{2}:\d{2}))")


def _rank(value: str) -> int:
    return _SEVERITY_RANK.get(value.upper(), 0)


def _risk(data: DashboardData) -> str:
    severities = {item.severity for item in data.findings}
    severities.update(item.severity for item in data.incidents)
    for name in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
        if name in severities:
            return "REVIEW" if name == "MEDIUM" else name
    return "CLEAR"


def _panel(body: RenderableType, title: str, tone: str = ACCENT, *, padding=(0, 1)) -> Panel:
    return Panel(
        body,
        title=Text(f" {title} ", style=f"bold {tone}"),
        title_align="left",
        box=box.ASCII,
        border_style=ACCENT_SOFT,
        padding=padding,
    )


def _header(data: DashboardData, width: int) -> Panel:
    left = Text()
    left.append("AEGISLOG", style=f"bold {ACCENT}")
    left.append("  //  ANALYZE  //  SECURITY INVESTIGATION", style=f"bold {NEUTRAL}")
    left.append("\nLOCAL-FIRST  READ-ONLY  DETERMINISTIC", style=MUTED)
    right = Text(justify="right")
    posture = _risk(data)
    right.append(
        f"POSTURE  {posture}",
        style=f"bold {severity_style(posture if posture != 'REVIEW' else 'MEDIUM')}",
    )
    right.append("\nHR-PRESENTS", style=ACCENT)
    grid = Table.grid(expand=True)
    grid.add_column(ratio=2)
    grid.add_column(ratio=1)
    grid.add_row(left, right)
    return Panel(grid, box=box.ASCII, border_style=ACCENT, padding=(0, 1), width=width)


def _kpis(data: DashboardData) -> Panel:
    elevated = sum(1 for item in data.findings if _rank(item.severity) >= _rank("MEDIUM"))
    values = (
        ("EVENTS", data.lines, ACCENT),
        ("FINDINGS", len(data.findings), WARNING if data.findings else NEUTRAL),
        ("ELEVATED", elevated, HIGH if elevated else SUCCESS),
        ("INCIDENTS", len(data.incidents), INCIDENT if data.incidents else NEUTRAL),
        ("ANOMALIES", len(data.anomalies), SECONDARY if data.anomalies else NEUTRAL),
    )
    grid = Table.grid(expand=True, padding=(0, 1))
    for _ in values:
        grid.add_column(ratio=1)
    cells = []
    for label, value, tone in values:
        cell = Text(justify="center")
        cell.append(label, style=MUTED)
        cell.append("\n")
        cell.append(str(value), style=f"bold {tone}")
        cells.append(cell)
    grid.add_row(*cells)
    return _panel(grid, "INVESTIGATION PULSE // LIVE TICKER", SKY)


def _bar(value: int, maximum: int, *, width: int = 16, tone: str = ACCENT) -> Text:
    maximum = max(1, maximum)
    filled = 0 if value <= 0 else max(1, round(value / maximum * width))
    out = Text("#" * min(width, filled), style=tone)
    out.append("." * max(0, width - filled), style="#45515a")
    return out


def _distribution(title: str, values: dict[str, int], *, semantic: bool = False, tone: str = ACCENT) -> Panel:
    items = sorted(values.items(), key=lambda item: (-item[1], str(item[0])))[:6]
    if not items:
        return _panel(Text("No retained activity", style=MUTED), title, tone)
    maximum = max(count for _, count in items)
    total = max(1, sum(values.values()))
    grid = Table.grid(expand=True, padding=(0, 1))
    grid.add_column(ratio=1, overflow="crop")
    grid.add_column(width=16)
    grid.add_column(width=8, justify="right")
    for index, (label, count) in enumerate(items):
        color = severity_style(str(label)) if semantic else _PALETTE[index % len(_PALETTE)]
        grid.add_row(
            Text(str(label).upper(), style=color),
            _bar(count, maximum, tone=color),
            Text(f"{count} {count / total * 100:.0f}%", style=MUTED),
        )
    return _panel(grid, title, tone)


def _activity(data: DashboardData) -> Panel:
    buckets: Counter[str] = Counter()
    for raw in data.raw_lines:
        match = _TIMESTAMP.match(raw.strip())
        if match:
            buckets[match.group("iso") or match.group("sys")] += 1
    items = list(buckets.items())[-12:]
    if len(items) < 2:
        # This is not a time axis. It is a deterministic histogram over real
        # input positions when timestamps are unavailable.
        total = len(data.raw_lines)
        if total:
            size = max(1, (total + 7) // 8)
            items = [
                (f"{start + 1}-{min(total, start + size)}", min(size, total - start))
                for start in range(0, total, size)
            ][:8]
    if not items:
        return _panel(Text("No event activity available", style=MUTED), "EVENT TREND", SKY)
    maximum = max(value for _, value in items)
    chart_height = 5
    cols = [max(1, round(value / maximum * chart_height)) for _, value in items]
    lines: list[Text] = []
    for row in range(chart_height, 0, -1):
        line = Text()
        for index, height in enumerate(cols):
            line.append(
                "##" if height >= row else "  ",
                style=_PALETTE[index % len(_PALETTE)] if height >= row else MUTED,
            )
            line.append(" ")
        lines.append(line)
    labels = Text(
        " ".join(label[-5:].center(2) for label, _ in items),
        style=MUTED,
        overflow="crop",
        no_wrap=True,
    )
    return _panel(
        Group(*lines, labels, Text(f"real events / {len(items)} latest buckets", style=MUTED)),
        "EVENT TREND",
        SKY,
    )


def _focus(data: DashboardData) -> Panel:
    incidents = sorted(data.incidents, key=lambda item: (-_rank(item.severity), -item.count, item.title))
    findings = sorted(data.findings, key=lambda item: (-_rank(item.severity), item.category, item.title))
    grid = Table.grid(expand=True, padding=(0, 1))
    grid.add_column(width=9, no_wrap=True)
    grid.add_column(ratio=1, overflow="fold")
    if incidents:
        item = incidents[0]
        grid.add_row(
            Text("PRIMARY", style=MUTED),
            Text(f"INC-{item.id.upper()[:8]}  {item.title}", style=f"bold {INCIDENT}"),
        )
        grid.add_row(
            Text("ACTION", style=MUTED),
            Text(
                "Review correlated evidence and surrounding source, account, host, and time context.",
                style=NEUTRAL,
            ),
        )
    elif findings:
        item = findings[0]
        grid.add_row(Text("PRIMARY", style=MUTED), Text(item.title, style=f"bold {severity_style(item.severity)}"))
        grid.add_row(Text("ACTION", style=MUTED), Text(item.recommendation, style=NEUTRAL))
    else:
        grid.add_row(Text("PRIMARY", style=MUTED), Text("No elevated investigation target", style=SUCCESS))
        grid.add_row(Text("ACTION", style=MUTED), Text("Preserve telemetry and review detection coverage.", style=NEUTRAL))
    return _panel(grid, "ANALYST FOCUS", HIGH if data.findings else SUCCESS)


def _findings(data: DashboardData) -> Panel:
    ordered = sorted(data.findings, key=lambda item: (-_rank(item.severity), item.category, item.title))[:5]
    table = Table(expand=True, box=None, padding=(0, 1))
    table.add_column("SEV", width=8)
    table.add_column("CATEGORY", width=14, overflow="crop")
    table.add_column("DETECTION / EVIDENCE", ratio=1, overflow="fold")
    for item in ordered:
        detail = Text(item.title, style=f"bold {NEUTRAL}")
        detail.append("\n")
        detail.append(" ".join(item.evidence.split()), style=MUTED)
        table.add_row(
            Text(item.severity, style=f"bold {severity_style(item.severity)}"),
            Text(item.category.upper(), style=SKY),
            detail,
        )
    if not ordered:
        table.add_row("-", "-", Text("No rule-backed findings retained", style=SUCCESS))
    return _panel(table, "LIVE EVIDENCE BOARD", WARNING, padding=(0, 0))


def _source(data: DashboardData) -> Panel:
    grid = Table.grid(expand=True, padding=(0, 1))
    grid.add_column(width=10, no_wrap=True)
    grid.add_column(ratio=1, overflow="fold")
    grid.add_row(Text("SOURCE", style=MUTED), Text(Path(data.source).name or data.source, style=f"bold {ACCENT}"))
    grid.add_row(Text("PATH", style=MUTED), Text(data.source, style=MUTED))
    grid.add_row(Text("HANDLING", style=MUTED), Text("LOCAL / READ-ONLY / SOURCE UNCHANGED", style=SUCCESS))
    return _panel(grid, "SOURCE PROFILE", ACCENT)


def render_dashboard(data: DashboardData, *, screen_width: int | None = None) -> RenderableType:
    width = min(max(68, screen_width or 100), _MAX_WIDTH)
    wide = width >= _WIDE
    sections: list[RenderableType] = [_header(data, width), Text(""), _kpis(data), Text("")]

    if wide:
        top = Table.grid(expand=True, padding=(0, 1))
        top.add_column(ratio=1)
        top.add_column(ratio=1)
        top.add_row(
            _activity(data),
            _distribution("SEVERITY MIX", data.severities, semantic=True, tone=WARNING),
        )
        sections.extend((top, Text("")))

        middle = Table.grid(expand=True, padding=(0, 1))
        middle.add_column(ratio=1)
        middle.add_column(ratio=1)
        middle.add_row(
            _distribution("SERVICE LOAD", data.services, tone=SKY),
            _distribution("FINDING CATEGORIES", data.categories, tone=SECONDARY),
        )
        sections.extend((middle, Text("")))
    else:
        sections.extend(
            (
                _activity(data),
                Text(""),
                _distribution("SEVERITY MIX", data.severities, semantic=True, tone=WARNING),
                Text(""),
                _distribution("SERVICE LOAD", data.services, tone=SKY),
                Text(""),
                _distribution("FINDING CATEGORIES", data.categories, tone=SECONDARY),
                Text(""),
            )
        )

    sections.extend(
        (
            _focus(data),
            Text(""),
            _findings(data),
            Text(""),
            _source(data),
            Text(""),
            Text(
                "REPORT: generated locally  |  INCIDENTS: correlated from retained findings  |  SOURCE: unchanged",
                style=MUTED,
            ),
        )
    )

    # A single fixed-width container constrains every expand=True child panel.
    # Do not center inside a wider console here: left padding becomes part of
    # the physical line length and breaks Windows width guarantees.
    frame = Table.grid(width=width, padding=0)
    frame.add_column(width=width)
    for section in sections:
        frame.add_row(section)
    return frame


__all__ = ["DashboardData", "analyze_dashboard", "render_dashboard"]
