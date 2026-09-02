from __future__ import annotations

import inspect
from pathlib import Path

from aegislog import commands_v13, commands_v18, commands_v144, entry


def test_start_command_uses_hardened_runtime() -> None:
    assert entry.start.__module__ == "aegislog.commands_v144"


def test_interactive_live_file_loads_current_content(monkeypatch, tmp_path: Path) -> None:
    log = tmp_path / "auth.log"
    log.write_text("INFO ready\n", encoding="utf-8")
    called: dict[str, object] = {}

    def fake_live_dashboard(path: Path, **kwargs: object) -> None:
        called["path"] = path
        called.update(kwargs)

    monkeypatch.setattr(commands_v144, "live_dashboard", fake_live_dashboard)
    commands_v144._launch_live_file(log, "security")

    assert called["path"] == log
    assert called["from_start"] is True
    assert called["refresh"] == 1.0
    assert called["profile"] == "security"


def test_live_views_do_not_use_alternate_screen() -> None:
    file_live_source = inspect.getsource(commands_v13.live_dashboard)
    native_live_source = inspect.getsource(commands_v18.native_live)
    assert "screen=False" in file_live_source
    assert "screen=False" in native_live_source
    assert "refresh=True" in file_live_source
    assert "refresh=True" in native_live_source


def test_menu_pause_has_no_empty_default_prompt() -> None:
    source = inspect.getsource(commands_v144._pause_for_menu)
    assert "Prompt.ask" not in source
    assert "default=\"\"" not in source
