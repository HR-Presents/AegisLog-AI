from __future__ import annotations

import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

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
    INCIDENT,
    INFO,
    MUTED,
    SUCCESS,
    WARNING,
    risk_style,
    severity_text,
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


def analyze_dashboard(path: Path, *, timestamp_year_hint: int | None = None) -> DashboardData:
    """Build one complete, local-only analysis snapshot for terminal rendering.

    ``timestamp_year_hint`` is explicit operator context for RFC3164-style timestamps
    that omit a year. It is forwarded to the detection engine and is never inferred
    from the current clock.
    """
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
    )


def _risk_state(data: DashboardData) -> str:
    if data.severities.get("CRITICAL", 0):
        return "CRITICAL"
    if data.severities.get("HIGH", 0):
        return "HIGH"
    if data.severities.get("MEDIUM", 0):
        return "REVIEW"
    return "CLEAR"


def _header(data: DashboardData) -> Panel:
    risk = _risk_state(data)
    body = Text()
    body.append("AEGISLOG", style=f"bold {ACCENT}")
    body.append("  /  INVESTIGATION", style="bold white")
    body.append(f"  v{__version__}", style=MUTED)
    body.append("\n")
    body.append("SOURCE  ", style=MUTED)
    body.append(data.source, style="white")
    body.append("\n")
    body.append("POSTURE  ", style=MUTED)
    body.append(risk, style=f"bold {risk_style(risk)}")
    body.append("    EVENTS  ", style=MUTED)
    body.append(f"{data.lines:,}", style=f"bold {ACCENT}")
    body.append("    LOCAL / READ-ONLY", style=MUTED)
    return Panel(body, border_style=ACCENT_SOFT, padding=(0, 1))


def _posture_table(data: DashboardData) -> Table:
    table = Table(
        title="INVESTIGATION SUMMARY",
        title_style=f"bold {ACCENT_SOFT}",
        expand=True,
        show_header=True,
        header_style=MUTED,
        border_style=ACCENT_SOFT,
        padding=(0, 1),
    )
    table.add_column("CRITICAL", justify="center")
    table.add_column("HIGH", justify="center")
    table.add_column("MEDIUM", justify="center")
    table.add_column("LOW", justify="center")
    table.add_column("FINDINGS", justify="center")
    table.add_column("INCIDENTS", justify="center")
    table.add_column("ANOMALIES", justify="center")
    table.add_row(
        Text(str(data.severities.get("CRITICAL", 0)), style="bold bright_red"),
        Text(str(data.severities.get("HIGH", 0)), style="bold bright_red"),
        Text(str(data.severities.get("MEDIUM", 0)), style=f"bold {WARNING}"),
        Text(str(data.severities.get("LOW", 0)), style=f"bold {INFO}"),
        Text(str(len(data.findings)), style="bold white"),
        Text(str(len(data.incidents)), style=f"bold {INCIDENT}"),
        Text(str(len(data.anomalies)), style=f"bold {ANOMALY}"),
    )
    return table


def _analyst_focus(data: DashboardData) -> Panel:
    risk = _risk_state(data)
    body = Text()
    body.append("PRIORITY  ", style=MUTED)
    body.append(risk, style=f"bold {risk_style(risk)}")

    if data.findings:
        top = sorted(
            data.findings,
            key=lambda item: (
                {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}.get(item.severity, 0),
                item.title,
            ),
            reverse=True,
        )[0]
        body.append("\nFOCUS     ", style=MUTED)
        body.append(top.title, style="bold white")
        body.append("\nACTION    ", style=MUTED)
        body.append(top.recommendation, style="white")
    else:
        body.append("\nFOCUS     ", style=MUTED)
        body.append("No elevated rule-backed findings retained", style=SUCCESS)
        body.append("\nACTION    ", style=MUTED)
        body.append("Review coverage and preserve original telemetry when required.", style="white")

    if data.incidents:
        incident = data.incidents[0]
        body.append("\nINCIDENT  ", style=MUTED)
        body.append(f"INC-{incident.id.upper()[:8]}", style=f"bold {INCIDENT}")
        body.append("  ", style=MUTED)
        body.append(incident.title, style="white")

    body.append("\n\nSignals are investigative evidence, not proof of compromise.", style=MUTED)
    return Panel(
        body,
        title=Text(" ANALYST FOCUS ", style=f"bold {risk_style(risk)}"),
        title_align="left",
        border_style=risk_style(risk),
        padding=(0, 1),
    )


