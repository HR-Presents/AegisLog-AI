from pathlib import Path

from rich.console import Console

from aegislog.dashboard import DashboardData, analyze_dashboard, render_dashboard
from aegislog.engine import Finding
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


def _render(data: DashboardData, width: int = 120) -> str:
    console = Console(record=True, force_terminal=False, width=width)
    console.print(render_dashboard(data))
    return console.export_text()


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
    output = _render(analyze_dashboard(log))
    assert "AEGISLOG  /  INVESTIGATION" in output
    assert "SOURCE" in output
    assert "POSTURE" in output
    assert "ANALYST FOCUS" in output
    assert "INVESTIGATION SUMMARY" in output
    assert "FOLLOW-UP / COPY-READY" in output
    assert "not markup" in output
    assert "Detected findings" in output
    assert "Signals are investigative evidence, not proof of compromise." in output


def test_dashboard_orders_findings_by_severity_and_surfaces_primary_action() -> None:
    data = DashboardData(
        source="/tmp/order.log",
        lines=2,
        findings=(
            Finding("MEDIUM", "network", "Medium finding", "medium evidence", "Medium action"),
            Finding("HIGH", "authentication", "High finding", "high evidence", "High action"),
        ),
        anomalies=(),
        incidents=(),
        levels={"ERROR": 2},
        services={"test": 2},
        categories={"network": 1, "authentication": 1},
        severities={"HIGH": 1, "MEDIUM": 1},
    )
    output = _render(data)

    assert output.index("High finding") < output.index("Medium finding")
    focus = output[output.index("ANALYST FOCUS") : output.index("Detected findings")]
    assert "PRIMARY" in focus
    assert "High finding" in focus
    assert "High action" in focus


def test_follow_up_uses_actual_source_instead_of_placeholder() -> None:
    data = DashboardData(
        source="/tmp/prod auth.log",
        lines=0,
        findings=(),
        anomalies=(),
        incidents=(),
        levels={},
        services={},
        categories={},
        severities={},
    )
    output = _render(data)

    assert "<file>" not in output
    assert "prod auth.log" in output
    assert "aegislog incidents" in output


def test_dashboard_command_is_registered_and_analyze_is_replaced():
    commands = {}
    for command in app.registered_commands:
        callback = getattr(command, "callback", None)
        name = command.name or (getattr(callback, "__name__", "").replace("_", "-") if callback else "")
        commands[name] = getattr(callback, "__name__", "") if callback else ""
    assert "dashboard" in commands
    assert commands.get("analyze") == "analyze_dashboard_command"