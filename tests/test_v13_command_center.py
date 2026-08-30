from pathlib import Path

from rich.console import Console

import aegislog.commands_v12 as command_center
from aegislog.commands_v12 import (
    _clean_path_input,
    _command_args,
    _launch_live_dashboard,
    _launch_live_multi,
    _menu,
    _path,
)


def test_clean_path_input_accepts_dragged_quoted_paths():
    assert _clean_path_input('"C:\\Security Logs\\auth.log"') == "C:\\Security Logs\\auth.log"
    assert _clean_path_input("'C:\\Security Logs\\auth.log'") == "C:\\Security Logs\\auth.log"


def test_command_args_preserve_windows_paths_and_strip_executable_prefix():
    args = _command_args('AegisLog.exe dashboard "C:\\Security Logs\\auth.log"')
    assert args == ["dashboard", "C:\\Security Logs\\auth.log"]


def test_command_args_allow_menu_native_command_without_prefix():
    args = _command_args("native-analyze windows --channel Security")
    assert args == ["native-analyze", "windows", "--channel", "Security"]


def test_path_accepts_real_file(tmp_path: Path):
    log = tmp_path / "auth log.txt"
    log.write_text("hello\n", encoding="utf-8")
    assert _path(f'"{log}"') == log


def test_menu_exposes_command_mode():
    console = Console(record=True, width=120)
    console.print(_menu())
    assert "Command mode" in console.export_text()


def test_menu_live_dashboard_passes_concrete_runtime_defaults(monkeypatch, tmp_path: Path):
    log = tmp_path / "auth.log"
    log.write_text("hello\n", encoding="utf-8")
    called = {}

    def fake_live(path, *, from_start, refresh, window, profile):
        called.update(
            path=path,
            from_start=from_start,
            refresh=refresh,
            window=window,
            profile=profile,
        )

    monkeypatch.setattr(command_center, "live_dashboard", fake_live)
    _launch_live_dashboard(log, "security")

    assert called == {
        "path": log,
        "from_start": False,
        "refresh": 1.0,
        "window": 500,
        "profile": "security",
    }


def test_menu_live_multi_passes_concrete_runtime_defaults(monkeypatch, tmp_path: Path):
    first = tmp_path / "one.log"
    second = tmp_path / "two.log"
    first.write_text("one\n", encoding="utf-8")
    second.write_text("two\n", encoding="utf-8")
    called = {}

    def fake_multi(paths, *, from_start, refresh, window, trend_seconds, profile):
        called.update(
            paths=paths,
            from_start=from_start,
            refresh=refresh,
            window=window,
            trend_seconds=trend_seconds,
            profile=profile,
        )

    monkeypatch.setattr(command_center, "live_multi", fake_multi)
    _launch_live_multi([first, second], "authentication")

    assert called == {
        "paths": [first, second],
        "from_start": False,
        "refresh": 1.0,
        "window": 1000,
        "trend_seconds": 60,
        "profile": "authentication",
    }


def test_menu_live_dashboard_failure_is_contained(monkeypatch, tmp_path: Path):
    log = tmp_path / "auth.log"
    log.write_text("hello\n", encoding="utf-8")
    recorded = Console(record=True, width=120)

    def broken_live(*args, **kwargs):
        raise TypeError("simulated menu launch failure")

    monkeypatch.setattr(command_center, "live_dashboard", broken_live)
    monkeypatch.setattr(command_center, "console", recorded)

    _launch_live_dashboard(log, "security")

    output = recorded.export_text()
    assert "Real-time file dashboard could not start" in output
    assert "simulated menu launch failure" in output
    assert "stayed open safely" in output
