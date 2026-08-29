from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .correlation import correlate_entities
from .database import add_incidents, list_incidents
from .engine import analyze_file
from .entity_store import find_entity, replace_incident_entities, top_entities
from .incidents import correlate

console = Console()


def index_entities(path: Path = typer.Argument(..., exists=True, dir_okay=False)) -> None:
    """Persist incidents from a log and index correlated entities for later hunting."""
    _, findings = analyze_file(path)
    incidents = correlate(findings)
    if not incidents:
        console.print("No incidents were found to index.")
        return
    from datetime import datetime, timezone

    add_incidents(str(path), datetime.now(timezone.utc).isoformat(), incidents)
    rows = list_incidents(limit=len(incidents))
    indexed = 0
    for row, incident in zip(reversed(rows), incidents):
        incident_findings = [item for item in findings if item.category == incident.category]
        entities = correlate_entities(incident_findings)
        indexed += replace_incident_entities(int(row["id"]), entities)
    console.print(f"Persisted {len(incidents)} incidents and indexed {indexed} entity links.")


def entity(entity_type: str, value: str, limit: int = 100) -> None:
    """Investigate historical incidents linked to one exact entity."""
    rows = find_entity(entity_type, value, limit)
    if not rows:
        console.print("No persisted incidents are linked to that entity.")
        return
    table = Table(show_lines=True)
    table.add_column("Incident")
    table.add_column("Time")
    table.add_column("Severity")
    table.add_column("Category")
    table.add_column("Source")
    table.add_column("Summary")
    for row in rows:
        table.add_row(str(row["incident_id"]), row["recorded_at"], row["severity"], row["category"], row["source"], row["title"])
    console.print(table)


def entity_top(entity_type: str = "", limit: int = 25) -> None:
    """Rank historically observed entities by correlation score."""
    rows = top_entities(entity_type or None, limit)
    if not rows:
        console.print("No persisted entity index exists yet. Run index-entities on a log first.")
        return
    table = Table(show_lines=True)
    table.add_column("Type")
    table.add_column("Entity")
    table.add_column("Incidents")
    table.add_column("Score")
    table.add_column("Max")
    for row in rows:
        table.add_row(row["entity_type"], row["entity_value"], str(row["incident_count"]), str(row["total_score"]), str(row["max_score"]))
    console.print(table)
