from aegislog.engine import analyze_lines


def test_finding_evidence_strips_ansi():
    findings = analyze_lines(["api: ERROR \x1b[31mdatabase failed\x1b[0m"])
    assert findings
    assert "\x1b" not in findings[0].evidence
