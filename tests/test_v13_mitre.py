from __future__ import annotations

from aegislog.engine import Finding
from aegislog.mitre import map_findings


def _finding(severity: str, category: str, title: str, evidence: str) -> Finding:
    return Finding(severity, category, title, evidence, "Review supporting evidence")


def test_maps_bruteforce_to_t1110() -> None:
    findings = [_finding("HIGH", "auth", "SSH brute force", "Repeated failed password attempts")]
    techniques = map_findings(findings)
    assert any(item.id == "T1110" for item in techniques)


def test_maps_env_probe_to_credentials_in_files() -> None:
    findings = [_finding("HIGH", "web", "Suspicious .env probe", "GET /.env HTTP/1.1")]
    techniques = map_findings(findings)
    assert any(item.id == "T1552.001" for item in techniques)


def test_maps_web_probe_to_initial_access() -> None:
    findings = [_finding("HIGH", "web", "Suspicious wp-login.php probe", "GET /wp-login.php")]
    techniques = map_findings(findings)
    assert any(item.id == "T1190" and item.tactic == "Initial Access" for item in techniques)


def test_unrelated_operational_finding_is_not_forced_into_mitre() -> None:
    findings = [_finding("MEDIUM", "ops", "Database timeout", "connection timeout")]
    assert map_findings(findings) == ()