def _incident_table(data: DashboardData, limit: int = 8) -> Table:
    table = Table(
        title=f"ACTIVE INCIDENTS  [{min(len(data.incidents), limit)}/{len(data.incidents)}]",
        title_style=f"bold {INCIDENT}",
        expand=True,
        border_style=ACCENT_SOFT,
        padding=(0, 1),
    )
    table.add_column("ID", width=15, style=INCIDENT, no_wrap=True)
    table.add_column("SEV", width=9)
    table.add_column("SIGNALS", width=8, justify="right", style=ACCENT)
    table.add_column("CATEGORY", width=18)
    table.add_column("SUMMARY", ratio=1, overflow="fold")
    for item in data.incidents[:limit]:
        table.add_row(
            f"INC-{item.id.upper()[:8]}",
            severity_text(item.severity),
            str(item.count),
            Text(item.category),
            Text(item.title),
        )
    if not data.incidents:
        table.add_row("-", "-", "0", "-", Text("No correlated incidents", style=MUTED))
    return table


def _finding_table(data: DashboardData, limit: int = 20) -> Table:
    table = Table(
        title=f"Detected findings  [{min(len(data.findings), limit)}/{len(data.findings)}]",
        title_style=f"bold {ACCENT}",
        expand=True,
        border_style=ACCENT_SOFT,
        padding=(0, 1),
    )
    table.add_column("SEV", width=9)
    table.add_column("CATEGORY", width=17)
    table.add_column("DETECTION", width=32)
    table.add_column("EVIDENCE", ratio=1, overflow="fold")
    for item in data.findings[:limit]:
        table.add_row(
            severity_text(item.severity),
            Text(item.category),
            Text(item.title),
            Text(item.evidence),
        )
    if not data.findings:
        table.add_row(
            "-",
            "-",
            Text("No rule-backed findings", style=SUCCESS),
            Text("No matching local detection rules", style=MUTED),
        )
    return table


def _anomaly_table(data: DashboardData, limit: int = 6) -> Table:
    table = Table(
        title=f"ANOMALY SIGNALS  [{min(len(data.anomalies), limit)}/{len(data.anomalies)}]",
        title_style=f"bold {ANOMALY}",
        expand=True,
        border_style=ACCENT_SOFT,
        padding=(0, 1),
    )
    table.add_column("SCORE", justify="right", width=8, style=ANOMALY)
    table.add_column("EVENT CLASS", width=28)
    table.add_column("REASON", ratio=1, overflow="fold")
    for item in data.anomalies[:limit]:
        table.add_row(f"{item.score:.1f}", Text(item.key), Text(item.reason))
    return table


def _telemetry_table(data: DashboardData) -> Table:
    table = Table(
        title="TELEMETRY CONTEXT",
        title_style=f"bold {ACCENT_SOFT}",
        expand=True,
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
        for index, (name, count) in enumerate(items):
            if index:
                text.append("   ", style=MUTED)
            text.append(str(name), style="white")
            text.append(f" {count}", style=ACCENT)
        return text

    table.add_row("CATEGORIES", render(data.categories))
    table.add_row("LOG LEVELS", render(data.levels))
    table.add_row("SERVICES", render(data.services))
    return table


def _next_steps(data: DashboardData) -> Panel:
    command = "AegisLog.exe" if getattr(sys, "frozen", False) else "aegislog"
    body = Text()
    body.append("REPORT  ", style=MUTED)
    body.append("HTML investigation report generated automatically", style=SUCCESS)
    body.append("\nNEXT    ", style=MUTED)
    body.append(f"{command} incidents <file>", style=ACCENT)
    if data.incidents:
        incident_id = f"INC-{data.incidents[0].id.upper()[:8]}"
        body.append("    ", style=MUTED)
        body.append(f"{command} investigate <file> {incident_id}", style=INCIDENT)
        body.append("    ", style=MUTED)
        body.append(f"{command} explain <file> {incident_id}", style=INFO)
    return Panel(
        body,
        title=Text(" FOLLOW-UP ", style=f"bold {ACCENT}"),
        title_align="left",
        border_style=ACCENT_SOFT,
        padding=(0, 1),
    )


def render_dashboard(data: DashboardData) -> RenderableType:
    """Return a prioritized SOC-style investigation dashboard."""
    sections: list[RenderableType] = [
        _header(data),
        _posture_table(data),
        _analyst_focus(data),
    ]
    if data.incidents:
        sections.append(_incident_table(data))
    sections.append(_finding_table(data))
    if data.anomalies:
        sections.append(_anomaly_table(data))
    sections.extend((_telemetry_table(data), _next_steps(data)))
    return Group(*sections)
