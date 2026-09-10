from __future__ import annotations

from pathlib import Path

from rich.console import Console

from aegislog.command_center_ui import render_multisource_command_center, render_realtime_command_center
from aegislog.commands_v145 import _home
from aegislog.dashboard import analyze_dashboard, render_dashboard
from aegislog.multisource import MultiSourceState
from aegislog.realtime import RealtimeState


def _plain(renderable, width: int = 120) -> str:
    console = Console(record=True, width=width, color_system=None)
    console.print(renderable)
    return console.export_text()


def _sample_lines() -> list[str]:
    return [
        "2026-09-10T14:32:01Z INFO sshd: authentication attempt from 10.0.0.5\n",
        "2026-09-10T14:32:04Z ERROR sshd: failed password for admin from 10.0.0.5\n",
        "2026-09-10T14:32:08Z ERROR sshd: failed password for admin from 10.0.0.5\n",
        "2026-09-10T14:32:12Z ERROR sshd: failed password for admin from 10.0.0.5\n",
        "2026-09-10T14:33:01Z WARNING web: suspicious request from 10.0.0.9\n",
        "2026-09-10T14:34:01Z INFO api: service restored successfully\n",
    ]


def test_mission_control_keeps_shield_a_and_existing_commands() -> None:
    output = _plain(_home(120), width=120)
    assert "AEGISLOG" in output
    assert "/A\\" in output or "/\\" in output
    assert "MISSION CONTROL" in output
    assert "INVESTIGATE" in output
    assert "MONITOR" in output
    assert "[01] ANALYZE LOG" in output
    assert "[02] LIVE MONITOR" in output
    assert "[03] MULTI-SOURCE" in output
    assert "[04] NATIVE LOGS" in output
    assert "[05] NATIVE MONITOR" in output
    assert "[06] INCIDENTS" in output
    assert "[07] DEMO" in output
    assert "[08] HEALTH" in output
    assert "[09] HELP" in output
    output.encode("cp1252")


def test_analysis_dashboard_visualizes_only_real_sample_data(tmp_path: Path) -> None:
    path = tmp_path / "sample.log"
    path.write_text("".join(_sample_lines()), encoding="utf-8")
    data = analyze_dashboard(path)
    output = _plain(render_dashboard(data, screen_width=120), width=120)

    assert "INVESTIGATION CONTEXT" in output
    assert "SECURITY METRICS" in output
    assert "EVENTS" in output and "6" in output
    assert "SECURITY DISTRIBUTION" in output
    assert "EVENT ACTIVITY" in output
    assert "ANALYST FOCUS" in output
    assert "INVESTIGATION TIMELINE" in output
    assert "DETECTED FINDINGS" in output
    assert "RAW EVIDENCE" in output
    assert "2026-09-10T14:32" in output
    assert "failed password for admin" in output
    output.encode("cp1252")


def test_analysis_dashboard_omits_activity_chart_without_timestamps(tmp_path: Path) -> None:
    path = tmp_path / "untimed.log"
    path.write_text("error service failed\ninfo service started\n", encoding="utf-8")
    data = analyze_dashboard(path)
    output = _plain(render_dashboard(data, screen_width=80), width=80)
    assert "SECURITY METRICS" in output
    assert "EVENT ACTIVITY" not in output
    assert "INVESTIGATION TIMELINE" not in output


def test_live_command_center_uses_realtime_state_values(monkeypatch) -> None:
    monkeypatch.setattr("aegislog.command_center_ui.shutil.get_terminal_size", lambda fallback: type("S", (), {"columns": 120})())
    state = RealtimeState(source="live.log", window_size=50, watch_profile="all")
    lines = _sample_lines()
    state.ingest(lines, now=10.0)
    output = _plain(render_realtime_command_center(state), width=120)

    assert "LIVE MONITOR" in output
    assert "LIVE SECURITY METRICS" in output
    assert "SERVICE ACTIVITY" in output
    assert "RECENT SECURITY FINDINGS" in output
    assert "6" in output
    assert "live.log" in output
    output.encode("cp1252")


def test_multisource_command_center_shows_real_source_activity(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("aegislog.command_center_ui.shutil.get_terminal_size", lambda fallback: type("S", (), {"columns": 120})())
    first = tmp_path / "auth.log"
    second = tmp_path / "web.log"
    first.write_text("", encoding="utf-8")
    second.write_text("", encoding="utf-8")
    state = MultiSourceState(sources=(first, second), window_size=50, trend_seconds=60, watch_profile="all")
    state.ingest(first, _sample_lines()[:4], now=10.0)
    state.ingest(second, _sample_lines()[4:], now=11.0)
    output = _plain(render_multisource_command_center(state), width=120)

    assert "MULTI-SOURCE" in output
    assert "SOURCE ACTIVITY" in output
    assert "auth.log" in output
    assert "web.log" in output
    assert "4" in output
    assert "2" in output
    assert "LIVE SECURITY ALERT FEED" in output
    output.encode("cp1252")
