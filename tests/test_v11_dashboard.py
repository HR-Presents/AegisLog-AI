from pathlib import Path

from rich.console import Console

from aegislog.dashboard import analyze_dashboard, render_dashboard
from aegislog.entry import app


def _write_log(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "sshd: Failed password for admin from 203.0.113.8 port 22 ssh2",
                "sshd: Failed password for admin from 203.0.113.8 port 22 ssh2",
                "sshd: Failed password for admin from 203.0.113.8 port 22 ssh2",
                "sshd: Failed password for admin from 203.0.113.8 port 22 ssh2",
                "sshd: Failed password for admin from 203.0.113.8 port 22 ssh2",
                "app: ERROR database timeout",
                "nginx: GET /index.html 200",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def test_dashboard_snapshot_contains_full_analysis(tmp_path: Path):
    log = tmp_path / "sample.log"
    _write_log(log)
    data = analyze_dashboard(log)
    assert data.lines == 7
    assert data.findings
    assert data.incidents
    assert data.severities.get("HIGH", 0) >= 1
    assert data.categories.get("authentication", 0) >= 1


def test_dashboard_render_is_terminal_safe(tmp_path: Path):
    log = tmp_path / "hostile.log"
    log.write_text("ERROR [bold red]not markup[/bold red]\n", encoding="utf-8")
    data = analyze_dashboard(log)
    console = Console(record=True, force_terminal=False, width=120)
    console.print(render_dashboard(data))
    output = console.export_text()
    assert "AEGISLOG AI" in output
    assert "not markup" in output
    assert "Detected findings" in output


def test_dashboard_command_is_registered_and_analyze_is_replaced():
    commands = {}
    for command in app.registered_commands:
        callback = getattr(command, "callback", None)
        name = command.name or (getattr(callback, "__name__", "").replace("_", "-") if callback else "")
        commands[name] = getattr(callback, "__name__", "") if callback else ""
    assert "dashboard" in commands
    assert commands.get("analyze") == "analyze_dashboard_command"
