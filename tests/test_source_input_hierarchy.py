from rich.console import Console

from aegislog.commands_v145 import _input_panel


def _render(panel, width: int = 90) -> str:
    console = Console(record=True, force_terminal=False, width=width)
    console.print(panel)
    return console.export_text()


def _cell_style(panel, column: int, row: int) -> str:
    return str(panel.renderable.columns[column]._cells[row].style)


def test_source_input_panel_emphasizes_only_primary_action() -> None:
    panel = _input_panel(
        "SOURCE INPUT",
        [
            ("INPUT", "Drag a log file here or paste its full path"),
            ("DEMO", "Type demo to use the built-in dataset"),
            ("BACK", "Type back to return to Mission Control"),
            ("OUTPUT", "HTML report generated after analysis"),
        ],
        primary_label="INPUT",
        screen_width=90,
    )
    output = _render(panel)

    assert "▶ INPUT" in output
    assert "▶ DEMO" not in output
    assert "▶ BACK" not in output
    assert "▶ OUTPUT" not in output
    assert "Drag a log file here or paste its full path" in output
    assert _cell_style(panel, 0, 0) == "bold cyan"
    assert _cell_style(panel, 0, 1) == "dim"
    assert _cell_style(panel, 1, 1) == "dim"


def test_generic_input_panel_restores_readable_hierarchy() -> None:
    panel = _input_panel(
        "WATCH PROFILE",
        [("SECURITY", "Balanced defensive detection")],
        screen_width=90,
    )
    output = _render(panel)

    assert "SECURITY" in output
    assert "▶ SECURITY" not in output
    assert _cell_style(panel, 0, 0) == "bold cyan"
    assert _cell_style(panel, 1, 0) == "white"
