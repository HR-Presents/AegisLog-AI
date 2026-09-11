from __future__ import annotations

import re
import shlex
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from rich import box
from rich.align import Align
from rich.console import Group, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from . import __version__
from .anomaly import Anomaly, score_events
from .engine import Finding, analyze_lines
from .incidents import Incident, correlate
from .parsers import Event, parse_line
from .theme import (
    ACCENT,
    ACCENT_SOFT,
    ANOMALY,
    DIM,
    INCIDENT,
    INFO,
    MUTED,
    NEUTRAL,
    SUCCESS,
    CYAN,
    LIME,
    MAGENTA,
    ORANGE,
    VIOLET,
    risk_style,
    severity_style,
    severity_text,
)
from .terminal_charts import donut_chart, stacked_composition, vertical_histogram, wave_chart

_SEVERITY_RANK = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "INFO": 0}
_NARROW_DASHBOARD_BREAKPOINT = 72
_WIDE_DASHBOARD_BREAKPOINT = 104
_MAX_DASHBOARD_WIDTH = 144
_MAX_BAR_WIDTH = 24
_TIMESTAMP_PATTERNS = (
    re.compile(r"^(?P<label>\d{4}-\d{2}-\d{2}T\d{2}:\d{2})(?::\d{2})?"),
    re.compile(r"^(?P<label>[A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2})(?::\d{2})?"),
    re.compile(r"^(?P<label>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2})(?::\d{2})?"),
)


@dataclass(frozen=True)
class DashboardData:
    source: str
    lines: int
    findings: tuple[Finding, ...]
    anomalies: tuple[Anomaly, ...]
    incidents: tuple[Incident, ...]
    levels: dict[str, int]
    services: dict[str, int]
    categories: dict[str, int]
    severities: dict[str, int]
    events: tuple[Event, ...] = ()
    raw_lines: tuple[str, ...] = ()


def analyze_dashboard(path: Path, *, timestamp_year_hint: int | None = None) -> DashboardData:
    """Build one complete, local-only analysis snapshot for terminal rendering."""
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        lines = handle.readlines()

    events: list[Event] = [parse_line(line) for line in lines]
    findings = analyze_lines(lines, timestamp_year_hint=timestamp_year_hint)
    anomalies = score_events(events)
    incidents = correlate(findings)

    level_counts = Counter((event.level or "unknown").upper() for event in events if event.message)
    service_counts = Counter(event.service or "unknown" for event in events if event.message)
    category_counts = Counter(item.category for item in findings)
    severity_counts = Counter(item.severity for item in findings)

    return DashboardData(
        source=str(path),
        lines=len(lines),
        findings=tuple(findings),
        anomalies=tuple(anomalies),
        incidents=tuple(incidents),
        levels=dict(level_counts),
        services=dict(service_counts),
        categories=dict(category_counts),
        severities=dict(severity_counts),
        events=tuple(events),
        raw_lines=tuple(line.rstrip("\n") for line in lines),
    )


def _severity_rank(value: str) -> int:
    return _SEVERITY_RANK.get(value.upper(), 0)


def _risk_state(data: DashboardData) -> str:
    severities = set(data.severities)
    severities.update(item.severity for item in data.incidents)
    if "CRITICAL" in severities:
        return "CRITICAL"
    if "HIGH" in severities:
        return "HIGH"
    if "MEDIUM" in severities:
        return "REVIEW"
    return "CLEAR"


def _ordered_findings(data: DashboardData) -> list[Finding]:
    return sorted(data.findings, key=lambda item: (-_severity_rank(item.severity), item.category, item.title))


def _ordered_incidents(data: DashboardData) -> list[Incident]:
    return sorted(
        data.incidents,
        key=lambda item: (-_severity_rank(item.severity), -item.count, item.category, item.title),
    )


def _elevated_count(data: DashboardData) -> int:
    return sum(count for severity, count in data.severities.items() if _severity_rank(severity) >= _severity_rank("MEDIUM"))


def _shield_label() -> Text:
    mark = Text("/A\\", style=f"bold {ACCENT}")
    mark.append("  AEGISLOG", style=f"bold {NEUTRAL}")
    return mark


