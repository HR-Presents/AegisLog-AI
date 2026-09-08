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
from .ui import bounded

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

    summary = Text(result.summary, style="white")
    subtitle = Text()
    subtitle.append(incident.severity, style=severity_text(incident.severity).style)
    subtitle.append(f" | confidence {incident.confidence}%", style=ACCENT)
    subtitle.append(" | local-only", style=MUTED)
    console.print(
        bounded(
            Panel(
                summary,
                title=Text(f"INCIDENT INTELLIGENCE - {incident.id}", style=f"bold {INCIDENT}"),
                subtitle=subtitle,
                border_style=INCIDENT,
            )
        )
    )

    why = Text(result.why_it_matters, style="white")
    console.print(bounded(Panel(why, title=Text("WHY THIS MATTERS", style=f"bold {WARNING}"), border_style=WARNING)))

    evidence = Table(
        title="EVIDENCE OBSERVED",
        title_style=f"bold {ACCENT}",
        border_style=ACCENT_SOFT,
        expand=True,
        show_lines=True,
        padding=(0, 1),
    )
    evidence.add_column("#", justify="right", min_width=2, max_width=4, style=ACCENT, no_wrap=True)
    evidence.add_column("Evidence", min_width=18, ratio=1, style="white", overflow="fold")
    for index, item in enumerate(result.evidence, start=1):
        evidence.add_row(str(index), Text(item))
    console.print(bounded(evidence))

    attack = Table(
        title="MITRE ATT&CK CONTEXT",
        title_style=f"bold {INCIDENT}",
        border_style=INCIDENT,
        expand=True,
        show_lines=True,
        padding=(0, 1),
    )
    attack.add_column("Technique", min_width=14, ratio=3, style=INCIDENT, overflow="fold")
    attack.add_column("Tactic", min_width=10, ratio=2, style=ACCENT, overflow="fold")
    attack.add_column("Confidence", min_width=8, max_width=12, justify="right", style=SUCCESS, no_wrap=True)
    for item in result.techniques:
        attack.add_row(f"{item.id} {item.name}", item.tactic, f"{item.confidence}%")
    if not result.techniques:
        attack.add_row(Text("No evidence-supported mapping", style=MUTED), Text("-", style=MUTED), Text("-", style=MUTED))
    console.print(bounded(attack))

    steps = Table(
        title="SAFE INVESTIGATION STEPS",
        title_style=f"bold {SUCCESS}",
        border_style=SUCCESS,
        expand=True,
        show_lines=True,
        padding=(0, 1),
    )
    steps.add_column("Step", justify="right", min_width=4, max_width=6, style=SUCCESS, no_wrap=True)
    steps.add_column("Action", min_width=18, ratio=1, style="white", overflow="fold")
    for index, item in enumerate(result.next_steps, start=1):
        steps.add_row(str(index), Text(item))
    console.print(bounded(steps))

    caveat = Text(result.caveat, style=MUTED)
    console.print(bounded(Panel(caveat, title=Text("ANALYST NOTE", style=f"bold {ACCENT}"), border_style=ACCENT_SOFT)))
