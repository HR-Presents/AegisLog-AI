import io
import json
from unittest.mock import MagicMock, patch

import pytest

from aegislog.engine import AnalysisState, analyze_file, analyze_lines
from aegislog.providers import ProviderError, _post_json, openai_compatible
from aegislog.sanitize import redact_sensitive
from aegislog.streaming import analyze_stream


def _shape(findings):
    return [(item.severity, item.category, item.title, item.evidence) for item in findings]


def test_streaming_results_are_independent_of_chunk_size(tmp_path):
    path = tmp_path / "auth.log"
    lines = [
        f"2026-09-07T10:00:0{i}Z sshd: Failed password for root from 203.0.113.7 port {2200 + i}\n"
        for i in range(6)
    ] + ["2026-09-07T10:01:00Z api: ERROR database timeout\n"]
    path.write_text("".join(lines), encoding="utf-8")

    full_count, full_findings = analyze_file(path)
    assert full_count == len(lines)
    for chunk_size in (1, 2, 3, len(lines)):
        streamed = analyze_stream(path, chunk_size=chunk_size)
        assert streamed.lines == full_count
        assert _shape(streamed.findings) == _shape(full_findings)


def test_auth_source_parsing_uses_one_validated_ipv6_source_not_destination_or_duplicates():
    lines = [
        "2026-09-07T10:00:00Z sshd: Failed password for root from 2001:db8::7 port 22 dst=192.0.2.10 repeated=2001:db8::7",
        "2026-09-07T10:00:01Z sshd: Failed password for root from 2001:db8::7 port 22 dst=192.0.2.10 repeated=2001:db8::7",
    ]
    findings = analyze_lines(lines)
    auth = [item for item in findings if item.category == "authentication"]
    assert len(auth) == 1
    assert "2001:db8::7" in auth[0].title
    assert "2 authentication failures" in auth[0].evidence
    assert "192.0.2.10" not in auth[0].title


def test_invalid_source_address_is_not_counted_as_an_ip():
    findings = analyze_lines(["2026-09-07T10:00:00Z sshd: Failed password for root from 999.999.1.1 port 22"])
    auth = next(item for item in findings if item.category == "authentication")
    assert "unparsed source" in auth.title


def test_single_auth_failure_is_low_context_not_medium_alert():
    auth = next(
        item
        for item in analyze_lines(
            ["2026-09-07T10:00:00Z sshd: Failed password for alice from 203.0.113.20 port 2210"]
        )
        if item.category == "authentication"
    )
    assert auth.severity == "LOW"
    assert "Authentication failure observed" in auth.title


def test_auth_window_expires_old_events_and_does_not_escalate_whole_input():
    lines = [
        "2026-09-07T10:00:00Z sshd: Failed password for root from 203.0.113.9 port 22",
        "2026-09-07T10:00:10Z sshd: Failed password for root from 203.0.113.9 port 22",
        "2026-09-07T10:00:20Z sshd: Failed password for root from 203.0.113.9 port 22",
        "2026-09-07T10:00:30Z sshd: Failed password for root from 203.0.113.9 port 22",
        "2026-09-07T10:10:00Z sshd: Failed password for root from 203.0.113.9 port 22",
    ]
    auth = next(item for item in analyze_lines(lines, auth_window_seconds=60) if item.category == "authentication")
    assert auth.severity == "LOW"
    assert "1 authentication failure" in auth.evidence


def test_out_of_order_events_inside_window_are_kept_but_expired_events_are_ignored():
    lines = [
        "2026-09-07T10:05:00Z sshd: Failed password for root from 203.0.113.11 port 22",
        "2026-09-07T10:04:30Z sshd: Failed password for root from 203.0.113.11 port 22",
        "2026-09-07T10:00:00Z sshd: Failed password for root from 203.0.113.11 port 22",
    ]
    auth = next(item for item in analyze_lines(lines, auth_window_seconds=60) if item.category == "authentication")
    assert auth.severity == "MEDIUM"
    assert "2 authentication failures" in auth.evidence


def test_missing_timestamps_use_explicit_bounded_event_order_behavior():
    lines = [f"sshd: Failed password for root from 203.0.113.12 port {2200 + i}" for i in range(6)]
    auth = next(item for item in analyze_lines(lines) if item.category == "authentication")
    assert auth.severity == "HIGH"
    assert "timestamp unavailable; correlated by bounded event order" in auth.evidence


def test_sudo_auth_failure_keeps_specific_privilege_classification():
    finding = analyze_lines(
        ["2026-09-07T11:00:00Z sudo: pam_unix(sudo:auth): authentication failure; user=alice"]
    )[0]
    assert finding.category == "privilege"
    assert finding.severity == "HIGH"


