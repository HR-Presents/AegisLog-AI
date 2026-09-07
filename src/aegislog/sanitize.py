from __future__ import annotations

import json
import re
from typing import Any

ANSI_ESCAPE = re.compile(r"\x1b(?:\[[0-?]*[ -/]*[@-~]|\][^\x07\x1b]*(?:\x07|\x1b\\)?)")
CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

_SENSITIVE_KEYS = {
    "authorization", "password", "passwd", "pwd", "secret", "token", "access_token",
    "refresh_token", "api_key", "apikey", "client_secret", "cookie", "set-cookie",
}
_KEY_VALUE = re.compile(
    r"(?i)(?P<key>authorization|password|passwd|pwd|secret|token|access[_-]?token|refresh[_-]?token|api[_-]?key|apikey|client[_-]?secret|cookie|set-cookie)"
    r"(?P<sep>\s*[:=]\s*)(?P<quote>[\"']?)(?P<value>[^\s,;\"']+|[^\"']*)(?P=quote)"
)
_BEARER = re.compile(r"(?i)\b(Bearer|Basic)\s+[A-Za-z0-9._~+/=-]+")
_URL_CREDS = re.compile(r"(?P<scheme>https?://)(?P<user>[^\s/@:]+):(?P<password>[^\s/@]+)@", re.I)
_JWT = re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b")
_COMMON_TOKENS = re.compile(
    r"\b(?:sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16})\b"
)


def terminal_safe(text: str) -> str:
    """Remove ANSI/terminal escape sequences and remaining control bytes."""
    return CONTROL.sub("", ANSI_ESCAPE.sub("", text))


def _redact_structured(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: "[REDACTED]" if str(key).lower() in _SENSITIVE_KEYS else _redact_structured(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_redact_structured(item) for item in value]
    if isinstance(value, str):
        return _redact_unstructured(value)
    return value


def _redact_unstructured(text: str) -> str:
    text = _URL_CREDS.sub(lambda m: f"{m.group('scheme')}{m.group('user')}:[REDACTED]@", text)
    text = _BEARER.sub(lambda m: f"{m.group(1)} [REDACTED]", text)
    text = _KEY_VALUE.sub(lambda m: f"{m.group('key')}{m.group('sep')}[REDACTED]", text)
    text = _JWT.sub("[REDACTED]", text)
    return _COMMON_TOKENS.sub("[REDACTED]", text)


def redact_sensitive(text: str) -> str:
    """Central redaction for terminal output and all AI-bound context.

    Valid JSON is parsed so nested sensitive fields are removed before serialization.
    Non-JSON text is covered by conservative credential/header/token patterns.
    """
    safe = terminal_safe(text)
    stripped = safe.strip()
    if stripped and stripped[0] in "[{":
        try:
            parsed = json.loads(stripped)
        except (json.JSONDecodeError, TypeError):
            pass
        else:
            return json.dumps(_redact_structured(parsed), ensure_ascii=False, separators=(",", ":"))
    return _redact_unstructured(safe)
