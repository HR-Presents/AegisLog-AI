from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .investigation import InvestigationIncident, load_investigation
from .mitre import map_findings

console = Console()


def _incident_table(incidents: list[InvestigationIncident]) -> Table:
    table = Table(title="Investigation incidents", expand=True)
    table.add_column("Incident ID", width=14)
    table.add_column("Severity", width=10)
    table.add_column("Confidence", justify="right", width=12)
    table.add_column("Category", width=18)
    table.add_column("ATT&CK", width=16)
    table.add_column("Signals", justify="right", width=8)
    table.add_column("Summary")
    for item in incidents:
        techniques = map_findings(item.findings)
        attack = ", ".join(t.id for t in techniques[:2]) or "-"
        table.add_row(item.id, item.severity, f"{item.confidence}%", item.category, attack, str(len(item.findings)), Text(item.title))
    if not incidents:
        table.add_row("-", "-", "-", "-", "-", "0", "No correlated incidents detected")
    return table


def incidents(path: Path = typer.Argument(..., exists=True, dir_okay=False)) -> None:
    """List deterministic incident IDs, confidence scores and ATT&CK mappings for a log file."""
    _, items, _ = load_investigation(path)
    console.print(_incident_table(items))
    if items:
        console.print(f"[dim]Drill down with: AegisLog.exe investigate {path} {items[0].id}[/dim]")


def _attack_table(incident: InvestigationIncident) -> Table:
    table = Table(title="MITRE ATT&CK mapping", expand=True, show_lines=True)
    table.add_column("Technique", width=14)
    table.add_column("Tactic", width=22)
    table.add_column("Confidence", justify="right", width=12)
    table.add_column("Evidence")
    techniques = map_findings(incident.findings)
    for technique in techniques:
        table.add_row(f"{technique.id} {technique.name}", technique.tactic, f"{technique.confidence}%", Text(technique.evidence))
    if not techniques:
        table.add_row("-", "-", "-", "No evidence-supported ATT&CK technique mapped")
    return table


def investigate(
    path: Path = typer.Argument(..., exists=True, dir_okay=False),
    incident_id: str = typer.Argument(..., help="Incident ID shown by the incidents command."),
) -> None:
    """Open a detailed incident timeline, entities, evidence, ATT&CK mapping and confidence view."""
    _, items, _ = load_investigation(path)
    wanted = incident_id.upper()
    incident = next((item for item in items if item.id.upper() == wanted), None)
    if incident is None:
        console.print(f"[red]Incident {incident_id} was not found in this log.[/red]")
        raise typer.Exit(code=2)
    console.print(Panel(
        Text(f"{incident.id}  {incident.severity}  confidence {incident.confidence}%\n{incident.title}\nCategory: {incident.category}"),
        title="AEGISLOG INCIDENT INVESTIGATION",
        subtitle="Evidence-led defensive analysis",
    ))
    entities = Table(title="Associated entities")
    entities.add_column("Entity")
    for item in incident.entities:
        entities.add_row(Text(item))
    if not incident.entities:
        entities.add_row("No structured IP/user entity extracted")
    console.print(entities)
    console.print(_attack_table(incident))
    timeline = Table(title="Attack / activity timeline", expand=True, show_lines=True)
    timeline.add_column("When", width=12)
    timeline.add_column("Service", width=16)
    timeline.add_column("Level", width=10)
    timeline.add_column("Activity")
    for event in incident.timeline:
        timeline.add_row(event.timestamp, Text(event.service), event.level, Text(event.summary))
    if not incident.timeline:
        timeline.add_row("-", "-", "-", "No matching timeline events were reconstructed")
    console.print(timeline)
    evidence = Table(title="Detection evidence", expand=True, show_lines=True)
    evidence.add_column("Severity", width=10)
    evidence.add_column("Finding", width=38)
    evidence.add_column("Evidence")
    for finding in incident.findings:
        evidence.add_row(finding.severity, Text(finding.title), Text(finding.evidence))
    console.print(evidence)
    console.print(Panel(
        "ATT&CK mappings are evidence-based analyst context, not proof that a specific adversary technique occurred. "
        "Confidence estimates strength of available log evidence; validate against host, identity, network and application context before action.",
        title="Analyst guidance",
    ))


def mitre(path: Path = typer.Argument(..., exists=True, dir_okay=False)) -> None:
    """Show evidence-supported MITRE ATT&CK techniques across detected incidents."""
    _, incidents_list, _ = load_investigation(path)
    table = Table(title="MITRE ATT&CK intelligence", expand=True, show_lines=True)
    table.add_column("Incident", width=14)
    table.add_column("Technique", width=24)
    table.add_column("Tactic", width=22)
    table.add_column("Confidence", justify="right", width=12)
    table.add_column("Evidence")
    rows = 0
    for incident in incidents_list:
        for technique in map_findings(incident.findings):
            table.add_row(incident.id, f"{technique.id} {technique.name}", technique.tactic, f"{technique.confidence}%", Text(technique.evidence))
            rows += 1
    if not rows:
        table.add_row("-", "-", "-", "-", "No evidence-supported ATT&CK mappings found")
    console.print(table)


def intel_entities(path: Path = typer.Argument(..., exists=True, dir_okay=False)) -> None:
    """Show IP and user entity intelligence extracted from a log file."""
    _, _, profiles = load_investigation(path)
    table = Table(title="Entity intelligence", expand=True)
    table.add_column("Type", width=10)
    table.add_column("Entity", width=24)
    table.add_column("Occurrences", justify="right", width=12)
    table.add_column("Services")
    table.add_column("First", justify="right", width=8)
    table.add_column("Last", justify="right", width=8)
    for item in profiles:
        table.add_row(item.kind.upper(), Text(item.value), str(item.occurrences), ", ".join(item.services), str(item.first_seen), str(item.last_seen))
    if not profiles:
        table.add_row("-", "No IP/user entities extracted", "0", "-", "-", "-")
    console.print(table)
