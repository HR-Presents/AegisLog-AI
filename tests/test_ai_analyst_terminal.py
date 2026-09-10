from rich.console import Console
from typer.testing import CliRunner

from aegislog.commands_v145 import _home
from aegislog.entry import app


def _render(value, width: int = 100) -> str:
    console = Console(record=True, force_terminal=False, color_system=None, width=width)
    console.print(value)
    return console.export_text(clear=False)


def test_ai_analyst_is_absent_from_home() -> None:
    output = _render(_home(100))

    assert "AI ANALYST" not in output
    assert "OLLAMA" not in output
    assert "REMOTE AI" not in output
    assert "LOCAL-FIRST" in output
    assert "READ-ONLY" in output
    assert "DETERMINISTIC" in output


def test_public_cli_does_not_expose_ai_commands() -> None:
    result = CliRunner().invoke(app, ["--help"])

    assert result.exit_code == 0
    output = result.stdout.lower()
    assert "ai-analyst" not in output
    assert "ollama" not in output
    assert "openai" not in output
    assert " ask " not in output


def test_home_keeps_deterministic_investigation_paths() -> None:
    output = _render(_home(100))

    for label in ("ANALYZE", "INCIDENTS", "NATIVE LOGS", "LIVE MONITOR", "MULTI-SOURCE", "HEALTH", "HELP"):
        assert label in output
