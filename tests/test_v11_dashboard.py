from __future__ import annotations

import asyncio
from pathlib import Path

from textual.widgets import DataTable

from aegislog.dashboard import AegisDashboard, build_dashboard_analysis
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


def test_dashboard_analysis_contains_full_pipeline(tmp_path: Path) -> None:
    log = tmp_path / "sample.log"
    _write_log(log)
    data = build_dashboard_analysis(log)
    assert data.line_count == 7
    assert data.findings
    assert data.incidents
    assert any(item.severity == "HIGH" for item in data.findings)
    assert any(item.category == "authentication" for item in data.findings)


def test_dashboard_renders_hostile_log_as_literal_text(tmp_path: Path) -> None:
    log = tmp_path / "[bold red]hostile.log"
    log.write_text("ERROR [bold red]not markup[/bold red]\n", encoding="utf-8")

    async def exercise() -> None:
        dashboard = AegisDashboard(log)
        async with dashboard.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            table = dashboard.query_one("#findings-table", DataTable)
            assert table.row_count
            assert "[bold red]" in dashboard.analysis.findings[0].evidence

    asyncio.run(exercise())


def test_dashboard_command_is_registered_and_analyze_is_replaced() -> None:
    commands = {}
    for command in app.registered_commands:
        callback = getattr(command, "callback", None)
        name = command.name or (getattr(callback, "__name__", "").replace("_", "-") if callback else "")
        commands[name] = getattr(callback, "__name__", "") if callback else ""
    assert "dashboard" in commands
    assert commands.get("analyze") == "analyze_dashboard_command"
