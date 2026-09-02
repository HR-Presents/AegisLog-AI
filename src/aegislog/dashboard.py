from __future__ import annotations

import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from rich.align import Align
from rich.columns import Columns
from rich.console import Group, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from . import __version__
from .anomaly import Anomaly, score_events
from .engine import Finding, analyze_lines
from .incidents import Incident, correlate
from .parsers import Event, parse_line
from .theme import ACCENT, ACCENT_SOFT, ANOMALY, INCIDENT, INFO, MUTED, SUCCESS, WARNING, risk_style, severity_text


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


def analyze_dashboard(path: Path) -> DashboardData:
    """Build one complete, local-only analysis snapshot for terminal rendering."""
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        lines = handle.readlines()

    events: list[Event] = [parse_line(line) for line in lines]
    findings = analyze_lines(lines)
    anomalies = score_events(events)
    incidents = correlate(findings)

    level_counts = Counter((event.level or "unknown").upper() for event in events if event.message)
    service_counts = Counter(event.service or "unknown" for event in events if event.message)
    category_counts = Counter(item.category for item in findings)
    severity_counts = Counter(item.severity for item in findings)

    return DashboardData(
        source=str(path), lines=len(lines), findings=tuple(findings), anomalies=tuple(anomalies),
        incidents=tuple(incidents), levels=dict(level_counts), services=dict(service_counts),
        categories=dict(category_counts), severities=dict(severity_counts),
    )


def _metric(title: str, value: str, subtitle: str = "", *, value_style: str = "bold", border_style: str = ACCENT_SOFT) -> Panel:
    body = Text(value, justify="center", style=value_style)
    if subtitle:
        body.append(f"\n{subtitle}", style=MUTED)
    return Panel(Align.center(body), title=title, title_align="left", border_style=border_style, padding=(0, 1))


def _severity_table(data: DashboardData) -> Table:
    table = Table(title="Severity breakdown", title_style=f"bold {ACCENT}", expand=True, border_style=ACCENT_SOFT)
    table.add_column("Severity", style="bold")
    table.add_column("Count", justify="right", style=ACCENT)
    for severity in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"):
        table.add_row(severity_text(severity), str(data.severities.get(severity, 0)))
    return table


def _top_table(title: str, values: dict[str, int], limit: int = 8) -> Table:
    table = Table(title=title, title_style=f"bold {ACCENT}", expand=True, border_style=ACCENT_SOFT)
    table.add_column("Name")
    table.add_column("Count", justify="right", style=ACCENT)
    for name, count in sorted(values.items(), key=lambda item: (-item[1], item[0]))[:limit]:
        table.add_row(Text(str(name)), str(count))
    if not values:
        table.add_row(Text("None", style=MUTED), "0")
    return table


def _incident_table(data: DashboardData, limit: int = 8) -> Table:
    table = Table(title="Correlated incidents", title_style=f"bold {INCIDENT}", expand=True, border_style=INCIDENT)
    table.add_column("Incident ID", width=16, style=INCIDENT)
    table.add_column("Severity", width=10)
    table.add_column("Category", width=18)
    table.add_column("Signals", justify="right", width=7, style=ACCENT)
    table.add_column("Incident summary")
    for item in data.incidents[:limit]:
        table.add_row(
            f"INC-{item.id.upper()[:8]}",
            severity_text(item.severity),
            Text(item.category),
            str(item.count),
            Text(item.title),
        )
    if not data.incidents:
        table.add_row("-", "-", "-", "0", Text("No correlated incidents", style=MUTED))
    return table


def _anomaly_table(data: DashboardData, limit: int = 8) -> Table:
    table = Table(title="High-signal anomalies", title_style=f"bold {ANOMALY}", expand=True, border_style=ANOMALY)
    table.add_column("Score", justify="right", width=7, style=ANOMALY)
    table.add_column("Event class", width=28)
    table.add_column("Reason")
    for item in data.anomalies[:limit]:
        table.add_row(f"{item.score:.1f}", Text(item.key), Text(item.reason))
    if not data.anomalies:
        table.add_row("-", "-", Text("No rare concerning event classes detected", style=MUTED))
    return table


