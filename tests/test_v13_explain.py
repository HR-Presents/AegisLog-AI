from __future__ import annotations

from aegislog.explain import explain_incident
from aegislog.investigation import build_incidents


def _auth_incident():
    lines = [
        f"Aug 29 12:01:0{i} demo sshd[10{i}]: Failed password for root from 203.0.113.7 port 22 ssh2\n"
        for i in range(1, 7)
    ]
    incidents = build_incidents(lines)
    assert incidents
    return incidents[0]


def test_explanation_is_local_and_evidence_led() -> None:
    result = explain_incident(_auth_incident())
    assert "confidence" in result.summary.lower()
    assert result.evidence
    assert result.next_steps
    assert "No log content is sent to an external AI service" in result.caveat


def test_explanation_includes_mitre_context_when_supported() -> None:
    result = explain_incident(_auth_incident())
    assert any(item.id == "T1110" for item in result.techniques)
    assert "Credential Access" in result.why_it_matters


def test_explanation_recommends_authentication_validation_for_bruteforce() -> None:
    result = explain_incident(_auth_incident())
    assert any("successful logins" in step for step in result.next_steps)
