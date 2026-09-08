from __future__ import annotations

from pathlib import Path

import pytest
from rich.console import Console

from aegislog.commands_v144 import _frame_width, _header, _home
from aegislog.multisource import MultiSourceState, render_multisource
from aegislog.realtime import RealtimeState, render_realtime


def _render_text(renderable, width: int) -> str:
    console = Console(width=width, record=True, color_system=None, force_terminal=False)
    console.print(renderable)
    return console.export_text(clear=False)


def test_multisource_dashboard_keeps_all_sections_at_standard_width() -> None:
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

    width = 100
    text = _render_text(render_multisource(state), width)

    for label in (
        "MULTI-SOURCE REAL-TIME SOC",
        "SOC summary",
        "Profile telemetry",
        "Rate & baseline intelligence",
        "Live security alert feed",
        "Monitoring status",
    ):
        assert label in text
    assert max(len(line) for line in text.splitlines()) <= width


def test_realtime_dashboard_keeps_all_sections_at_standard_width() -> None:
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

    width = 100
    text = _render_text(render_realtime(state), width)

    for label in (
        "REAL-TIME DEFENSIVE MONITOR",
        "Live summary",
        "Profile telemetry",
        "Rate & baseline intelligence",
        "Recent findings - Security",
        "Live status",
    ):
        assert label in text
    assert max(len(line) for line in text.splitlines()) <= width


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
    assert "[+] ENGINE ONLINE" in plain
    assert "[-] REMOTE AI OFF BY DEFAULT" in plain
    assert "●" not in plain
    assert "○" not in plain


@pytest.mark.parametrize("width", [40, 50, 59, 60, 80, 100, 120, 160, 220])
def test_interactive_home_fits_terminal_width(width: int) -> None:
    text = _render_text(_home(width), width)
    assert "AEGISLOG" in text
    assert "ANALYZE LOG" in text
    assert "MULTI-SOURCE SOC" in text
    assert "INCIDENT INTEL" in text
    assert "COMMAND MODE" in text
    assert "Remote AI is opt-in" in text
    assert max(len(line) for line in text.splitlines()) <= width


def test_interactive_home_caps_wide_terminal_content() -> None:
    assert _frame_width(100) == 84
    assert _frame_width(160) == 84
    assert _frame_width(220) == 84
    assert _frame_width(60) == 58
    assert _frame_width(40) == 38


def test_interactive_home_is_left_anchored_on_wide_terminals() -> None:
    text = _render_text(_home(220), 220)
    lines = [line for line in text.splitlines() if line]
    assert lines[0].startswith("╭") or lines[0].startswith("┌")
    assert max(len(line) for line in lines) <= 84
    assert "Ctrl+C exits live views | Remote AI is opt-in" in text


def test_interactive_home_keeps_descriptions_on_narrow_terminals() -> None:
    text = _render_text(_home(40), 40)
    assert "Static log investigation" in text
    assert "Real-time event monitoring" in text
    assert "Correlate multiple log sources" in text
    assert max(len(line) for line in text.splitlines()) <= 40