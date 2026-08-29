from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .explain import explain_incident
from .investigation import load_investigation

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
        console.print(f"[red]Incident {incident_id} was not found in this log.[/red]")
        raise typer.Exit(code=2)

    result = explain_incident(incident)
    console.print(
        Panel(
            Text(result.summary),
            title=f"EXPLAIN THIS INCIDENT — {incident.id}",
            subtitle=f"{incident.severity} | confidence {incident.confidence}% | local-only",
        )
    )
    console.print(Panel(Text(result.why_it_matters), title="Why this matters"))

    evidence = Table(title="What AegisLog saw", expand=True, show_lines=True)
    evidence.add_column("#", justify="right", width=4)
    evidence.add_column("Evidence")
    for index, item in enumerate(result.evidence, start=1):
        evidence.add_row(str(index), Text(item))
    console.print(evidence)

    attack = Table(title="MITRE ATT&CK context", expand=True, show_lines=True)
    attack.add_column("Technique", width=26)
    attack.add_column("Tactic", width=22)
    attack.add_column("Confidence", justify="right", width=12)
    for item in result.techniques:
        attack.add_row(f"{item.id} {item.name}", item.tactic, f"{item.confidence}%")
    if not result.techniques:
        attack.add_row("No evidence-supported mapping", "-", "-")
    console.print(attack)

    steps = Table(title="Safe investigation steps", expand=True, show_lines=True)
    steps.add_column("Step", justify="right", width=6)
    steps.add_column("Action")
    for index, item in enumerate(result.next_steps, start=1):
        steps.add_row(str(index), Text(item))
    console.print(steps)
    console.print(Panel(Text(result.caveat), title="Analyst note"))
