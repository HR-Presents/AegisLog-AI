from __future__ import annotations

import json
import stat

from aegislog import config
from aegislog.collectors import CollectorError, _run
from aegislog.incidents import correlate
from aegislog.engine import Finding


def test_incident_ids_are_stable_sha256_prefixes() -> None:
    finding = Finding("HIGH", "auth", "Failure", "evidence", "review")
    incident = correlate([finding])[0]
    assert len(incident.id) == 12
    assert all(character in "0123456789abcdef" for character in incident.id)


def test_collector_rejects_non_allowlisted_executables() -> None:
    try:
        _run(["echo", "unsafe"])
    except CollectorError as exc:
        assert "unsupported" in str(exc)
    else:
        raise AssertionError("collector command should have been rejected")


def test_config_is_versioned_filtered_and_private(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(config, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(config, "CONFIG_FILE", tmp_path / "config.json")
    path = config.save_config({"ai_provider": "none", "unknown": "discard-me"})
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == config.CONFIG_SCHEMA_VERSION
    assert "unknown" not in payload
    if hasattr(stat, "S_IMODE"):
        assert stat.S_IMODE(path.stat().st_mode) & 0o077 == 0


def test_future_config_schema_fails_closed(tmp_path, monkeypatch) -> None:
    path = tmp_path / "config.json"
    path.write_text('{"schema_version": 999, "ai_provider": "openai"}', encoding="utf-8")
    monkeypatch.setattr(config, "CONFIG_FILE", path)
    assert config.load_config()["ai_provider"] == "none"