def _finding_table(data: DashboardData, limit: int = 20) -> Table:
    table = Table(
        title=f"Detected findings — showing {min(len(data.findings), limit)} of {len(data.findings)}",
        title_style=f"bold {ACCENT}",
        expand=True,
        show_lines=True,
        border_style=ACCENT_SOFT,
    )
    table.add_column("Severity", width=10)
    table.add_column("Category", width=18)
    table.add_column("Finding", width=34)
    table.add_column("Evidence")
    for item in data.findings[:limit]:
        table.add_row(severity_text(item.severity), Text(item.category), Text(item.title), Text(item.evidence))
    if not data.findings:
        table.add_row("-", "-", Text("No rule-backed findings", style=SUCCESS), Text("No matching local detection rules", style=MUTED))
    return table


def _risk_state(data: DashboardData) -> str:
    if data.severities.get("CRITICAL", 0):
        return "CRITICAL"
    if data.severities.get("HIGH", 0):
        return "HIGH"
    if data.severities.get("MEDIUM", 0):
        return "REVIEW"
    return "CLEAR"


def _next_steps(data: DashboardData) -> Panel:
    command = "AegisLog.exe" if getattr(sys, "frozen", False) else "aegislog"
    text = Text("Signals are investigative evidence, not proof of compromise. ", style=MUTED)
    if data.incidents:
        incident_id = f"INC-{data.incidents[0].id.upper()[:8]}"
        text.append("Start with ", style="white")
        text.append(f"{command} incidents <file>", style=ACCENT)
        text.append(", then use ", style="white")
        text.append(f"{command} investigate <file> {incident_id}", style=INCIDENT)
        text.append(" or ", style="white")
        text.append(f"{command} explain <file> {incident_id}", style=INFO)
        text.append(" for the incident shown above. ", style="white")
    else:
        text.append("Use ", style="white")
        text.append(f"{command} incidents <file>", style=ACCENT)
        text.append(" to review correlated findings. ", style="white")
    text.append("Additional local review: ", style="white")
    text.append(f"{command} mitre <file>", style=WARNING)
    text.append(" and ", style="white")
    text.append(f"{command} intel-entities <file>", style=ACCENT)
    text.append(".", style="white")
    return Panel(text, title="Next steps", title_align="left", border_style=ACCENT)


def render_dashboard(data: DashboardData) -> RenderableType:
    """Return a rich terminal dashboard containing the full investigation summary."""
    critical = data.severities.get("CRITICAL", 0)
    high = data.severities.get("HIGH", 0)
    medium = data.severities.get("MEDIUM", 0)
    risk = _risk_state(data)

    header_text = Text(justify="center")
    header_text.append("AEGISLOG AI", style=f"bold {ACCENT}")
    header_text.append(f"  v{__version__}\n", style=MUTED)
    header_text.append(data.source, style="bold white")
    header = Panel(
        Align.center(header_text),
        border_style=ACCENT,
        subtitle="Defensive log intelligence • local analysis dashboard",
        subtitle_align="right",
    )

    metrics = Columns([
        _metric("Lines analyzed", f"{data.lines:,}", value_style=f"bold {ACCENT}"),
        _metric("Findings", str(len(data.findings)), f"{critical} critical • {high} high • {medium} medium", value_style="bold white"),
        _metric("Incidents", str(len(data.incidents)), value_style=f"bold {INCIDENT}", border_style=INCIDENT),
        _metric("Anomalies", str(len(data.anomalies)), value_style=f"bold {ANOMALY}", border_style=ANOMALY),
        _metric("Risk state", risk, value_style=f"bold {risk_style(risk)}", border_style=risk_style(risk)),
    ], equal=True, expand=True)
    overview = Columns([
        _severity_table(data), _top_table("Finding categories", data.categories),
        _top_table("Parsed log levels", data.levels), _top_table("Top services", data.services),
    ], equal=True, expand=True)
    return Group(header, metrics, overview, _incident_table(data), _anomaly_table(data), _finding_table(data), _next_steps(data))