def _header(data: DashboardData) -> Panel:
    risk = _risk_state(data)
    source_name = Path(data.source).name or data.source
    grid = Table.grid(expand=True, padding=(0, 1))
    grid.add_column(ratio=1)
    grid.add_column(no_wrap=True)

    title = Text()
    title.append_text(_shield_label())
    title.append("  /  INVESTIGATION", style=f"bold {ACCENT}")
    status = Text()
    status.append(f"VERSION v{__version__}", style=MUTED)
    status.append("   POSTURE ", style=MUTED)
    status.append(risk, style=f"bold {risk_style(risk)}")
    grid.add_row(title, status)

    source = Text()
    source.append("SOURCE  ", style=MUTED)
    source.append(source_name, style=f"bold {NEUTRAL}")
    if data.source != source_name:
        source.append("\nPATH    ", style=MUTED)
        source.append(data.source, style=MUTED)
    mode = Text("LOCAL / READ-ONLY / DETERMINISTIC", style=MUTED)
    grid.add_row(source, mode)

    return Panel(
        grid,
        title=Text(" INVESTIGATION SUMMARY ", style=f"bold {ACCENT}"),
        title_align="left",
        box=box.ASCII,
        border_style=ACCENT_SOFT,
        padding=(0, 1),
    )


def _metric_cell(label: str, value: int | str, style: str, note: str = "") -> Text:
    cell = Text(justify="center")
    cell.append(label, style=MUTED)
    cell.append("\n")
    cell.append(str(value), style=f"bold {style}")
    if note:
        cell.append("\n")
        cell.append(note, style=MUTED)
    return cell


def _metric_strip(data: DashboardData, *, compact: bool = False) -> Panel:
    risk = _risk_state(data)
    metrics = (
        ("EVENTS", f"{data.lines:,}", ACCENT, "parsed input"),
        ("FINDINGS", len(data.findings), NEUTRAL, "rule-backed"),
        ("ELEVATED", _elevated_count(data), risk_style(risk), "medium+"),
        ("INCIDENTS", len(data.incidents), INCIDENT, "correlated"),
        ("ANOMALIES", len(data.anomalies), ANOMALY, "scored"),
    )
    if compact:
        table = Table.grid(expand=True, padding=(0, 1))
        table.add_column(ratio=1)
        table.add_column(ratio=1)
        for index in range(0, len(metrics), 2):
            left = _metric_cell(*metrics[index])
            right = _metric_cell(*metrics[index + 1]) if index + 1 < len(metrics) else Text("")
            table.add_row(left, right)
    else:
        table = Table.grid(expand=True, padding=(0, 1))
        for _ in metrics:
            table.add_column(ratio=1)
        table.add_row(*(_metric_cell(*metric) for metric in metrics))
    return Panel(
        table,
        title=Text(" SECURITY METRICS // INVESTIGATION TICKER ", style=f"bold {CYAN}"),
        title_align="left",
        box=box.ASCII,
        border_style=ACCENT_SOFT,
        padding=(0, 1),
    )


