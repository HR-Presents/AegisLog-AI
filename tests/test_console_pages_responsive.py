from rich.console import Console
from rich.text import Text

from aegislog.console_pages import _command_table, _health_table


def _render(value, width: int) -> str:
    console = Console(record=True, force_terminal=False, width=width)
    console.print(value)
    return console.export_text()


def test_health_table_collapses_state_and_details_on_narrow_terminal() -> None:
    rows = [
        ("Runtime", Text("READY"), "Python 3.12.0"),
        ("Windows Event Logs", Text("NOT ON THIS OS"), "Windows only"),
    ]
    output = _render(_health_table(rows, 50), 50)

    assert "Status / Details" in output
    assert "State" not in output
    assert "READY" in output
    assert "Python 3.12.0" in output
    assert "NOT ON THIS OS" in output
    assert "Windows only" in output


def test_health_table_keeps_three_column_layout_when_space_allows() -> None:
    rows = [("Runtime", Text("READY"), "Python 3.12.0")]
    output = _render(_health_table(rows, 100), 100)

    assert "State" in output
    assert "Details" in output
    assert "Status / Details" not in output


def test_command_table_stacks_command_and_purpose_on_narrow_terminal() -> None:
    rows = (("aegislog dashboard <file>", "Analyze one log"),)
    output = _render(_command_table(rows, 50), 50)

    assert "Command / Purpose" in output
    assert "aegislog dashboard <file>" in output
    assert "Analyze one log" in output


def test_command_table_keeps_two_columns_when_space_allows() -> None:
    rows = (("aegislog dashboard <file>", "Analyze one log"),)
    output = _render(_command_table(rows, 100), 100)

    assert "Command" in output
    assert "Purpose" in output
    assert "Command / Purpose" not in output
