from aegislog.engine import analyze_lines, redact


def test_bruteforce_detection():
    lines = [f"sshd: Failed password for root from 203.0.113.7 port {2200+i}" for i in range(6)]
    findings = analyze_lines(lines)
    assert any("brute-force" in finding.title.lower() for finding in findings)
    assert any(finding.severity == "HIGH" for finding in findings)


def test_error_detection():
    findings = analyze_lines(["api: ERROR database connection timeout"])
    assert findings
    assert findings[0].category == "error"


def test_secret_redaction():
    text = redact("api_key=supersecret password=hunter2")
    assert "supersecret" not in text
    assert "hunter2" not in text