def _analyst_focus(data: DashboardData) -> Panel:
    risk = _risk_state(data)
    findings = _ordered_findings(data)
    incidents = _ordered_incidents(data)
    top_finding = findings[0] if findings else None
    top_incident = incidents[0] if incidents else None

    grid = Table.grid(expand=True, padding=(0, 1))
    grid.add_column(width=10, no_wrap=True)
    grid.add_column(ratio=1, overflow="fold")
    grid.add_row(Text("PRIORITY", style=MUTED), Text(risk, style=f"bold {risk_style(risk)}"))

    incident_first = bool(top_incident and (top_finding is None or _severity_rank(top_incident.severity) >= _severity_rank(top_finding.severity)))
    if incident_first and top_incident:
        incident_id = f"INC-{top_incident.id.upper()[:8]}"
        primary = Text(incident_id, style=f"bold {INCIDENT}")
        primary.append("  ")
        primary.append(top_incident.title, style=f"bold {NEUTRAL}")
        grid.add_row(Text("PRIMARY", style=MUTED), primary)
        grid.add_row(
            Text("ACTION", style=MUTED),
            Text("Review the correlated evidence chain with source, identity, host, and surrounding telemetry context.", style=NEUTRAL),
        )
        if top_finding:
            next_item = Text(top_finding.severity, style=f"bold {severity_style(top_finding.severity)}")
            next_item.append("  ")
            next_item.append(top_finding.title, style=NEUTRAL)
            grid.add_row(Text("NEXT", style=MUTED), next_item)
    elif top_finding:
        grid.add_row(Text("PRIMARY", style=MUTED), Text(top_finding.title, style=f"bold {NEUTRAL}"))
        grid.add_row(Text("ACTION", style=MUTED), Text(top_finding.recommendation, style=NEUTRAL))
        if top_incident:
            next_item = Text(f"INC-{top_incident.id.upper()[:8]}", style=f"bold {INCIDENT}")
            next_item.append("  ")
            next_item.append(top_incident.title, style=NEUTRAL)
            grid.add_row(Text("NEXT", style=MUTED), next_item)
        elif len(findings) > 1:
            next_finding = findings[1]
            next_item = Text(next_finding.severity, style=f"bold {severity_style(next_finding.severity)}")
            next_item.append("  ")
            next_item.append(next_finding.title, style=NEUTRAL)
            grid.add_row(Text("NEXT", style=MUTED), next_item)
    else:
        grid.add_row(Text("PRIMARY", style=MUTED), Text("No elevated rule-backed findings or correlated incidents retained", style=SUCCESS))
        grid.add_row(Text("ACTION", style=MUTED), Text("Review coverage and preserve original telemetry when required.", style=NEUTRAL))

    footer = Text("Signals are investigative evidence, not proof of compromise.", style=MUTED)
    return Panel(
        Group(grid, Text(""), footer),
        title=Text(" ANALYST FOCUS ", style=f"bold {risk_style(risk)}"),
        title_align="left",
        box=box.ASCII,
        border_style=risk_style(risk),
        padding=(0, 1),
    )


def _bar(value: int, maximum: int, width: int = _MAX_BAR_WIDTH) -> Text:
    maximum = max(maximum, 1)
    filled = 0 if value <= 0 else max(1, round((value / maximum) * width))
    filled = min(width, filled)
    bar = Text("#" * filled, style=ACCENT)
    bar.append("." * (width - filled), style=DIM)
    return bar


def _ranked_panel(title: str, values: dict[str, int], *, compact: bool = False, tone: str = ACCENT) -> Panel:
    items = sorted(values.items(), key=lambda item: (-item[1], item[0]))[:6]
    if not items:
        return Panel(
            Text("No data available for this dimension.", style=MUTED),
            title=Text(f" {title} ", style=f"bold {tone}"),
            title_align="left",
            box=box.ASCII,
            border_style=ACCENT_SOFT,
        )
    maximum = max(count for _, count in items)
    total = max(1, sum(values.values()))
    table = Table.grid(expand=True, padding=(0, 1))
    table.add_column(ratio=1, overflow="ellipsis")
    if not compact:
        table.add_column(width=18)
    table.add_column(width=10, justify="right")
    for name, count in items:
        cells: list[RenderableType] = [Text(str(name).upper(), style=NEUTRAL)]
        if not compact:
            cells.append(_bar(count, maximum, width=18))
        cells.append(Text(f"{count}  {count / total:>4.0%}", style=tone))
        table.add_row(*cells)
    return Panel(table, title=Text(f" {title} ", style=f"bold {tone}"), title_align="left", box=box.ASCII, border_style=ACCENT_SOFT, padding=(0, 1))


