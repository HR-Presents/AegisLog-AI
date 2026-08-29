from aegislog.engine import analyze_lines
from aegislog.incidents import correlate


def test_auth_findings_create_incident():
    lines = [f"sshd: Failed password for root from 192.0.2.10 port {i}" for i in range(5)]
    findings = analyze_lines(lines)
    incidents = correlate(findings)
    assert incidents
    assert any(item.category == "authentication" for item in incidents)
