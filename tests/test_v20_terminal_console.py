from __future__ import annotations

from io import StringIO

from rich.console import Console

from aegislog.commands_v145 import _footer, _home


def _render(renderable, width: int) -> str:
    stream = StringIO()
    console = Console(file=stream, force_terminal=False, width=width, color_system=None)
    console.print(renderable)
    return stream.getvalue()


def test_wide_home_is_bounded_and_uses_final_operator_layout() -> None:
    output = _render(_home(180), 180)
    lines = output.splitlines()
    assert "AEGISLOG" in output
    assert "MAIN MENU" in output
    assert "QUICK INFO" in output
    assert "SYSTEM READY" in output
    assert "INVESTIGATE LOGS" in output
    assert "LIVE MONITOR" in output
    assert "MADE BY HR-PRESENTS" in output
    assert "VERSION" not in output
    assert max(len(line.lstrip()) for line in lines) <= 116
    assert max(len(line.lstrip()) for line in lines) >= 100
    assert any(line.startswith(" " * 20) for line in lines if line.strip())


def test_wide_home_descriptions_do_not_wrap_like_table_cells() -> None:
    output = _render(_home(180), 180)
    assert "Analyze evidence and generate a report" in output
    assert "Review correlated evidence chains" in output
    assert "Correlate activity across live sources" in output
    assert "Watch native telemetry read-only" in output


def test_narrow_home_collapses_without_losing_actions() -> None:
    output = _render(_home(52), 52)
    assert "AEGISLOG" in output
    assert "MAIN MENU" in output
    assert "INVESTIGATE LOGS" in output
    assert "MULTI-SOURCE" in output
    assert "HELP" in output
    assert all(len(line) <= 52 for line in output.splitlines())


def test_home_has_one_real_prompt_and_clear_navigation_hint() -> None:
    output = _render(_home(180), 180)
    assert "SELECT  >" not in output
    assert output.count("aegis@console") == 1
    footer = _render(_footer(180), 180)
    assert "Select [01-09]" in footer
    assert "Q Exit" in footer


def test_home_chrome_is_ascii_safe() -> None:
    output = _render(_home(180), 180)
    output.encode("cp1252")
