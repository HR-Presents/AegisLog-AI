from __future__ import annotations

import inspect
from pathlib import Path

from aegislog import commands_v13, commands_v14, commands_v18, commands_v144, commands_v145, entry


def test_start_command_uses_hardened_runtime() -> None:
    assert entry.start is commands_v145.start


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


def test_live_views_use_atomic_full_screen_redraw() -> None:
    for module in (commands_v13, commands_v14, commands_v18):
        options = module._live_options()
        assert options["auto_refresh"] is False
        assert options["screen"] is True
        assert options["transient"] is True
        assert options["vertical_overflow"] == "crop"

    for function in (commands_v13.live_dashboard, commands_v14.live_multi, commands_v18.native_live):
        source = inspect.getsource(function)
        assert "refresh_per_second" not in source
        assert "refresh=True" in source


def test_menu_pause_has_no_empty_default_prompt() -> None:
    source = inspect.getsource(commands_v144._pause_for_menu)
    assert "Prompt.ask" not in source
    assert "default=\"\"" not in source
