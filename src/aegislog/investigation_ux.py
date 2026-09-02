from __future__ import annotations

from rich.panel import Panel
from rich.text import Text

from .investigation import InvestigationIncident
from .theme import ACCENT, ACCENT_SOFT, INCIDENT, MUTED, WARNING


def triage_priority(incident: InvestigationIncident) -> tuple[str, str]:
    """Return a conservative analyst-review priority and presentation style."""
    severity = incident.severity.upper()
    if severity == "CRITICAL" or (severity == "HIGH" and incident.confidence >= 85):
        return "Urgent review", INCIDENT
    if severity == "HIGH" or (severity == "MEDIUM" and incident.confidence >= 80):
        return "Elevated review", WARNING
    return "Routine review", ACCENT_SOFT


def incident_triage_panel(incident: InvestigationIncident) -> Panel:
    """Summarize why an incident deserves analyst attention without claiming compromise."""
    priority, style = triage_priority(incident)
    text = Text()
    text.append("Priority: ", style="bold white")
    text.append(priority, style=style)
    text.append("\nEvidence: ", style="bold white")
    text.append(str(len(incident.findings)), style=ACCENT)
    text.append(" finding(s), ", style=MUTED)
    text.append(str(len(incident.timeline)), style=ACCENT)
    text.append(" timeline event(s), ", style=MUTED)
    text.append(str(len(incident.entities)), style=ACCENT)
    text.append(" associated entity value(s)", style=MUTED)
    text.append("\nConfidence: ", style="bold white")
    text.append(f"{incident.confidence}%", style=ACCENT)

    if incident.entities:
        next_step = "Validate the associated entities against nearby identity, host, network, or application telemetry."
    elif incident.timeline:
        next_step = "Validate the reconstructed event sequence against surrounding source telemetry."
    else:
        next_step = "Collect additional source context before escalating this incident."

    text.append("\nRecommended triage step: ", style="bold white")
    text.append(next_step, style="white")
    text.append(
        "\n\nPriority reflects available local evidence only; it is not proof of compromise, attribution, or attacker intent.",
        style=MUTED,
    )
    return Panel(text, title="Analyst triage", title_align="left", border_style=style)
