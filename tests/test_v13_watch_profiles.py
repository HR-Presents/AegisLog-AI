from pathlib import Path

import pytest

from aegislog.engine import Finding
from aegislog.multisource import MultiSourceState
from aegislog.parsers import Event
from aegislog.realtime import RealtimeState
from aegislog.watch_profiles import event_matches, finding_matches, get_profile, profile_choices


def _finding(category: str, title: str, evidence: str) -> Finding:
    return Finding("MEDIUM", category, title, evidence, "Review the related activity.")


def test_profile_catalog_contains_expected_modes() -> None:
    assert profile_choices() == ("all", "security", "authentication", "web", "docker", "operations")
    assert get_profile("AUTHENTICATION").key == "authentication"


def test_unknown_profile_is_rejected() -> None:
    with pytest.raises(ValueError, match="Unknown watch profile"):
        get_profile("offensive")


def test_authentication_profile_focuses_auth_activity() -> None:
    profile = get_profile("authentication")
    auth = _finding("authentication", "Possible brute-force activity", "6 authentication failures from 203.0.113.8")
    web = _finding("web", "Suspicious web probing detected", "GET /.env")
    assert finding_matches(profile, auth)
    assert not finding_matches(profile, web)


def test_web_and_docker_profiles_focus_matching_events() -> None:
    web = get_profile("web")
    docker = get_profile("docker")
    nginx = Event(raw="x", service="nginx", level="warning", message="GET /.env 404")
    container = Event(raw="x", service="dockerd", level="error", message="container restart failed")
    assert event_matches(web, nginx)
    assert not event_matches(web, container)
    assert event_matches(docker, container)


def test_realtime_state_filters_findings_without_dropping_input() -> None:
    state = RealtimeState(source="test.log", watch_profile="authentication")
    lines = [
        "Aug 29 12:01:01 demo sshd[1]: Failed password for root from 203.0.113.9 port 22 ssh2\n",
        "Aug 29 12:01:02 demo nginx[2]: ERROR GET /.env from 198.51.100.7\n",
    ]
    state.ingest(lines, now=10.0)
    assert state.total_lines == 2
    assert all(item.category == "authentication" for item in state.focused_findings)
    assert len(state.findings) >= len(state.focused_findings)


def test_multisource_profile_filters_alert_generation() -> None:
    state = MultiSourceState(
        sources=(Path("auth.log"), Path("web.log")),
        watch_profile="web",
    )
    state.ingest(Path("auth.log"), ["Failed password for root from 203.0.113.9\n"], now=10.0)
    state.ingest(Path("web.log"), ["198.51.100.7 - - [29/Aug/2026:12:00:00 +0000] \"GET /.env HTTP/1.1\" 404 12\n"], now=11.0)
    assert state.total_lines == 2
    assert all(item.category == "web" for item in state.focused_findings)
    assert all(item.category == "web" for item in state.alerts)


def test_profile_exposes_relevant_rate_metrics() -> None:
    assert get_profile("authentication").trend_metrics == ("Failed logins",)
    assert get_profile("operations").trend_metrics == ("Errors",)
    assert "Firewall blocks" in get_profile("security").trend_metrics
