from __future__ import annotations

from pathlib import Path

from aegislog import commands_v17


def test_native_dashboard_lines_passes_plain_timestamp_default(monkeypatch):
    calls: dict[str, object] = {}

    def fake_dashboard(path: Path, *, timestamp_year: int | None) -> None:
        calls["path"] = path
        calls["timestamp_year"] = timestamp_year
        assert path.is_file()

    monkeypatch.setattr(commands_v17, "dashboard", fake_dashboard)

    commands_v17._dashboard_lines(["native event\n"], "windows")

    assert calls["timestamp_year"] is None
    assert isinstance(calls["path"], Path)
    assert not calls["path"].exists()
