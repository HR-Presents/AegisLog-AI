from __future__ import annotations

import json

import pytest

from aegislog import native_collectors as nc


def test_windows_events_normalize_to_log_lines(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(nc.os, "name", "nt")
    payload = [{"TimeCreated": "2026-08-29T12:00:00", "Id": 4625, "LevelDisplayName": "Warning", "ProviderName": "Security", "Message": "Failed logon\nfor user"}]
    monkeypatch.setattr(nc, "_run", lambda command, timeout=15: json.dumps(payload))
    lines = nc.windows_event_logs(limit=10, channel="Security")
    assert len(lines) == 1
    assert "Security[4625]" in lines[0]
    assert "WARNING Failed logon for user" in lines[0]


def test_windows_channel_is_allowlisted(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(nc.os, "name", "nt")
    with pytest.raises(nc.CollectorError):
        nc.windows_event_logs(channel="System'; Remove-Item C:\\*")


def test_journald_uses_bounded_read(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(nc.platform, "system", lambda: "Linux")
    seen: list[str] = []
    def fake_run(command: list[str], timeout: int = 15) -> str:
        seen.extend(command); return "2026-08-29 host sshd[1]: Failed password\n"
    monkeypatch.setattr(nc, "_run", fake_run)
    assert nc.journald_logs(limit=25)
    assert "25" in seen
    assert "--no-pager" in seen


def test_docker_passes_container_as_argument(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: list[str] = []
    def fake_run(command: list[str], timeout: int = 15) -> str:
        captured.extend(command); return "2026-08-29T12:00:00Z ERROR timeout\n"
    monkeypatch.setattr(nc, "_run", fake_run)
    lines = nc.docker_logs("api-1", limit=20)
    assert captured[-1] == "api-1"
    assert lines[0].startswith("docker/api-1:")


def test_docker_rejects_whitespace_container() -> None:
    with pytest.raises(nc.CollectorError):
        nc.docker_logs("api container")
