from __future__ import annotations

from rich.console import Console

from aegislog import commands_v145


def _render(width: int) -> str:
    console = Console(width=width, color_system=None, force_terminal=False, record=True)
    console.print(commands_v145._home(width))
    return console.export_text()


def test_final_wordmark_replaces_falcon_and_version() -> None:
    output = _render(160)
    assert "DEFENSIVE LOG INVESTIGATION" in output
    assert "MADE BY HR-PRESENTS" in output
    assert "SYSTEM READY" in output
    assert "INVESTIGATE" in output
    assert "MONITOR & INVESTIGATE" in output
    assert "UTILITIES" in output
    assert "ANALYZE LOG" in output
    assert "LIVE MONITOR" in output
    assert "VERSION" not in output
    assert "<F>" not in output
    assert "__/\\__" not in output


def test_final_home_is_centered_and_compact_on_wide_windows_terminal() -> None:
    width = 180
    output = _render(width)
    lines = [line for line in output.splitlines() if line.strip()]
    assert lines
    first_border = next(line for line in lines if "+" in line)
    left_margin = len(first_border) - len(first_border.lstrip())
    assert left_margin >= 28
    assert len(first_border.strip()) <= 118
    assert max(len(line.rstrip()) for line in lines) <= width


def test_final_header_stays_compact() -> None:
    output = _render(120)
    lines = output.splitlines()
    investigate_index = next(i for i, line in enumerate(lines) if "INVESTIGATE" in line)
    assert investigate_index <= 15


def test_final_home_remains_ascii_safe_across_common_windows_widths() -> None:
    for width in (40, 64, 80, 100, 120, 160, 180):
        output = _render(width)
        output.encode("ascii")
        assert "DEFENSIVE LOG" in output
        assert "01" in output
        assert "Q EXIT" in output.upper()
        assert max(len(line) for line in output.splitlines()) <= width
        if width >= 120:
            borders = [line.strip() for line in output.splitlines() if "+" in line]
            assert borders
            assert max(len(line) for line in borders) <= 118
