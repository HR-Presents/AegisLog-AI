from __future__ import annotations

from rich.console import Group, RenderableType
from rich.table import Table
from rich.text import Text

from .investigation import InvestigationIncident
from .theme import ACCENT, ACCENT_SOFT, INCIDENT, MUTED, NEUTRAL, WARNING


def triage_priority(incident: InvestigationIncident) -> tuple[str, str]:
    """Return a conservative analyst-review priority and presentation style."""
    severity = incident.severity.upper()
    if severity == "CRITICAL" or (severity == "HIGH" and incident.confidence >= 85):
        return "Urgent review", INCIDENT
    if severity == "HIGH" or (severity == "MEDIUM" and incident.confidence >= 80):
        return "Elevated review", WARNING
    return "Routine review", ACCENT_SOFT


def incident_triage_panel(incident: InvestigationIncident) -> RenderableType:
    """Summarize triage with a flat evidence-first layout."""
    priority, style = triage_priority(incident)

    heading = Text("TRIAGE", style=f"bold {MUTED}")
    priority_line = Text()
    priority_line.append(priority, style=f"bold {style}")
    priority_line.append(f"   confidence {incident.confidence}%", style=MUTED)

    metrics = Table.grid(padding=(0, 2))
    metrics.add_column(style=MUTED)
    metrics.add_column(style=NEUTRAL)
    metrics.add_row("Findings", str(len(incident.findings)))
    metrics.add_row("Timeline events", str(len(incident.timeline)))
    metrics.add_row("Associated entities", str(len(incident.entities)))

    if incident.entities:
        next_step = "Validate associated entities against nearby identity, host, network, or application telemetry."
    elif incident.timeline:
        next_step = "Validate the reconstructed event sequence against surrounding source telemetry."
    else:
        next_step = "Collect additional source context before escalating this incident."

    guidance = Text()
    guidance.append("Next  ", style=f"bold {ACCENT}")
    guidance.append(next_step, style=NEUTRAL)

    caveat = Text(
        "Priority reflects available local evidence only; it is not proof of compromise, attribution, or attacker intent.",
        style=MUTED,
    )

    return Group(
        heading,
        Text("─" * 48, style="grey35"),
        priority_line,
        Text(""),
        metrics,
        Text(""),
        guidance,
        Text(""),
        caveat,
    )
