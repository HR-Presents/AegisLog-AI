from __future__ import annotations

from shutil import get_terminal_size

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
    """Summarize triage with a width-aware, evidence-first layout."""
    priority, style = triage_priority(incident)
    width = max(32, get_terminal_size((80, 24)).columns)
    narrow = width < 60

    heading = Text("Analyst triage", style=f"bold {MUTED}")
    priority_line = Text("Priority: ", style=MUTED)
    priority_line.append(priority, style=f"bold {style}")
    if narrow:
        priority_line.append(f"\nConfidence: {incident.confidence}%", style=MUTED)
    else:
        priority_line.append(f"   Confidence: {incident.confidence}%", style=MUTED)

    metrics = Table.grid(padding=(0, 1 if narrow else 2), expand=narrow)
    metrics.add_column(style=MUTED, min_width=8 if narrow else 12, overflow="fold")
    metrics.add_column(style=NEUTRAL, ratio=1, overflow="fold")
    metrics.add_row("Findings", str(len(incident.findings)))
    metrics.add_row("Timeline events", str(len(incident.timeline)))
    metrics.add_row("Associated entities", str(len(incident.entities)))

    if incident.entities:
        next_step = "Validate the associated entities against nearby identity, host, network, or application telemetry."
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
        Text("-" * max(20, min(width - 2, 48)), style="grey35"),
        priority_line,
        Text(""),
        metrics,
        Text(""),
        guidance,
        Text(""),
        caveat,
    )
