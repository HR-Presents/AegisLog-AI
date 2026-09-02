from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .explain import explain_incident
from .investigation import load_investigation
from .theme import ACCENT, ACCENT_SOFT, HIGH, INCIDENT, MUTED, SUCCESS, WARNING, severity_text

console = Console()


def explain(
    path: Path = typer.Argument(..., exists=True, dir_okay=False),
    incident_id: str = typer.Argument(..., help="Incident ID shown by the incidents command."),
) -> None:
    """Explain one incident in clear analyst-friendly language using only local evidence."""
    _, incidents, _ = load_investigation(path)
    wanted = incident_id.upper()
    incident = next((item for item in incidents if item.id.upper() == wanted), None)
    if incident is None:
        message = Text("Incident ", style=HIGH)
        message.append(incident_id, style=f"bold {INCIDENT}")
        message.append(" was not found in this log.", style=HIGH)
        console.print(message)
        raise typer.Exit(code=2)

    result = explain_incident(incident)

    summary = Text(result.summary)
    summary.stylize("white")
    subtitle = Text()
    subtitle.append(incident.severity, style=severity_text(incident.severity).style)
    subtitle.append(f" | confidence {incident.confidence}%", style=ACCENT)
    subtitle.append(" | local-only", style=MUTED)
    console.print(
        Panel(
            summary,
            title=Text(f"EXPLAIN THIS INCIDENT — {incident.id}", style=f"bold {INCIDENT}"),
            subtitle=subtitle,
            border_style=INCIDENT,
        )
    )

    why = Text(result.why_it_matters, style="white")
    console.print(Panel(why, title=Text("Why this matters", style=f"bold {WARNING}"), border_style=WARNING))

    evidence = Table(title="What AegisLog saw", title_style=f"bold {ACCENT}", border_style=ACCENT_SOFT, expand=True, show_lines=True)
    evidence.add_column("#", justify="right", width=4, style=ACCENT)
    evidence.add_column("Evidence", style="white")
    for index, item in enumerate(result.evidence, start=1):
        evidence.add_row(str(index), Text(item))
    console.print(evidence)

    attack = Table(title="MITRE ATT&CK context", title_style=f"bold {INCIDENT}", border_style=INCIDENT, expand=True, show_lines=True)
    attack.add_column("Technique", width=26, style=INCIDENT)
    attack.add_column("Tactic", width=22, style=ACCENT)
    attack.add_column("Confidence", justify="right", width=12, style=SUCCESS)
    for item in result.techniques:
        attack.add_row(f"{item.id} {item.name}", item.tactic, f"{item.confidence}%")
    if not result.techniques:
        attack.add_row(Text("No evidence-supported mapping", style=MUTED), Text("-", style=MUTED), Text("-", style=MUTED))
    console.print(attack)

    steps = Table(title="Safe investigation steps", title_style=f"bold {SUCCESS}", border_style=SUCCESS, expand=True, show_lines=True)
    steps.add_column("Step", justify="right", width=6, style=SUCCESS)
    steps.add_column("Action", style="white")
    for index, item in enumerate(result.next_steps, start=1):
        steps.add_row(str(index), Text(item))
    console.print(steps)

    caveat = Text(result.caveat, style=MUTED)
    console.print(Panel(caveat, title=Text("Analyst note", style=f"bold {ACCENT}"), border_style=ACCENT_SOFT))
