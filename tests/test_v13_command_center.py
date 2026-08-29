from pathlib import Path

from aegislog.commands_v12 import _clean_path_input, _command_args, _menu, _path


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
    table = _menu()
    rendered = " ".join(str(cell) for row in table.rows for cell in row.cells)
    assert "Command mode" in rendered
