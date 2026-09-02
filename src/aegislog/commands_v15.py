from __future__ import annotations

import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .investigation import InvestigationIncident, load_investigation
from .investigation_ux import incident_triage_panel
from .mitre import map_findings
from .theme import ACCENT, ACCENT_SOFT, INCIDENT, INFO, MUTED, WARNING, severity_text

console = Console()


def _command_name() -> str:
    return "AegisLog.exe" if getattr(sys, "frozen", False) else "aegislog"


def _display_path(path: Path) -> str:
    value = str(path)
    return f'"{value}"' if any(character.isspace() for character in value) else value


def _analyst_workflow(path: Path, incident: InvestigationIncident) -> Panel:
    command = _command_name()
    source = _display_path(path)
    text = Text()
    text.append("1. Investigate evidence: ", style="bold white")
    text.append(f"{command} investigate {source} {incident.id}", style=INCIDENT)
    text.append("\n2. Read the deterministic explanation: ", style="bold white")
    text.append(f"{command} explain {source} {incident.id}", style=INFO)
    text.append("\n3. Preserve the investigation locally: ", style="bold white")
    text.append(f"{command} save-investigation {source} {incident.id}", style=ACCENT)
    text.append("\n4. Expand context: ", style="bold white")
    text.append(f"{command} intel-entities {source}", style=ACCENT)
    text.append("  •  ", style=MUTED)
    text.append(f"{command} mitre {source}", style=WARNING)
    text.append("\n\nAegisLog findings are investigative signals, not proof of compromise or attribution.", style=MUTED)
    return Panel(text, title="Analyst workflow", title_align="left", border_style=INCIDENT)


def _investigation_next_actions(path: Path, incident: InvestigationIncident) -> Panel:
    command = _command_name()
    source = _display_path(path)
    text = Text()
    text.append("Explain this incident: ", style="bold white")
    text.append(f"{command} explain {source} {incident.id}", style=INFO)
    text.append("\nSave this investigation: ", style="bold white")
    text.append(f"{command} save-investigation {source} {incident.id}", style=ACCENT)
    text.append("\nReview all entities: ", style="bold white")
    text.append(f"{command} intel-entities {source}", style=ACCENT)
    text.append("\nReview ATT&CK context: ", style="bold white")
    text.append(f"{command} mitre {source}", style=WARNING)
    return Panel(text, title="Next analyst actions", title_align="left", border_style=ACCENT_SOFT)


def _incident_table(incidents: list[InvestigationIncident]) -> Table:
    table = Table(title="Investigation incidents", title_style=f"bold {INCIDENT}", expand=True, border_style=INCIDENT)
    table.add_column("Incident ID", width=14, style=INCIDENT)
    table.add_column("Severity", width=10)
    table.add_column("Confidence", justify="right", width=12, style=ACCENT)
    table.add_column("Category", width=18)
    table.add_column("ATT&CK", width=16, style=WARNING)
    table.add_column("Signals", justify="right", width=8, style=ACCENT)
    table.add_column("Summary")
    for item in incidents:
        techniques = map_findings(item.findings)
        attack = ", ".join(t.id for t in techniques[:2]) or "-"
        table.add_row(item.id, severity_text(item.severity), f"{item.confidence}%", Text(item.category), attack, str(len(item.findings)), Text(item.title))
    if not incidents:
        table.add_row("-", "-", "-", "-", "-", "0", Text("No correlated incidents detected", style=MUTED))
    return table


def incidents(path: Path = typer.Argument(..., exists=True, dir_okay=False)) -> None:
    """List deterministic incident IDs, confidence scores and ATT&CK mappings for a log file."""
    _, items, _ = load_investigation(path)
    console.print(_incident_table(items))
    if items:
        console.print(_analyst_workflow(path, items[0]))
    else:
        console.print(Panel(
            Text("No correlated incidents were detected. Review the main dashboard and findings before escalating.", style=MUTED),
            title="Analyst workflow",
            title_align="left",
            border_style=ACCENT_SOFT,
        ))


