from aegislog.engine import Finding
from aegislog.incidents import correlate


def test_correlates_by_category_and_uses_highest_severity():
    findings = [
        Finding("MEDIUM", "auth", "Failure", "one", "review"),
        Finding("CRITICAL", "auth", "Brute force", "two", "review"),
        Finding("MEDIUM", "service", "Crash", "three", "review"),
    ]
    incidents = correlate(findings)
    assert len(incidents) == 2
    assert incidents[0].severity == "CRITICAL"
    assert incidents[0].count == 2
