from __future__ import annotations

from aegislog.engine import analyze_lines
from aegislog.windows_security import parse_windows_security_line, signal_for_event


def test_parse_failed_logon_fields() -> None:
    line = (
        "2026-08-29T12:00:00Z Microsoft-Windows-Security-Auditing[4625]: INFO "
        "An account failed to log on. Account Name: alice Workstation Name: LAPTOP01 "
        "Source Network Address: 203.0.113.50"
    )
    event = parse_windows_security_line(line)
    assert event is not None
    assert event.event_id == 4625
    assert event.account == "alice"
    assert event.workstation == "LAPTOP01"
    assert event.source_ip == "203.0.113.50"


def test_failed_logons_correlate_by_source_ip() -> None:
    lines = [
        (
            "2026-08-29T12:00:00Z Microsoft-Windows-Security-Auditing[4625]: INFO "
            "An account failed to log on. Account Name: alice Source Network Address: 203.0.113.50\n"
        )
        for _ in range(6)
    ]
    findings = analyze_lines(lines)
    assert findings[0].category == "authentication"
    assert findings[0].severity == "HIGH"
    assert "203.0.113.50" in findings[0].title
    assert "6 authentication failures" in findings[0].evidence


def test_audit_log_clear_is_critical() -> None:
    line = (
        "2026-08-29T12:00:00Z Microsoft-Windows-Security-Auditing[1102]: INFO "
        "The audit log was cleared. Account Name: administrator"
    )
    event = parse_windows_security_line(line)
    assert event is not None
    signal = signal_for_event(event)
    assert signal is not None
    assert signal.severity == "CRITICAL"
    assert signal.category == "audit"
    assert "Event ID 1102" in signal.evidence


def test_account_creation_is_high_priority() -> None:
    line = (
        "2026-08-29T12:00:00Z Microsoft-Windows-Security-Auditing[4720]: INFO "
        "A user account was created. New Account Name: temp-admin"
    )
    findings = analyze_lines([line])
    assert len(findings) == 1
    assert findings[0].severity == "HIGH"
    assert findings[0].category == "account"
    assert "temp-admin" in findings[0].evidence
