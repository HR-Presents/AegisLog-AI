from rich.console import Console

from aegislog.console_pages import _command_summary, _health_summary


def _render(value, width: int = 100) -> str:
    console = Console(record=True, force_terminal=False, width=width)
    console.print(value)
    return console.export_text()


def test_health_summary_surfaces_readiness_and_native_availability() -> None:
    output = _render(_health_summary(2, 3))

    assert "CORE CAPABILITIES" in output
    assert "READY" in output
    assert "NATIVE SOURCES" in output
    assert "2/3" in output
    assert "HOST CHECK" in output
    assert "READ-ONLY" in output


def test_command_summary_highlights_primary_entry_points() -> None:
    output = _render(_command_summary("AegisLog.exe"), width=120)

    assert "START" in output
    assert "AegisLog.exe" in output
    assert "ANALYZE" in output
    assert "AegisLog.exe dashboard <file>" in output
    assert "HELP" in output
    assert "AegisLog.exe --help" in output
