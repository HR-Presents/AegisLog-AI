from rich.console import Console

from aegislog.commands_v145 import _input_panel


def _render(value, width: int = 90) -> str:
    console = Console(record=True, force_terminal=False, color_system=None, width=width)
    console.print(value)
    return console.export_text(clear=False)


def test_source_input_emphasizes_primary_action_without_panel_chrome() -> None:
    value = _input_panel(
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
    output = _render(value)

    assert "SOURCE INPUT" in output
    assert "INPUT" in output
    assert "Drag a log file here or paste its full path" in output
    assert "DEMO" in output
    assert "BACK" in output
    assert "OUTPUT" in output
    assert "╭" not in output
    assert "╰" not in output
    assert "▶" not in output


def test_generic_input_surface_remains_readable() -> None:
    output = _render(
        _input_panel(
            "WATCH PROFILE",
            [("SECURITY", "Balanced defensive detection")],
            screen_width=90,
        )
    )

    assert "WATCH PROFILE" in output
    assert "SECURITY" in output
    assert "Balanced defensive detection" in output
    assert "╭" not in output
