from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .case_store import get_case, list_cases, save_cases
from .investigation import load_investigation

console = Console()


def save_investigation(path: Path = typer.Argument(..., exists=True, dir_okay=False)) -> None:
    """Analyze a log and persist its investigation cases locally."""
    _, incidents, _ = load_investigation(path)
    count = save_cases(str(path.resolve()), incidents)
    console.print(f"[green]Saved/updated {count} investigation case(s) in the local AegisLog history.[/green]")


def case_history(
    limit: int = typer.Option(50, "--limit", min=1, max=1000),
    severity: str | None = typer.Option(None, "--severity"),
) -> None:
    """Show investigation cases retained across AegisLog restarts."""
    rows = list_cases(limit=limit, severity=severity)
    table = Table(title="Persistent investigation history", expand=True)
    table.add_column("Incident ID", width=14)
    table.add_column("Severity", width=10)
    table.add_column("Confidence", justify="right", width=12)
    table.add_column("Seen", justify="right", width=7)
    table.add_column("Category", width=18)
    table.add_column("Source")
    table.add_column("Summary")
    for row in rows:
        table.add_row(
            row["incident_id"], row["severity"], f'{row["confidence"]}%', str(row["observation_count"]),
            row["category"], Text(row["source"]), Text(row["title"]),
        )
    if not rows:
        table.add_row("-", "-", "-", "0", "-", "No saved cases", "Run save-investigation <file>")
    console.print(table)


def case_show(incident_id: str = typer.Argument(...)) -> None:
    """Open a previously saved investigation without needing the original log file."""
    item = get_case(incident_id)
    if item is None:
        console.print(f"[red]Saved incident {incident_id} was not found.[/red]")
        raise typer.Exit(code=2)
    console.print(Panel(
        Text(
            f'{item["incident_id"]}  {item["severity"]}  confidence {item["confidence"]}%\n'
            f'{item["title"]}\nCategory: {item["category"]}\nObservations: {item["observation_count"]}\n'
            f'First saved: {item["first_recorded_at"]}\nLast saved: {item["last_recorded_at"]}'
        ),
        title="SAVED AEGISLOG CASE",
        subtitle=Text(item["source"]),
    ))
    entities = Table(title="Entities")
    entities.add_column("Entity")
    for entity in item["entities"]:
        entities.add_row(Text(str(entity)))
    if not item["entities"]:
        entities.add_row("No structured entities stored")
    console.print(entities)
    timeline = Table(title="Saved activity timeline", expand=True, show_lines=True)
    timeline.add_column("When", width=12); timeline.add_column("Service", width=16); timeline.add_column("Level", width=10); timeline.add_column("Activity")
    for event in item["timeline"]:
        timeline.add_row(str(event["timestamp"]), Text(str(event["service"])), str(event["level"]), Text(str(event["summary"])))
    if not item["timeline"]:
        timeline.add_row("-", "-", "-", "No timeline stored")
    console.print(timeline)
    evidence = Table(title="Saved detection evidence", expand=True, show_lines=True)
    evidence.add_column("Severity", width=10); evidence.add_column("Finding", width=36); evidence.add_column("Evidence")
    for finding in item["findings"]:
        evidence.add_row(str(finding["severity"]), Text(str(finding["title"])), Text(str(finding["evidence"])))
    console.print(evidence)
