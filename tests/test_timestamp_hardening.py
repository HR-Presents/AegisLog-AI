from aegislog.engine import AnalysisState, analyze_lines


def _auth(findings):
    return next(item for item in findings if item.category == "authentication")


def test_rfc3164_uses_explicit_year_hint_for_event_time_window():
    findings = analyze_lines(
        [
            "Sep  7 10:00:00 host sshd: Failed password for root from 203.0.113.50 port 22",
            "Sep  7 10:00:30 host sshd: Failed password for root from 203.0.113.50 port 22",
            "Sep  7 10:10:00 host sshd: Failed password for root from 203.0.113.50 port 22",
        ],
        auth_window_seconds=60,
        timestamp_year_hint=2026,
    )
    auth = _auth(findings)
    assert auth.severity == "LOW"
    assert "1 authentication failure" in auth.evidence
    assert "window=60s" in auth.evidence
    assert "timestamp unavailable" not in auth.evidence


def test_rfc3164_inherits_year_only_after_absolute_timestamp_observed():
    state = AnalysisState(auth_window_seconds=60)
    state.process("2026-09-07T09:59:50Z app: INFO analysis anchor")
    state.process("Sep  7 10:00:00 host sshd: Failed password for root from 203.0.113.51 port 22")
    state.process("Sep  7 10:00:30 host sshd: Failed password for root from 203.0.113.51 port 22")
    auth = _auth(state.findings())
    assert auth.severity == "MEDIUM"
    assert "2 authentication failures" in auth.evidence
    assert "window=60s" in auth.evidence


def test_rfc3164_without_year_context_keeps_explicit_fallback():
    auth = _auth(
        analyze_lines(
            ["Sep  7 10:00:00 host sshd: Failed password for root from 203.0.113.52 port 22"]
        )
    )
    assert "timestamp unavailable; correlated by bounded event order" in auth.evidence


def test_out_of_order_event_inside_window_is_retained_and_sorted():
    state = AnalysisState(auth_window_seconds=120)
    state.process("2026-09-07T10:02:00Z sshd: Failed password for root from 203.0.113.60 port 22")
    state.process("2026-09-07T10:01:00Z sshd: Failed password for root from 203.0.113.60 port 22")

    auth = _auth(state.findings())
    assert auth.severity == "MEDIUM"
    assert "2 authentication failures" in auth.evidence
    assert "2026-09-07T10:02:00Z" in auth.evidence


def test_out_of_order_event_older_than_current_window_is_expired():
    state = AnalysisState(auth_window_seconds=60)
    state.process("2026-09-07T10:05:00Z sshd: Failed password for root from 203.0.113.61 port 22")
    state.process("2026-09-07T10:00:00Z sshd: Failed password for root from 203.0.113.61 port 22")

    auth = _auth(state.findings())
    assert auth.severity == "LOW"
    assert "1 authentication failure" in auth.evidence
    assert state.expired_auth_events == 1


def test_missing_timestamp_events_use_bounded_event_order_fallback():
    state = AnalysisState(max_auth_events=3)
    for index in range(5):
        state.process(f"sshd: Failed password for root from 203.0.113.62 port {2200 + index}")

    auth = _auth(state.findings())
    assert "3 authentication failures" in auth.evidence
    assert "timestamp unavailable; correlated by bounded event order" in auth.evidence
    assert state.dropped_auth_events == 2


def test_events_exactly_on_window_boundary_are_retained():
    findings = analyze_lines(
        [
            "2026-09-07T10:00:00Z sshd: Failed password for root from 203.0.113.63 port 22",
            "2026-09-07T10:01:00Z sshd: Failed password for root from 203.0.113.63 port 22",
        ],
        auth_window_seconds=60,
    )
    auth = _auth(findings)
    assert auth.severity == "MEDIUM"
    assert "2 authentication failures" in auth.evidence