def test_single_wp_login_request_is_low_severity_not_high():
    finding = analyze_lines(['198.51.100.2 - - [07/Sep/2026] "GET /wp-login.php HTTP/1.1" 200 123'])[0]
    assert finding.category == "web"
    assert finding.severity == "LOW"
    assert "endpoint requested" in finding.title.lower()


def test_redaction_covers_nested_json_headers_urls_cookies_and_common_tokens():
    synthetic = {
        "outer": {
            "password": "synthetic-password",
            "authorization": "Bearer synthetic-bearer-token",
            "child": {"api_key": "sk-ABCDEFGHIJKLMNOPQRSTUV"},
        },
        "url": "https://alice:synthetic-url-password@example.test/path",
        "cookie": "session=synthetic-cookie",
    }
    redacted = redact_sensitive(json.dumps(synthetic))
    for secret in (
        "synthetic-password",
        "synthetic-bearer-token",
        "sk-ABCDEFGHIJKLMNOPQRSTUV",
        "synthetic-url-password",
        "synthetic-cookie",
    ):
        assert secret not in redacted

    headers = redact_sensitive(
        "Authorization: Bearer synthetic-token Cookie: session=abc123 token=synthetic-value"
    )
    assert "synthetic-token" not in headers
    assert "abc123" not in headers
    assert "synthetic-value" not in headers


def test_remote_provider_rejects_plain_http():
    with pytest.raises(ProviderError, match="require HTTPS"):
        with patch("aegislog.providers.socket.getaddrinfo", return_value=[(2, 1, 6, "", ("93.184.216.34", 80))]):
            _post_json("http://provider.example/v1", {}, {}, allow_local=False)


def test_outgoing_openai_prompt_is_redacted_before_transport(monkeypatch):
    monkeypatch.setenv("AEGISLOG_API_KEY", "synthetic-api-key")
    captured = {}

    def fake_post(url, payload, headers, timeout=45, allow_local=False):
        captured["payload"] = payload
        return {"choices": [{"message": {"content": "ok"}}]}

    monkeypatch.setattr("aegislog.providers._post_json", fake_post)
    response = openai_compatible("password=synthetic-password Authorization: Bearer synthetic-token", "model")
    sent = captured["payload"]["messages"][0]["content"]
    assert "synthetic-password" not in sent
    assert "synthetic-token" not in sent
    assert response.text == "ok"


def test_post_json_connects_to_validated_address_without_second_dns_lookup():
    parsed = __import__("urllib.parse").parse.urlparse("https://provider.example/v1")
    response = MagicMock()
    response.status = 200
    response.getheader.return_value = None
    response.read.return_value = io.BytesIO(b"{}").getvalue()
    connection = MagicMock()
    connection.getresponse.return_value = response

    with patch(
        "aegislog.providers._validated_endpoint",
        return_value=(parsed, {__import__("ipaddress").ip_address("93.184.216.34")}),
    ), patch("aegislog.providers._PinnedHTTPSConnection", return_value=connection) as connection_cls:
        assert _post_json("https://provider.example/v1", {}, {}) == {}
        connection_cls.assert_called_once_with("provider.example", 443, "93.184.216.34", 45)


def test_provider_rejects_malformed_response_shape(monkeypatch):
    monkeypatch.setenv("AEGISLOG_API_KEY", "synthetic-api-key")
    monkeypatch.setattr("aegislog.providers._post_json", lambda *args, **kwargs: {"choices": []})
    with pytest.raises(ProviderError, match="unexpected response shape"):
        openai_compatible("safe prompt", "model")


def test_auth_state_is_globally_bounded_across_many_timestamp_less_sources():
    state = AnalysisState(max_auth_events=10, max_auth_sources=4)
    for i in range(25):
        state.process(f"sshd: Failed password for root from 198.51.100.{(i % 20) + 1} port {2200 + i}")

    assert len(set(state._auth) | set(state._missing_ts)) <= 4
    assert sum(len(events) for events in state._auth.values()) + sum(
        len(events) for events in state._missing_ts.values()
    ) <= 10
    assert state.dropped_auth_sources > 0
    assert state.dropped_auth_events > 0


def test_non_auth_findings_are_bounded_during_ingest_not_only_on_output():
    state = AnalysisState(max_findings=3)
    for i in range(20):
        state.process(f"2026-09-07T12:00:{i:02d}Z app: ERROR synthetic failure {i}")

    findings = state.findings()
    assert len([item for item in findings if item.category == "error"]) == 3
    assert state.dropped_findings == 17


def test_stream_reports_findings_dropped_during_ingest(tmp_path):
    path = tmp_path / "errors.log"
    path.write_text("".join(f"app: ERROR synthetic failure {i}\n" for i in range(10)), encoding="utf-8")
    result = analyze_stream(path, max_findings=3)
    assert len(result.findings) == 3
    assert result.dropped_findings == 7
