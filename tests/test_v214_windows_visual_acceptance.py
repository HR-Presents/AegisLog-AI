from __future__ import annotations

from rich.console import Console

from aegislog import commands_v145


def _render(width: int) -> str:
    console = Console(width=width, color_system=None, force_terminal=False, record=True)
    console.print(commands_v145._home(width))
    return console.export_text()


def test_v214_falcon_is_compact_and_mantra_is_removed() -> None:
    output = _render(160)
    assert "A E G I S L O G" in output
    assert "SYSTEM READY" in output
    assert "INVESTIGATE" in output
    assert "MONITOR" in output
    assert "INVEST\nDETECT\nUNDERSTAND\nSTAY AHEAD" not in output
    assert "\\__" in output
    assert "/\\" in output
    assert "\\__/" in output


def test_v214_home_is_centered_and_bounded_on_wide_windows_terminal() -> None:
    width = 180
    output = _render(width)
    lines = [line for line in output.splitlines() if line.strip()]
    assert lines
    visible = [line for line in lines if "+" in line or "MISSION CONTROL" in line]
    assert visible
    assert max(len(line.rstrip()) for line in lines) <= width
    first_border = next(line for line in lines if "+" in line)
    left_margin = len(first_border) - len(first_border.lstrip())
    assert left_margin >= 20
    assert len(first_border.strip()) <= 98


def test_v214_compact_header_does_not_consume_excess_vertical_space() -> None:
    output = _render(120)
    lines = output.splitlines()
    mission_index = next(i for i, line in enumerate(lines) if "MISSION CONTROL" in line)
    assert mission_index <= 13


def test_v214_remains_ascii_safe_across_common_windows_widths() -> None:
    for width in (40, 64, 80, 100, 120, 160, 180):
        output = _render(width)
        output.encode("ascii")
        assert "AEGISLOG" in output or "A E G I S L O G" in output
        assert "01" in output
        assert "Q EXIT" in output.upper()
        assert max(len(line) for line in output.splitlines()) <= width
