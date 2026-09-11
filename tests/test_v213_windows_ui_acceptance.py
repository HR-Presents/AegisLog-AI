from __future__ import annotations

from rich.console import Console

from aegislog import commands_v145
from aegislog.dashboard import DashboardData
from aegislog.dashboard_v213 import render_dashboard


def _plain(renderable, width: int = 118) -> str:
    console = Console(width=width, color_system=None, force_terminal=False, record=True)
    console.print(renderable)
    return console.export_text()


def test_mission_control_uses_final_wordmark_identity() -> None:
    output = _plain(commands_v145._home(118), width=120)
    assert "DEFENSIVE LOG INVESTIGATION" in output
    assert "MADE BY HR-PRESENTS" in output
    assert "SYSTEM READY" in output
    assert "INVESTIGATE" in output
    assert "MONITOR & INVESTIGATE" in output
    assert "UTILITIES" in output
    assert "ANALYZE LOG" in output
    assert "LIVE MONITOR" in output
    assert "VERSION" not in output
    assert "__/\\__" not in output
    assert "<F>" not in output


def test_analyze_uses_dense_visual_soc_hierarchy() -> None:
    data = DashboardData(
        source=r"C:\\Logs\\sample.log",
        lines=26,
        findings=(),
        anomalies=(),
        incidents=(),
        levels={"INFO": 20, "ERROR": 6},
        services={"app": 18, "sshd": 8},
        categories={},
        severities={},
        raw_lines=tuple(f"2026-09-11T10:{index:02d}:00 app INFO event" for index in range(26)),
    )
    output = _plain(render_dashboard(data, screen_width=118), width=120)
    for label in (
        "SECURITY INVESTIGATION",
        "INVESTIGATION TICKER",
        "EVENT TREND",
        "SEVERITY MIX",
        "SERVICE LOAD",
        "FINDING CATEGORIES",
        "ANALYST FOCUS",
        "LIVE EVIDENCE BOARD",
        "SOURCE PROFILE",
    ):
        assert label in output
    assert "26" in output
    assert "app" in output.lower()


def test_analyze_is_bounded_for_wide_windows_terminal() -> None:
    data = DashboardData(source=r"C:\\Users\\Example\\Downloads\\very-long-but-realistic-log-file-name.log", lines=1, findings=(), anomalies=(), incidents=(), levels={}, services={}, categories={}, severities={})
    output = _plain(render_dashboard(data, screen_width=220), width=220)
    meaningful = [line.rstrip() for line in output.splitlines() if line.strip()]
    assert meaningful
    assert max(len(line) for line in meaningful) <= 118
