from __future__ import annotations

import shlex
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
    risk_style,
    severity_text,
)

_SEVERITY_RANK = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "INFO": 0}


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
    return sorted(
        data.findings,
        key=lambda item: (-_severity_rank(item.severity), item.category, item.title),
    )


def _ordered_incidents(data: DashboardData) -> list[Incident]:
    return sorted(
        data.incidents,
        key=lambda item: (-_severity_rank(item.severity), -item.count, item.category, item.title),
    )


def _header(data: DashboardData) -> Panel:
    risk = _risk_state(data)
    source_name = Path(data.source).name or data.source
    elevated = sum(
        count
        for severity, count in data.severities.items()
        if _severity_rank(severity) >= _severity_rank("MEDIUM")
    )

    body = Text()
    body.append("AEGISLOG", style=f"bold {ACCENT}")
    body.append("  /  INVESTIGATION", style="bold white")
    body.append(f"  v{__version__}", style=MUTED)
    body.append("\n")
    body.append("SOURCE  ", style=MUTED)
    body.append(source_name, style="bold white")
    body.append("    POSTURE  ", style=MUTED)
    body.append(risk, style=f"bold {risk_style(risk)}")
    body.append("\n")
    body.append("EVENTS  ", style=MUTED)
    body.append(f"{data.lines:,}", style=f"bold {ACCENT}")
    body.append("    FINDINGS  ", style=MUTED)
    body.append(str(len(data.findings)), style="bold white")
    body.append("    ELEVATED  ", style=MUTED)
    body.append(str(elevated), style=f"bold {risk_style(risk)}")
    body.append("    INCIDENTS  ", style=MUTED)
    body.append(str(len(data.incidents)), style=f"bold {INCIDENT}")
    body.append("    ANOMALIES  ", style=MUTED)
    body.append(str(len(data.anomalies)), style=f"bold {ANOMALY}")
    if data.source != source_name:
        body.append("\nPATH    ", style=MUTED)
        body.append(data.source, style=MUTED)
    body.append("\nLOCAL / READ-ONLY", style=MUTED)

    return Panel(
        body,
        title=Text(" INVESTIGATION SUMMARY ", style=f"bold {ACCENT_SOFT}"),
        title_align="left",
        border_style=ACCENT_SOFT,
        padding=(0, 1),
    )


def _analyst_focus(data: DashboardData) -> Panel:
    risk = _risk_state(data)
    findings = _ordered_findings(data)
    incidents = _ordered_incidents(data)
    top_finding = findings[0] if findings else None
    top_incident = incidents[0] if incidents else None

    body = Text()
    body.append("PRIORITY  ", style=MUTED)
    body.append(risk, style=f"bold {risk_style(risk)}")

    incident_first = bool(
        top_incident
        and (
            top_finding is None
            or _severity_rank(top_incident.severity) >= _severity_rank(top_finding.severity)
        )
    )

    if incident_first and top_incident:
        incident_id = f"INC-{top_incident.id.upper()[:8]}"
        body.append("\nPRIMARY   ", style=MUTED)
        body.append(incident_id, style=f"bold {INCIDENT}")
        body.append("  ", style=MUTED)
        body.append(top_incident.title, style="bold white")
        body.append("\nACTION    ", style=MUTED)
        body.append(
            "Review the correlated evidence chain with source, identity, host, and surrounding telemetry context.",
            style="white",
        )
        if top_finding:
            body.append("\nNEXT      ", style=MUTED)
            body.append(top_finding.severity, style=f"bold {risk_style(top_finding.severity)}")
            body.append("  ", style=MUTED)
            body.append(top_finding.title, style="white")
    elif top_finding:
        body.append("\nPRIMARY   ", style=MUTED)
        body.append(top_finding.title, style="bold white")
        body.append("\nACTION    ", style=MUTED)
        body.append(top_finding.recommendation, style="white")
        if top_incident:
            body.append("\nNEXT      ", style=MUTED)
            body.append(f"INC-{top_incident.id.upper()[:8]}", style=f"bold {INCIDENT}")
            body.append("  ", style=MUTED)
            body.append(top_incident.title, style="white")
        elif len(findings) > 1:
            next_item = findings[1]
            body.append("\nNEXT      ", style=MUTED)
            body.append(next_item.severity, style=f"bold {risk_style(next_item.severity)}")
            body.append("  ", style=MUTED)
            body.append(next_item.title, style="white")
    else:
        body.append("\nPRIMARY   ", style=MUTED)
        body.append("No elevated rule-backed findings or correlated incidents retained", style=SUCCESS)
        body.append("\nACTION    ", style=MUTED)
        body.append("Review coverage and preserve original telemetry when required.", style="white")

    body.append("\n\nSignals are investigative evidence, not proof of compromise.", style=MUTED)
    return Panel(
        body,
        title=Text(" ANALYST FOCUS ", style=f"bold {risk_style(risk)}"),
        title_align="left",
        border_style=risk_style(risk),
        padding=(0, 1),
    )