def _distribution_panel(data: DashboardData, *, compact: bool = False) -> Panel:
    rows: list[tuple[str, str, int, str]] = []
    severity_order = ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO")
    for severity in severity_order:
        count = data.severities.get(severity, 0)
        if count:
            rows.append(("SEVERITY", severity, count, severity_style(severity)))
    for category, count in sorted(data.categories.items(), key=lambda item: (-item[1], item[0]))[:5]:
        rows.append(("CATEGORY", category.upper(), count, ACCENT))
    if not rows:
        return Panel(
            Text("No finding distribution is available for this input.", style=SUCCESS),
            title=Text(" SECURITY DISTRIBUTION // SEVERITY DONUT ", style=f"bold {MAGENTA}"),
            title_align="left",
            box=box.ASCII,
            border_style=ACCENT_SOFT,
        )

    maximum = max(count for _, _, count, _ in rows)
    table = Table.grid(expand=True, padding=(0, 1))
    if compact:
        table.add_column(ratio=1, overflow="ellipsis")
        table.add_column(width=7, justify="right")
        for _, label, count, style in rows:
            table.add_row(Text(label, style=f"bold {style}"), Text(str(count), style=f"bold {style}"))
    else:
        table.add_column(width=10, style=MUTED, no_wrap=True)
        table.add_column(width=16, overflow="ellipsis")
        table.add_column(width=_MAX_BAR_WIDTH)
        table.add_column(width=7, justify="right")
        for dimension, label, count, style in rows:
            table.add_row(
                Text(dimension, style=MUTED),
                Text(label, style=f"bold {style}"),
                _bar(count, maximum),
                Text(str(count), style=f"bold {style}"),
            )
    composition = {severity: data.severities.get(severity, 0) for severity in severity_order}
    chart: RenderableType = stacked_composition(composition, width=28) if compact else donut_chart(composition)
    return Panel(
        Group(chart, Text(""), table),
        title=Text(" SECURITY DISTRIBUTION // SEVERITY DONUT CHART ", style=f"bold {MAGENTA}"),
        title_align="left",
        box=box.ASCII,
        border_style=MAGENTA,
        padding=(0, 1),
    )


def _timestamp_label(raw: str) -> str | None:
    stripped = raw.strip()
    for pattern in _TIMESTAMP_PATTERNS:
        match = pattern.match(stripped)
        if match:
            return match.group("label")
    return None


