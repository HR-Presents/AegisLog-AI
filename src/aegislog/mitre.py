from __future__ import annotations

from dataclasses import dataclass

from .engine import Finding


@dataclass(frozen=True)
class MitreTechnique:
    id: str
    name: str
    tactic: str
    confidence: int
    evidence: str


_RULES: tuple[tuple[tuple[str, ...], str, str, str], ...] = (
    (("failed password", "authentication failure", "brute force"), "T1110", "Brute Force", "Credential Access"),
    (("password spraying",), "T1110.003", "Password Spraying", "Credential Access"),
    (("credential stuffing",), "T1110.004", "Credential Stuffing", "Credential Access"),
    (("invalid user", "account enumeration"), "T1087", "Account Discovery", "Discovery"),
    (("/etc/passwd", "system owner/user discovery"), "T1033", "System Owner/User Discovery", "Discovery"),
    ((".env", "environment file", "credential file"), "T1552.001", "Credentials In Files", "Credential Access"),
    (("wp-login.php", "admin login", "login probe"), "T1190", "Exploit Public-Facing Application", "Initial Access"),
    (("path traversal", "../", "directory traversal"), "T1190", "Exploit Public-Facing Application", "Initial Access"),
    (("sql injection", "union select", "sql probe"), "T1190", "Exploit Public-Facing Application", "Initial Access"),
    (("powershell",), "T1059.001", "PowerShell", "Execution"),
    (("cmd.exe", "command shell"), "T1059.003", "Windows Command Shell", "Execution"),
    (("cron", "scheduled task", "scheduled job"), "T1053", "Scheduled Task/Job", "Persistence"),
    (("service created", "new service", "systemd service"), "T1543", "Create or Modify System Process", "Persistence"),
    (("sudo", "privilege escalation"), "T1548", "Abuse Elevation Control Mechanism", "Privilege Escalation"),
    (("firewall block", "ufw block", "blocked connection"), "T1046", "Network Service Discovery", "Discovery"),
)


def map_findings(findings: tuple[Finding, ...] | list[Finding]) -> tuple[MitreTechnique, ...]:
    mapped: dict[str, MitreTechnique] = {}
    for finding in findings:
        haystack = f"{finding.title} {finding.category} {finding.evidence}".lower()
        for needles, technique_id, name, tactic in _RULES:
            if not any(needle in haystack for needle in needles):
                continue
            score = 88 if len(needles) == 1 and needles[0] in haystack else 80
            candidate = MitreTechnique(technique_id, name, tactic, score, finding.title)
            existing = mapped.get(technique_id)
            if existing is None or candidate.confidence > existing.confidence:
                mapped[technique_id] = candidate
    return tuple(sorted(mapped.values(), key=lambda item: (-item.confidence, item.tactic, item.id)))