def _attack_table(incident: InvestigationIncident) -> Table:
    table = Table(title="MITRE ATT&CK mapping", title_style=f"bold {WARNING}", expand=True, show_lines=True, border_style=WARNING)
    table.add_column("Technique", width=14, style=WARNING)
    table.add_column("Tactic", width=22)
    table.add_column("Confidence", justify="right", width=12, style=ACCENT)
    table.add_column("Evidence")
    techniques = map_findings(incident.findings)
    for technique in techniques:
        table.add_row(f"{technique.id} {technique.name}", Text(technique.tactic), f"{technique.confidence}%", Text(technique.evidence))
    if not techniques:
        table.add_row("-", "-", "-", Text("No evidence-supported ATT&CK technique mapped", style=MUTED))
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
        message = Text()
        message.append("Incident ", style="bold white")
        message.append(incident_id, style=INCIDENT)
        message.append(" was not found in this log.", style="bold white")
        console.print(Panel(message, title="Investigation lookup failed", border_style="bright_red"))
        raise typer.Exit(code=2)

    header = Text()
    header.append(f"{incident.id}  ", style=INCIDENT)
    header.append_text(severity_text(incident.severity))
    header.append(f"  confidence {incident.confidence}%\n", style=ACCENT)
    header.append(f"{incident.title}\n", style="bold white")
    header.append("Category: ", style=MUTED)
    header.append(incident.category, style="white")
    console.print(Panel(
        header,
        title="AEGISLOG INCIDENT INVESTIGATION",
        subtitle="Evidence-led defensive analysis",
        border_style=INCIDENT,
    ))
    console.print(incident_triage_panel(incident))

    entities = Table(title="Associated entities", title_style=f"bold {ACCENT}", border_style=ACCENT_SOFT)
    entities.add_column("Entity", style=ACCENT)
    for item in incident.entities:
        entities.add_row(Text(item))
    if not incident.entities:
        entities.add_row(Text("No structured IP/user entity extracted", style=MUTED))
    console.print(entities)
    console.print(_attack_table(incident))

    timeline = Table(title="Attack / activity timeline", title_style=f"bold {INCIDENT}", expand=True, show_lines=True, border_style=INCIDENT)
    timeline.add_column("When", width=12, style=ACCENT)
    timeline.add_column("Service", width=16)
    timeline.add_column("Level", width=10, style=WARNING)
    timeline.add_column("Activity")
    for event in incident.timeline:
        timeline.add_row(event.timestamp, Text(event.service), event.level, Text(event.summary))
    if not incident.timeline:
        timeline.add_row("-", "-", "-", Text("No matching timeline events were reconstructed", style=MUTED))
    console.print(timeline)

    evidence = Table(title="Detection evidence", title_style=f"bold {ACCENT}", expand=True, show_lines=True, border_style=ACCENT_SOFT)
    evidence.add_column("Severity", width=10)
    evidence.add_column("Finding", width=38)
    evidence.add_column("Evidence")
    for finding in incident.findings:
        evidence.add_row(severity_text(finding.severity), Text(finding.title), Text(finding.evidence))
    if not incident.findings:
        evidence.add_row("-", Text("No rule-backed findings attached", style=MUTED), "-")
    console.print(evidence)

    console.print(Panel(
        Text(
            "ATT&CK mappings are evidence-based analyst context, not proof that a specific adversary technique occurred. "
            "Confidence estimates strength of available log evidence; validate against host, identity, network and application context before action.",
            style=MUTED,
        ),
        title="Analyst guidance",
        border_style=ACCENT_SOFT,
    ))
    console.print(_investigation_next_actions(path, incident))


def mitre(path: Path = typer.Argument(..., exists=True, dir_okay=False)) -> None:
    """Show evidence-supported MITRE ATT&CK techniques across detected incidents."""
    _, incidents_list, _ = load_investigation(path)
    table = Table(title="MITRE ATT&CK intelligence", title_style=f"bold {WARNING}", expand=True, show_lines=True, border_style=WARNING)
    table.add_column("Incident", width=14, style=INCIDENT)
    table.add_column("Technique", width=24, style=WARNING)
    table.add_column("Tactic", width=22)
    table.add_column("Confidence", justify="right", width=12, style=ACCENT)
    table.add_column("Evidence")
    rows = 0
    for incident in incidents_list:
        for technique in map_findings(incident.findings):
            table.add_row(incident.id, f"{technique.id} {technique.name}", Text(technique.tactic), f"{technique.confidence}%", Text(technique.evidence))
            rows += 1
    if not rows:
        table.add_row("-", "-", "-", "-", Text("No evidence-supported ATT&CK mappings found", style=MUTED))
    console.print(table)


def intel_entities(path: Path = typer.Argument(..., exists=True, dir_okay=False)) -> None:
    """Show IP and user entity intelligence extracted from a log file."""
    _, _, profiles = load_investigation(path)
    table = Table(title="Entity intelligence", title_style=f"bold {ACCENT}", expand=True, border_style=ACCENT_SOFT)
    table.add_column("Type", width=10, style=ACCENT)
    table.add_column("Entity", width=24)
    table.add_column("Occurrences", justify="right", width=12, style=ACCENT)
    table.add_column("Services")
    table.add_column("First", justify="right", width=8)
    table.add_column("Last", justify="right", width=8)
    for item in profiles:
        table.add_row(item.kind.upper(), Text(item.value), str(item.occurrences), Text(", ".join(item.services)), str(item.first_seen), str(item.last_seen))
    if not profiles:
        table.add_row("-", Text("No IP/user entities extracted", style=MUTED), "0", "-", "-", "-")
    console.print(table)