def _incident_table(data: DashboardData, limit: int = 8) -> Table:
    ordered = _ordered_incidents(data)
    table = Table(
        title=f"ACTIVE INCIDENTS  [{min(len(ordered), limit)}/{len(ordered)}]",
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
    for item in ordered[:limit]:
        table.add_row(
            f"INC-{item.id.upper()[:8]}",
            severity_text(item.severity),
            str(item.count),
            Text(item.category),
            Text(item.title),
        )
    return table


def _evidence_preview(value: str, limit: int = 180) -> str:
    normalized = " ".join(value.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 1].rstrip() + "…"


def _finding_table(data: DashboardData, limit: int = 12) -> Table:
    ordered = _ordered_findings(data)
    table = Table(
        title=f"Detected findings  [{min(len(ordered), limit)}/{len(ordered)}]",
        title_style=f"bold {ACCENT}",
        expand=True,
        border_style=ACCENT_SOFT,
        padding=(0, 1),
    )
    table.add_column("SEV", width=9)
    table.add_column("CATEGORY", width=17)
    table.add_column("DETECTION", width=32)
    table.add_column("EVIDENCE PREVIEW", ratio=1, overflow="fold")
    for item in ordered[:limit]:
        table.add_row(
            severity_text(item.severity),
            Text(item.category),
            Text(item.title),
            Text(_evidence_preview(item.evidence)),
        )
    if not ordered:
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


def _source_argument(source: str) -> str:
    if sys.platform == "win32" or getattr(sys, "frozen", False):
        return f'"{source.replace(chr(34), chr(34) * 2)}"'
    return shlex.quote(source)


def _next_steps(data: DashboardData) -> Panel:
    command = "AegisLog.exe" if getattr(sys, "frozen", False) else "aegislog"
    source = _source_argument(data.source)
    incidents = _ordered_incidents(data)

    body = Text()
    body.append("REPORT  ", style=MUTED)
    body.append("HTML investigation report generated automatically", style=SUCCESS)
    body.append("\nLIST    ", style=MUTED)
    body.append(f"{command} incidents {source}", style=ACCENT)
    if incidents:
        incident_id = f"INC-{incidents[0].id.upper()[:8]}"
        body.append("\nOPEN    ", style=MUTED)
        body.append(f"{command} investigate {source} {incident_id}", style=INCIDENT)
        body.append("\nEXPLAIN ", style=MUTED)
        body.append(f"{command} explain {source} {incident_id}", style=INFO)

    return Panel(
        body,
        title=Text(" FOLLOW-UP / COPY-READY ", style=f"bold {ACCENT}"),
        title_align="left",
        border_style=ACCENT_SOFT,
        padding=(0, 1),
    )


def render_dashboard(data: DashboardData) -> RenderableType:
    """Return a prioritized SOC-style investigation dashboard."""
    sections: list[RenderableType] = [_header(data), _analyst_focus(data)]
    if data.incidents:
        sections.append(_incident_table(data))
    sections.append(_finding_table(data))
    if data.anomalies:
        sections.append(_anomaly_table(data))
    sections.extend((_telemetry_table(data), _next_steps(data)))
    return Group(*sections)
