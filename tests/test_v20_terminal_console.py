from __future__ import annotations

from io import StringIO

from rich.console import Console

from aegislog.commands_v145 import _footer, _home


def _render(renderable, width: int) -> str:
    stream = StringIO()
    console = Console(file=stream, force_terminal=False, width=width, color_system=None)
    console.print(renderable)
    return stream.getvalue()


def test_wide_home_is_bounded_and_uses_two_operator_work_areas() -> None:
    output = _render(_home(180), 180)
    lines = output.splitlines()
    assert "MISSION CONTROL" in output
    assert "INVESTIGATE" in output
    assert "MONITOR" in output
    assert "ANALYZE LOG" in output
    assert "LIVE MONITOR" in output
    assert "SYSTEM READY" in output
    assert "INV  " not in output
    assert "ACTION" not in output
    assert "PURPOSE" not in output
    assert max(map(len, lines)) <= 112
    assert max(map(len, lines)) >= 100


def test_wide_home_descriptions_do_not_wrap_like_table_cells() -> None:
    output = _render(_home(180), 180)
    assert "Analyze evidence and generate a report" in output
    assert "Review correlated evidence chains" in output
    assert "Correlate activity across live sources" in output
    assert "Watch native telemetry read-only" in output


def test_narrow_home_collapses_without_losing_actions() -> None:
    output = _render(_home(52), 52)
    assert "MISSION CONTROL" in output
    assert "ANALYZE LOG" in output
    assert "MULTI-SOURCE" in output
    assert "HELP" in output
    assert all(len(line) <= 52 for line in output.splitlines())


def test_home_has_one_navigation_hint_not_a_fake_second_prompt() -> None:
    output = _render(_home(180), 180)
    assert "SELECT  >" not in output
    assert "aegis@console" not in output
    footer = _render(_footer(180), 180)
    assert "01-09 Select" in footer
    assert "C Command Mode" in footer
    assert "Q Exit" in footer


def test_home_chrome_is_ascii_safe() -> None:
    output = _render(_home(180), 180)
    output.encode("cp1252")
