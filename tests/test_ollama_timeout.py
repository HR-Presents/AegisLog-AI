from unittest.mock import patch

import pytest

from aegislog.providers import AIResponse, ProviderError, _ollama_timeout_seconds, ollama


def test_ollama_timeout_defaults_to_120_seconds(monkeypatch):
    monkeypatch.delenv("AEGISLOG_OLLAMA_TIMEOUT_SECONDS", raising=False)
    assert _ollama_timeout_seconds() == 120


def test_ollama_timeout_can_be_overridden(monkeypatch):
    monkeypatch.setenv("AEGISLOG_OLLAMA_TIMEOUT_SECONDS", "240")
    assert _ollama_timeout_seconds() == 240


@pytest.mark.parametrize("value", ["0", "601", "not-a-number"])
def test_ollama_timeout_rejects_invalid_values(monkeypatch, value):
    monkeypatch.setenv("AEGISLOG_OLLAMA_TIMEOUT_SECONDS", value)
    with pytest.raises(ProviderError, match="AEGISLOG_OLLAMA_TIMEOUT_SECONDS"):
        _ollama_timeout_seconds()


def test_ollama_uses_local_timeout_without_changing_remote_default(monkeypatch):
    monkeypatch.delenv("AEGISLOG_OLLAMA_TIMEOUT_SECONDS", raising=False)
    with patch("aegislog.providers._post_json", return_value={"response": "model ready"}) as post_json:
        response = ollama("investigate", "llama3.2")

    assert response == AIResponse("ollama", "llama3.2", "model ready")
    post_json.assert_called_once()
    assert post_json.call_args.kwargs["timeout"] == 120
    assert post_json.call_args.kwargs["allow_local"] is True


def test_ollama_timeout_error_explains_slow_model_and_override(monkeypatch):
    monkeypatch.delenv("AEGISLOG_OLLAMA_TIMEOUT_SECONDS", raising=False)
    with patch(
        "aegislog.providers._post_json",
        side_effect=ProviderError("provider connection failed for all validated addresses: 127.0.0.1: timed out"),
    ):
        with pytest.raises(ProviderError) as exc_info:
            ollama("investigate", "llama3.2")

    message = str(exc_info.value)
    assert "did not respond within 120 seconds" in message
    assert "running slowly on CPU" in message
    assert "AEGISLOG_OLLAMA_TIMEOUT_SECONDS" in message
