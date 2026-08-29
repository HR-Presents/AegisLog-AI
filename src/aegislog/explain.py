from __future__ import annotations

from dataclasses import dataclass

from .investigation import InvestigationIncident
from .mitre import MitreTechnique, map_findings


@dataclass(frozen=True)
class IncidentExplanation:
    headline: str
    summary: str
    why_it_matters: str
    evidence: tuple[str, ...]
    techniques: tuple[MitreTechnique, ...]
    next_steps: tuple[str, ...]
    caveat: str


def _summary(incident: InvestigationIncident, techniques: tuple[MitreTechnique, ...]) -> str:
    entities = ", ".join(incident.entities[:3])
    entity_text = f" involving {entities}" if entities else ""
    attack_text = ""
    if techniques:
        attack_text = f" The evidence is consistent with {', '.join(item.name for item in techniques[:2])}."
    return (
        f"AegisLog correlated {len(incident.findings)} detection signal(s) into a {incident.severity.lower()}-severity "
        f"{incident.category} incident{entity_text}. Confidence is {incident.confidence}%.{attack_text}"
    )


def _why_it_matters(incident: InvestigationIncident, techniques: tuple[MitreTechnique, ...]) -> str:
    severity = incident.severity.upper()
    if techniques:
        tactics = ", ".join(dict.fromkeys(item.tactic for item in techniques))
        return (
            f"This activity touches ATT&CK tactic context including {tactics}. A {severity} incident deserves review because "
            "multiple log signals may represent coordinated hostile activity rather than an isolated operational error."
        )
    return (
        f"This is a {severity} incident because the available log evidence crossed AegisLog detection thresholds. "
        "No evidence-supported ATT&CK technique was mapped, so treat it as an investigation lead rather than proof of an attack."
    )


def _evidence(incident: InvestigationIncident) -> tuple[str, ...]:
    rows: list[str] = []
    for finding in incident.findings[:6]:
        text = finding.evidence.strip() or finding.title
        rows.append(f"{finding.severity}: {finding.title} — {text[:220]}")
    if incident.timeline:
        first = incident.timeline[0]
        last = incident.timeline[-1]
        rows.append(f"Timeline spans {first.timestamp} to {last.timestamp} across {len(incident.timeline)} related event(s).")
    return tuple(rows)


def _next_steps(incident: InvestigationIncident, techniques: tuple[MitreTechnique, ...]) -> tuple[str, ...]:
    steps: list[str] = [
        "Validate the source log and timestamps against the host or service that produced them.",
        "Review the associated IP addresses, users, services and nearby events for corroborating activity.",
    ]
    ids = {item.id for item in techniques}
    if any(item.startswith("T1110") for item in ids):
        steps.append("Review authentication history for the affected account(s) and source IP(s), including any successful logins after the failures.")
    if "T1552.001" in ids:
        steps.append("Check whether the probed file or path was actually exposed or returned sensitive content; do not assume access from the probe alone.")
    if "T1190" in ids:
        steps.append("Review web/application access logs around the probe for follow-on requests, unusual status codes, spawned processes or authentication changes.")
    if any(item.startswith("T1059") for item in ids):
        steps.append("Correlate command execution with process, parent-process and user/session telemetry where available.")
    if "T1548" in ids:
        steps.append("Review privilege-elevation events and confirm whether the user, command and timing were expected.")
    steps.append("Preserve relevant logs and evidence before making changes; escalate only when corroborating evidence supports it.")
    return tuple(steps[:6])


def explain_incident(incident: InvestigationIncident) -> IncidentExplanation:
    techniques = map_findings(incident.findings)
    return IncidentExplanation(
        headline=f"{incident.id}: {incident.title}",
        summary=_summary(incident, techniques),
        why_it_matters=_why_it_matters(incident, techniques),
        evidence=_evidence(incident),
        techniques=techniques,
        next_steps=_next_steps(incident, techniques),
        caveat=(
            "This explanation is generated locally from the available log evidence. It does not prove compromise, identify an attacker, "
            "or replace validation against host, identity, network and application telemetry. No log content is sent to an external AI service."
        ),
    )
