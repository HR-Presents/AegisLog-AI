from __future__ import annotations

import json

import pytest

from aegislog import native_collectors
from aegislog.native_collectors import CollectorError
from aegislog.parsers import parse_line


def test_windows_event_output_is_normalized_and_parseable(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = [{
        "TimeCreated": "/Date(1787987725199)/",
        "Id": 134,
        "LevelDisplayName": "Warning",
        "ProviderName": "Microsoft-Windows-Time-Service",
        "Message": "NtpClient was unable to resolve time.windows.com",
    }]
    monkeypatch.setattr(native_collectors.os, "name", "nt")
    monkeypatch.setattr(native_collectors, "_run", lambda *_args, **_kwargs: json.dumps(payload))

    line = native_collectors.windows_event_logs(channel="System")[0]
    event = parse_line(line)

    assert "/Date(" not in line
    assert "Microsoft-Windows-Time-Service[134]" in line
    assert event.source == "windows"
    assert event.service == "Microsoft-Windows-Time-Service"
    assert event.level == "warning"


def test_windows_security_permission_error_is_friendly(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(native_collectors.os, "name", "nt")

    def denied(*_args, **_kwargs):
        raise CollectorError("Get-WinEvent : Attempted to perform an unauthorized operation. UnauthorizedAccessException")

    monkeypatch.setattr(native_collectors, "_run", denied)
    with pytest.raises(CollectorError) as exc_info:
        native_collectors.windows_event_logs(channel="Security")

    message = str(exc_info.value)
    assert "Security Event Log" in message
    assert "administrator" in message.lower()
    assert "Get-WinEvent" not in message
    assert "UnauthorizedAccessException" not in message


def test_docker_status_is_not_unconditionally_ready(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(native_collectors.shutil, "which", lambda _name: None)
    docker = next(source for source in native_collectors.source_status() if source.name == "docker")
    assert docker.available is False
    assert "not found" in docker.detail.lower()
