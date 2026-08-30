from rich.console import Console

from aegislog.engine import Finding
from aegislog.realtime import RealtimeState, render_realtime


def _brute_force_line(port: int) -> str:
    return f"Aug 29 21:55:0{port % 10} server sshd[100{port % 10}]: Failed password for admin from 203.0.113.50 port {port} ssh2\n"


def test_recent_live_finding_replaces_growing_duplicate() -> None:
    state = RealtimeState(source="security.log", watch_profile="security")
    state.ingest([_brute_force_line(port) for port in range(50001, 50006)], now=10.0)
    state.ingest([_brute_force_line(50006)], now=11.0)

    brute = [item for item in state.recent_findings if "brute-force" in item.title.lower()]
    assert len(brute) == 1
    assert "6 authentication failures" in brute[0].evidence


def test_live_dashboard_explains_waiting_for_new_lines() -> None:
    state = RealtimeState(source="security.log", watch_profile="security")
    console = Console(record=True, width=180)
    console.print(render_realtime(state))
    output = console.export_text()

    assert "Waiting for NEW lines appended after monitoring started" in output
    assert "Existing file contents are intentionally skipped unless --from-start is used" in output
    assert "Average rate" in output


def test_finding_key_ignores_evidence_growth() -> None:
    first = Finding(
        "HIGH",
        "authentication",
        "Possible brute-force activity from 203.0.113.50",
        "5 authentication failures",
        "Review authentication activity.",
    )
    second = Finding(
        "HIGH",
        "authentication",
        "Possible brute-force activity from 203.0.113.50",
        "6 authentication failures",
        "Review authentication activity.",
    )
    assert RealtimeState._finding_key(first) == RealtimeState._finding_key(second)
