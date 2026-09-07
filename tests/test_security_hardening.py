import io
import json
from unittest.mock import MagicMock, patch

import pytest

from aegislog.engine import analyze_file, analyze_lines
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
    assert "2 failures" in auth[0].evidence
    assert "192.0.2.10" not in auth[0].title


def test_invalid_source_address_is_not_counted_as_an_ip():
    findings = analyze_lines(["2026-09-07T10:00:00Z sshd: Failed password for root from 999.999.1.1 port 22"])
    auth = next(item for item in findings if item.category == "authentication")
    assert "unparsed source" in auth.title


def test_auth_window_expires_old_events_and_does_not_escalate_whole_input():
    lines = [
        "2026-09-07T10:00:00Z sshd: Failed password for root from 203.0.113.9 port 22",
        "2026-09-07T10:00:10Z sshd: Failed password for root from 203.0.113.9 port 22",
        "2026-09-07T10:00:20Z sshd: Failed password for root from 203.0.113.9 port 22",
        "2026-09-07T10:00:30Z sshd: Failed password for root from 203.0.113.9 port 22",
        "2026-09-07T10:10:00Z sshd: Failed password for root from 203.0.113.9 port 22",
    ]
    auth = next(item for item in analyze_lines(lines, auth_window_seconds=60) if item.category == "authentication")
    assert auth.severity == "MEDIUM"
    assert "1 failures" in auth.evidence


def test_out_of_order_events_inside_window_are_kept_but_expired_events_are_ignored():
    lines = [
        "2026-09-07T10:05:00Z sshd: Failed password for root from 203.0.113.11 port 22",
        "2026-09-07T10:04:30Z sshd: Failed password for root from 203.0.113.11 port 22",
        "2026-09-07T10:00:00Z sshd: Failed password for root from 203.0.113.11 port 22",
    ]
    auth = next(item for item in analyze_lines(lines, auth_window_seconds=60) if item.category == "authentication")
    assert "2 failures" in auth.evidence


def test_missing_timestamps_use_explicit_bounded_event_order_behavior():
    lines = [f"sshd: Failed password for root from 203.0.113.12 port {2200 + i}" for i in range(6)]
    auth = next(item for item in analyze_lines(lines) if item.category == "authentication")
    assert auth.severity == "HIGH"
    assert "timestamp unavailable; correlated by bounded event order" in auth.evidence


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
    response.read.return_value = io.BytesIO(b'{}').getvalue()
    connection = MagicMock()
    connection.getresponse.return_value = response

    with patch("aegislog.providers._validated_endpoint", return_value=(parsed, {__import__("ipaddress").ip_address("93.184.216.34")})), patch(
        "aegislog.providers._PinnedHTTPSConnection", return_value=connection
    ) as connection_cls:
        assert _post_json("https://provider.example/v1", {}, {}) == {}
        connection_cls.assert_called_once_with("provider.example", 443, "93.184.216.34", 45)


def test_provider_rejects_malformed_response_shape(monkeypatch):
    monkeypatch.setenv("AEGISLOG_API_KEY", "synthetic-api-key")
    monkeypatch.setattr("aegislog.providers._post_json", lambda *args, **kwargs: {"choices": []})
    with pytest.raises(ProviderError, match="unexpected response shape"):
        openai_compatible("safe prompt", "model")
