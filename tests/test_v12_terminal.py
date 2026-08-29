from __future__ import annotations

from pathlib import Path

from aegislog.commands_v12 import _choose_log_file, _resolve_demo
from aegislog.entry import app


def test_start_command_is_registered() -> None:
    names = {command.name or getattr(command.callback, "__name__", "") for command in app.registered_commands}
    assert "start" in names


def test_choose_log_file_rejects_directory(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("aegislog.commands_v12.Prompt.ask", lambda *args, **kwargs: str(tmp_path))
    assert _choose_log_file() is None


def test_choose_log_file_accepts_file(monkeypatch, tmp_path: Path) -> None:
    log = tmp_path / "auth.log"
    log.write_text("failed login\n", encoding="utf-8")
    monkeypatch.setattr("aegislog.commands_v12.Prompt.ask", lambda *args, **kwargs: f'"{log}"')
    assert _choose_log_file() == log


def test_resolve_demo_from_bundle_root(monkeypatch, tmp_path: Path) -> None:
    sample_dir = tmp_path / "sample_logs"
    sample_dir.mkdir()
    sample = sample_dir / "auth.log"
    sample.write_text("demo\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    assert _resolve_demo() == sample
