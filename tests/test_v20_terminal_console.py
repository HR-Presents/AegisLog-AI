from __future__ import annotations

from io import StringIO

from rich.console import Console

from aegislog.commands_v145 import _footer, _home


def _render(renderable, width: int) -> str:
    stream = StringIO()
    console = Console(file=stream, force_terminal=False, width=width, color_system=None)
    console.print(renderable)
    return stream.getvalue()


def test_wide_home_uses_full_width_and_two_work_areas() -> None:
    output = _render(_home(160), 160)
    lines = output.splitlines()
    assert "MISSION CONTROL" in output
    assert "INV" in output
    assert "MON" in output
    assert "ANALYZE" in output
    assert "LIVE MONITOR" in output
    assert "SYSTEM READY" in output
    assert max(map(len, lines)) >= 150


def test_narrow_home_collapses_without_losing_actions() -> None:
    output = _render(_home(52), 52)
    assert "MISSION CONTROL" in output
    assert "ANALYZE" in output
    assert "MULTI-SOURCE" in output
    assert "HELP" in output
    assert all(len(line) <= 52 for line in output.splitlines())


def test_home_has_one_navigation_hint_not_a_fake_second_prompt() -> None:
    output = _render(_home(160), 160)
    assert "SELECT  >" not in output
    assert "aegis@console" not in output
    footer = _render(_footer(160), 160)
    assert "01-09 select" in footer
    assert "C command mode" in footer
    assert "Q quit" in footer


def test_home_chrome_is_ascii_safe() -> None:
    output = _render(_home(160), 160)
    output.encode("cp1252")
