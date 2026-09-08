from __future__ import annotations

from pathlib import Path

import pytest
from rich.console import Console

from aegislog.commands_v144 import _frame_width, _header, _home
from aegislog.multisource import MultiSourceState, render_multisource
from aegislog.realtime import RealtimeState, render_realtime
from aegislog.ui import bounded


def _render_text(renderable, width: int) -> str:
    console = Console(width=width, record=True, color_system=None, force_terminal=False)
    console.print(renderable)
    return console.export_text(clear=False)


def _multisource_state() -> MultiSourceState:
    first = Path("aegislog_v145_test.log")
    second = Path("aegislog_second_test.log")
    state = MultiSourceState((first, second), watch_profile="security")
    state.ingest(
        first,
        [
            "2026-09-02T09:37:00Z ERROR auth: failed login user=admin source=198.51.100.42\n",
            "2026-09-02T09:37:01Z WARNING sshd: invalid user root from 198.51.100.42\n",
        ],
        now=1.0,
    )
    state.ingest(
        second,
        [
            "2026-09-02T09:37:31Z ERROR firewall: blocked inbound connection port=3389\n",
            "2026-09-02T09:37:50Z ERROR firewall: blocked probe port=445\n",
        ],
        now=2.0,
    )
    return state


def _realtime_state() -> RealtimeState:
    state = RealtimeState("aegislog_v145_test.log", watch_profile="security")
    state.ingest(
        [
            "2026-09-02T09:37:00Z ERROR auth: failed login user=admin source=198.51.100.42\n",
            "2026-09-02T09:37:01Z WARNING sshd: invalid user root from 198.51.100.42\n",
            "2026-09-02T09:37:31Z ERROR firewall: blocked inbound connection port=3389\n",
            "2026-09-02T09:37:50Z ERROR firewall: blocked probe port=445\n",
        ],
        now=1.0,
    )
    return state


def test_multisource_dashboard_keeps_all_sections_at_standard_width() -> None:
    width = 100
    text = _render_text(render_multisource(_multisource_state()), width)

    for label in (
        "MULTI-SOURCE REAL-TIME SOC",
        "SOC summary",
        "Profile telemetry",
        "baseline intelligence",
        "Live security alert feed",
        "Monitoring status",
    ):
        assert label.lower() in text.lower()
    assert max(len(line) for line in text.splitlines()) <= width


def test_realtime_dashboard_keeps_all_sections_at_standard_width() -> None:
    width = 100
    text = _render_text(render_realtime(_realtime_state()), width)

    for label in (
        "REAL-TIME DEFENSIVE MONITOR",
        "Live summary",
        "Profile telemetry",
        "baseline intelligence",
        "Recent findings - Security",
        "Live status",
    ):
        assert label.lower() in text.lower()
    assert max(len(line) for line in text.splitlines()) <= width


def test_live_views_can_use_ultrawide_terminal_space() -> None:
    for renderable in (
        bounded(render_realtime(_realtime_state())),
        bounded(render_multisource(_multisource_state())),
    ):
        text = _render_text(renderable, 220)
        assert max(len(line) for line in text.splitlines()) <= 220
        assert max(len(line) for line in text.splitlines()) > 112


def test_realtime_dashboard_static_labels_are_legacy_console_safe() -> None:
    state = RealtimeState("aegislog_v145_test.log", watch_profile="security")
    text = _render_text(render_realtime(state), 100)
    for label in (
        "REAL-TIME DEFENSIVE MONITOR",
        "Live summary",
        "Profile telemetry",
        "Recent findings - Security",
        "Live status",
    ):
        label.encode("cp1252")
        assert label in text
    assert "•" not in text
    assert "—" not in text


def test_interactive_header_uses_legacy_console_safe_status_text() -> None:
    plain = _header().renderable.plain
    plain.encode("cp1252")
    assert "[ READY ]" in plain
    assert "LOCAL-FIRST" in plain
    assert "READ-ONLY MONITORING" in plain
    assert "REMOTE AI: OPT-IN" in plain
    assert "●" not in plain
    assert "○" not in plain


@pytest.mark.parametrize("width", [40, 50, 59, 60, 64, 80, 100, 120, 160, 220])
def test_interactive_home_fits_terminal_width(width: int) -> None:
    text = _render_text(_home(width), width)
    assert "AEGISLOG" in text
    assert "MISSION CONTROL" in text
    assert "ANALYZE LOG" in text
    assert "MULTI-SOURCE SOC" in text
    assert "INCIDENT INTEL" in text
    assert "COMMAND MODE" in text
    assert "opt-in" in text.lower()
    assert max(len(line) for line in text.splitlines()) <= width


def test_interactive_home_uses_full_terminal_width() -> None:
    assert _frame_width(100) == 98
    assert _frame_width(160) == 158
    assert _frame_width(220) == 218
    assert _frame_width(60) == 58
    assert _frame_width(40) == 38


def test_interactive_home_expands_on_wide_terminals() -> None:
    text = _render_text(_home(220), 220)
    lines = [line for line in text.splitlines() if line]
    assert lines[0].startswith("╭") or lines[0].startswith("┌")
    assert max(len(line) for line in lines) <= 220
    assert max(len(line) for line in lines) >= 218
    assert "LOCAL-FIRST" in text
    assert "CAPABILITY" in text
    header_lines = [line for line in lines if "KEY" in line and "ACTION" in line]
    assert header_lines
    assert "MODE" not in header_lines[0]


def test_interactive_home_keeps_descriptions_on_narrow_terminals() -> None:
    text = _render_text(_home(40), 40)
    assert "Deep static" in text
    assert "Stream one log" in text
    assert "Correlate multiple live" in text
    assert "opt-in" in text.lower()
    assert max(len(line) for line in text.splitlines()) <= 40