def _activity_panel(data: DashboardData, *, compact: bool = False) -> Panel | None:
    if not data.events:
        return None
    buckets: Counter[str] = Counter()
    for event in data.events:
        label = _timestamp_label(event.raw)
        if label:
            buckets[label] += 1
    timestamped = len(buckets) >= 2
    if timestamped:
        items = list(buckets.items())[-8:]
    else:
        size = max(1, (len(data.events) + 7) // 8)
        items = [(f"{start + 1}-{min(len(data.events), start + size)}", min(size, len(data.events) - start)) for start in range(0, len(data.events), size)][:8]
    if not items:
        return None
    return Panel(
        vertical_histogram(items, height=5 if compact else 7),
        title=Text(f" {'EVENT ACTIVITY // EVENT TREND' if timestamped else 'EVENT CADENCE // EVENT TREND'} ", style=f"bold {CYAN}"),
        subtitle=Text("timestamp buckets" if timestamped else "real event-position buckets", style=MUTED),
        title_align="left",
        box=box.ASCII,
        border_style=CYAN,
        padding=(0, 1),
    )


def _threat_wave_panel(data: DashboardData, *, compact: bool = False) -> Panel:
    weights = {"CRITICAL": 5.0, "ERROR": 4.0, "WARNING": 2.5, "WARN": 2.5, "INFO": 1.0, "DEBUG": 0.5}
    values = [weights.get((event.level or "INFO").upper(), 1.0) for event in data.events if event.message]
    if not values:
        values = [0.0]
    buckets = min(12, max(1, len(values)))
    size = max(1, (len(values) + buckets - 1) // buckets)
    energy = [sum(values[index : index + size]) for index in range(0, len(values), size)][:buckets]
    return Panel(
        wave_chart(energy, width=24 if compact else 48, height=5 if compact else 7, tone=MAGENTA),
        title=Text(" THREAT WAVE // EVENT ENERGY ", style=f"bold {MAGENTA}"),
        subtitle=Text("severity-weighted log activity", style=MUTED),
        title_align="left",
        box=box.ASCII,
        border_style=MAGENTA,
        padding=(0, 1),
    )


def _analysis_flow_panel(data: DashboardData) -> Panel:
    grid = Table.grid(expand=True, padding=(0, 1))
    for ratio in (2, 1, 2, 1, 2, 1, 2):
        grid.add_column(ratio=ratio, justify="center")
    grid.add_row(
        Text(f"INPUT\n{data.lines:,} events", style=f"bold {CYAN}", justify="center"),
        Text("━━▶", style=LIME),
        Text(f"SERVICES\n{len(data.services)} observed", style=f"bold {LIME}", justify="center"),
        Text("━━▶", style=ORANGE),
        Text(f"FINDINGS\n{len(data.findings)} detected", style=f"bold {ORANGE}", justify="center"),
        Text("━━▶", style=MAGENTA),
        Text(f"INCIDENTS\n{len(data.incidents)} correlated", style=f"bold {MAGENTA}", justify="center"),
    )
    return Panel(
        grid,
        title=Text(" INVESTIGATION FLOW // CORRELATION DIAGRAM ", style=f"bold {LIME}"),
        title_align="left",
        box=box.ASCII,
        border_style=LIME,
        padding=(0, 1),
    )


def _incident_table(data: DashboardData, limit: int = 8, *, compact: bool = False) -> Table:
    ordered = _ordered_incidents(data)
    table = Table(
        title=f"ACTIVE INCIDENTS  [{min(len(ordered), limit)}/{len(ordered)}]",
        title_style=f"bold {INCIDENT}",
        expand=True,
        box=box.ASCII,
        border_style=ACCENT_SOFT,
        padding=(0, 1),
        show_lines=False,
    )
    table.add_column("ID", width=14, style=INCIDENT, no_wrap=True)
    table.add_column("SEV", width=9)
    if compact:
        table.add_column("INCIDENT", ratio=1, overflow="fold")
    else:
        table.add_column("SIGNALS", width=8, justify="right", style=ACCENT)
        table.add_column("CATEGORY", width=16, overflow="ellipsis")
        table.add_column("SUMMARY", ratio=1, overflow="fold")
    for item in ordered[:limit]:
        incident_id = f"INC-{item.id.upper()[:8]}"
        if compact:
            detail = Text(item.title, style=NEUTRAL)
            detail.append("\n")
            detail.append(f"{item.count} signals / {item.category}", style=MUTED)
            table.add_row(incident_id, severity_text(item.severity), detail)
        else:
            table.add_row(incident_id, severity_text(item.severity), str(item.count), Text(item.category), Text(item.title))
    return table


def _evidence_preview(value: str, limit: int = 180) -> str:
    normalized = " ".join(value.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 1].rstrip() + "…"


def _finding_table(data: DashboardData, limit: int = 12, *, compact: bool = False) -> Table:
    ordered = _ordered_findings(data)
    table = Table(
        title=f"DETECTED FINDINGS  [{min(len(ordered), limit)}/{len(ordered)}]",
        title_style=f"bold {ACCENT}",
        expand=True,
        box=box.ASCII,
        border_style=ACCENT_SOFT,
        padding=(0, 1),
    )
    table.add_column("SEV", width=9)
    if compact:
        table.add_column("DETECTION / EVIDENCE", ratio=1, overflow="fold")
    else:
        table.add_column("CATEGORY", width=16)
        table.add_column("DETECTION", width=28)
        table.add_column("EVIDENCE PREVIEW", ratio=1, overflow="fold")
    for item in ordered[:limit]:
        if compact:
            detail = Text()
            detail.append(item.category.upper(), style=MUTED)
            detail.append("  ")
            detail.append(item.title, style=f"bold {NEUTRAL}")
            detail.append("\n")
            detail.append(_evidence_preview(item.evidence, limit=120), style=MUTED)
            table.add_row(severity_text(item.severity), detail)
        else:
            table.add_row(severity_text(item.severity), Text(item.category), Text(item.title), Text(_evidence_preview(item.evidence)))
    if not ordered:
        if compact:
            table.add_row("-", Text("No rule-backed findings\nNo matching local detection rules", style=SUCCESS))
        else:
            table.add_row("-", "-", Text("No rule-backed findings", style=SUCCESS), Text("No matching local detection rules", style=MUTED))
    return table


def _timeline_panel(data: DashboardData, limit: int = 10, *, compact: bool = False) -> Panel | None:
    if not data.events:
        return None
    rows: list[tuple[int, str, Event]] = []
    for line_no, event in enumerate(data.events, start=1):
        if not event.message:
            continue
        timestamp = _timestamp_label(event.raw)
        if timestamp is None:
            continue
        rows.append((line_no, timestamp, event))
    if len(rows) < 2:
        return None
    interesting = [row for row in rows if (row[2].level or "").lower() in {"critical", "error", "warning"}]
    selected = interesting[:limit] if len(interesting) >= 2 else rows[:limit]
    table = Table(expand=True, box=box.ASCII, border_style=ACCENT_SOFT, padding=(0, 1))
    table.add_column("TIME", width=18 if not compact else 13, style=MUTED, no_wrap=True)
    table.add_column("LEVEL", width=9, no_wrap=True)
    if not compact:
        table.add_column("SOURCE", width=14, overflow="ellipsis")
    table.add_column("EVENT", ratio=1, overflow="fold")
    for line_no, timestamp, event in selected:
        level = (event.level or "INFO").upper()
        cells: list[RenderableType] = [Text(timestamp), Text(level, style=severity_style(level))]
        if not compact:
            cells.append(Text(event.service or event.source or "unknown", style=MUTED))
        message = Text(event.message, style=NEUTRAL)
        message.append(f"  [line {line_no}]", style=MUTED)
        cells.append(message)
        table.add_row(*cells)
    return Panel(
        table,
        title=Text(" INVESTIGATION TIMELINE ", style=f"bold {ACCENT}"),
        title_align="left",
        box=box.ASCII,
        border_style=ACCENT_SOFT,
        padding=(0, 0),
    )


def _anomaly_table(data: DashboardData, limit: int = 6, *, compact: bool = False) -> Table:
    table = Table(
        title=f"ANOMALY SIGNALS  [{min(len(data.anomalies), limit)}/{len(data.anomalies)}]",
        title_style=f"bold {ANOMALY}",
        expand=True,
        box=box.ASCII,
        border_style=ACCENT_SOFT,
        padding=(0, 1),
    )
    table.add_column("SCORE", justify="right", width=8, style=ANOMALY)
    if compact:
        table.add_column("SIGNAL", ratio=1, overflow="fold")
    else:
        table.add_column("EVENT CLASS", width=26)
        table.add_column("REASON", ratio=1, overflow="fold")
    for item in data.anomalies[:limit]:
        if compact:
            detail = Text(item.key)
            detail.append("\n")
            detail.append(item.reason, style=MUTED)
            table.add_row(f"{item.score:.1f}", detail)
        else:
            table.add_row(f"{item.score:.1f}", Text(item.key), Text(item.reason))
    return table


def _telemetry_table(data: DashboardData, *, compact: bool = False) -> Table:
    table = Table(
        title="TELEMETRY CONTEXT",
        title_style=f"bold {ACCENT}",
        expand=True,
        box=box.ASCII,
        border_style=ACCENT_SOFT,
        padding=(0, 1),
    )
    table.add_column("TYPE", width=14, style=MUTED)
    table.add_column("TOP VALUES", ratio=1)

    def render(values: dict[str, int], limit: int = 5) -> Text:
        text = Text()
        items = sorted(values.items(), key=lambda item: (-item[1], item[0]))[:limit]
        if not items:
            text.append("none", style=MUTED)
            return text
        maximum = max(count for _, count in items)
        for index, (name, count) in enumerate(items):
            if index:
                text.append("   " if not compact else "\n", style=MUTED)
            text.append(str(name), style=NEUTRAL)
            text.append(f" {count}", style=f"bold {ACCENT}")
            if not compact:
                width = max(1, round((count / maximum) * 6))
                text.append(" " + "#" * width, style=ACCENT_SOFT)
        return text

    table.add_row("CATEGORIES", render(data.categories))
    table.add_row("LOG LEVELS", render(data.levels))
    table.add_row("SERVICES", render(data.services))
    return table


def _raw_evidence_panel(data: DashboardData, limit: int = 10, *, compact: bool = False) -> Panel | None:
    raw_lines = data.raw_lines or tuple(event.raw for event in data.events)
    if not raw_lines:
        return None
    finding_evidence = {item.evidence.strip() for item in data.findings if item.evidence.strip()}
    selected: list[tuple[int, str]] = []
    for line_no, raw in enumerate(raw_lines, start=1):
        if raw.strip() in finding_evidence:
            selected.append((line_no, raw))
        if len(selected) >= limit:
            break
    if not selected:
        selected = [(line_no, raw) for line_no, raw in enumerate(raw_lines[:limit], start=1) if raw.strip()]
    if not selected:
        return None
    table = Table(expand=True, box=None, padding=(0, 1))
    table.add_column("LINE", width=6, justify="right", style=MUTED)
    if not compact:
        table.add_column("TIME", width=18, style=MUTED, no_wrap=True)
    table.add_column("RAW LOG EVIDENCE", ratio=1, overflow="fold")
    for line_no, raw in selected:
        cells: list[RenderableType] = [Text(str(line_no), style=MUTED)]
        if not compact:
            cells.append(Text(_timestamp_label(raw) or "-", style=MUTED))
        cells.append(Text(raw, style=NEUTRAL))
        table.add_row(*cells)
    return Panel(
        table,
        title=Text(" RAW EVIDENCE ", style=f"bold {ACCENT}"),
        subtitle=Text("source preserved / read-only", style=MUTED),
        title_align="left",
        box=box.ASCII,
        border_style=ACCENT_SOFT,
        padding=(0, 0),
    )


def _source_argument(source: str) -> str:
    if sys.platform == "win32" or getattr(sys, "frozen", False):
        return f'"{source.replace(chr(34), chr(34) * 2)}"'
    return shlex.quote(source)


def _next_steps(data: DashboardData) -> Panel:
    command = "AegisLog.exe" if getattr(sys, "frozen", False) else "aegislog"
    source = _source_argument(data.source)
    incidents = _ordered_incidents(data)
    grid = Table.grid(expand=True, padding=(0, 1))
    grid.add_column(width=9, no_wrap=True)
    grid.add_column(ratio=1, overflow="fold")
    grid.add_row(Text("REPORT", style=MUTED), Text("HTML investigation report generated automatically", style=SUCCESS))
    grid.add_row(Text("LIST", style=MUTED), Text(f"{command} incidents {source}", style=ACCENT))
    if incidents:
        incident_id = f"INC-{incidents[0].id.upper()[:8]}"
        grid.add_row(Text("OPEN", style=MUTED), Text(f"{command} investigate {source} {incident_id}", style=INCIDENT))
        grid.add_row(Text("EXPLAIN", style=MUTED), Text(f"{command} explain {source} {incident_id}", style=INFO))
    return Panel(
        grid,
        title=Text(" FOLLOW-UP / COPY-READY ", style=f"bold {ACCENT}"),
        title_align="left",
        box=box.ASCII,
        border_style=ACCENT_SOFT,
        padding=(0, 1),
    )


def _visual_analysis(data: DashboardData, *, screen_width: int, compact: bool) -> RenderableType:
    distribution = _distribution_panel(data, compact=compact)
    activity = _activity_panel(data, compact=compact)
    services = _ranked_panel("SERVICE LOAD", data.services, compact=compact, tone=VIOLET)
    if activity is None or screen_width < _WIDE_DASHBOARD_BREAKPOINT:
        return Group(distribution, *((Text(""), activity) if activity is not None else ()), Text(""), services)
    layout = Table.grid(expand=True, padding=(0, 1))
    layout.add_column(ratio=1)
    layout.add_column(ratio=1)
    layout.add_row(distribution, Group(activity, Text(""), services))
    return layout


def render_dashboard(data: DashboardData, *, screen_width: int | None = None) -> RenderableType:
    """Return a prioritized, responsive, data-aware terminal investigation command center."""
    width = min(screen_width if screen_width is not None else 100, _MAX_DASHBOARD_WIDTH)
    compact = width < _NARROW_DASHBOARD_BREAKPOINT
    sections: list[RenderableType] = [
        _header(data),
        Text(""),
        _metric_strip(data, compact=compact),
        Text(""),
        _visual_analysis(data, screen_width=width, compact=compact),
        Text(""),
        _threat_wave_panel(data, compact=compact),
        Text(""),
        _analysis_flow_panel(data),
        Text(""),
        _analyst_focus(data),
    ]
    timeline = _timeline_panel(data, compact=compact)
    if timeline is not None:
        sections.extend((Text(""), timeline))
    if data.incidents:
        sections.extend((Text(""), _incident_table(data, compact=compact)))
    sections.extend((Text(""), _finding_table(data, compact=compact)))
    if data.anomalies:
        sections.extend((Text(""), _anomaly_table(data, compact=compact)))
    sections.extend((Text(""), _telemetry_table(data, compact=compact)))
    raw = _raw_evidence_panel(data, compact=compact)
    if raw is not None:
        sections.extend((Text(""), raw))
    sections.extend((Text(""), _next_steps(data)))
    return Align.left(Group(*sections), width=width, pad=False)
