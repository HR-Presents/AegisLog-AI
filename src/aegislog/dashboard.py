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
    title = Text()
    title.append("AEGISLOG AI", style=f"bold {ACCENT}")
    title.append(" // ANALYSIS", style="bold white")
    title.append(f"  v{__version__}", style=MUTED)

    metadata = Text()
    metadata.append("TARGET  ", style=MUTED)
    metadata.append(data.source, style="bold white")
    metadata.append("\nEVENTS  ", style=MUTED)
    metadata.append(f"{data.lines:,}", style=ACCENT)
    metadata.append("    STATE  ", style=MUTED)
    metadata.append(f"● {risk}", style=f"bold {risk_style(risk)}")
    return Panel(Text.assemble(title, "\n", metadata), border_style=ACCENT_SOFT, padding=(0, 1))


def _posture_table(data: DashboardData) -> Table:
    table = Table(
        title="THREAT POSTURE",
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
        severity_text(str(data.severities.get("CRITICAL", 0))),
        Text(str(data.severities.get("HIGH", 0)), style="bold bright_red"),
        Text(str(data.severities.get("MEDIUM", 0)), style=f"bold {WARNING}"),
        Text(str(data.severities.get("LOW", 0)), style=f"bold {INFO}"),
        Text(str(len(data.findings)), style="bold white"),
        Text(str(len(data.incidents)), style=f"bold {INCIDENT}"),
        Text(str(len(data.anomalies)), style=f"bold {ANOMALY}"),
    )
    return table


def _incident_table(data: DashboardData, limit: int = 8) -> Table:
    table = Table(
        title="ACTIVE INCIDENTS",
        title_style=f"bold {INCIDENT}",
        expand=True,
        border_style=ACCENT_SOFT,
        padding=(0, 1),
    )
    table.add_column("ID", width=15, style=INCIDENT, no_wrap=True)
    table.add_column("SEV", width=9)
    table.add_column("SIGNALS", width=8, justify="right", style=ACCENT)
    table.add_column("CATEGORY", width=18)
    table.add_column("SUMMARY")
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


def _anomaly_table(data: DashboardData, limit: int = 8) -> Table:
    table = Table(
        title="ANOMALY FEED",
        title_style=f"bold {ANOMALY}",
        expand=True,
        border_style=ACCENT_SOFT,
        padding=(0, 1),
    )
    table.add_column("SCORE", justify="right", width=8, style=ANOMALY)
    table.add_column("EVENT CLASS", width=30)
    table.add_column("REASON")
    for item in data.anomalies[:limit]:
        table.add_row(f"{item.score:.1f}", Text(item.key), Text(item.reason))
    if not data.anomalies:
        table.add_row("-", "-", Text("No rare concerning event classes detected", style=MUTED))
    return table


def _finding_table(data: DashboardData, limit: int = 20) -> Table:
    table = Table(
        title=f"FINDINGS  [{min(len(data.findings), limit)}/{len(data.findings)}]",
        title_style=f"bold {ACCENT}",
        expand=True,
        border_style=ACCENT_SOFT,
        padding=(0, 1),
    )
    table.add_column("SEV", width=9)
    table.add_column("CATEGORY", width=18)
    table.add_column("DETECTION", width=34)
    table.add_column("EVIDENCE")
    for item in data.findings[:limit]:
        table.add_row(severity_text(item.severity), Text(item.category), Text(item.title), Text(item.evidence))
    if not data.findings:
        table.add_row(
            "-",
            "-",
            Text("No rule-backed findings", style=SUCCESS),
            Text("No matching local detection rules", style=MUTED),
        )
    return table


def _telemetry_table(data: DashboardData) -> Table:
    table = Table(
        title="TELEMETRY SNAPSHOT",
        title_style=f"bold {ACCENT_SOFT}",
        expand=True,
        border_style=ACCENT_SOFT,
        padding=(0, 1),
    )
    table.add_column("TYPE", width=14, style=MUTED)
    table.add_column("TOP VALUES")

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
    text = Text()
    text.append("analyst › ", style=f"bold {ACCENT}")
    text.append(f"{command} incidents <file>", style=ACCENT)
    if data.incidents:
        incident_id = f"INC-{data.incidents[0].id.upper()[:8]}"
        text.append("    |    ", style=MUTED)
        text.append(f"{command} investigate <file> {incident_id}", style=INCIDENT)
        text.append("    |    ", style=MUTED)
        text.append(f"{command} explain <file> {incident_id}", style=INFO)
    text.append("\nSignals are investigative evidence, not proof of compromise.", style=MUTED)
    return Panel(text, border_style=ACCENT_SOFT, padding=(0, 1))


def render_dashboard(data: DashboardData) -> RenderableType:
    """Return a compact SOC-style terminal investigation dashboard."""
    return Group(
        _header(data),
        _posture_table(data),
        _incident_table(data),
        _anomaly_table(data),
        _finding_table(data),
        _telemetry_table(data),
        _next_steps(data),
    )
