from __future__ import annotations

from pathlib import Path

from rich.console import Console

from aegislog.commands_v144 import _header
from aegislog.multisource import MultiSourceState, render_multisource


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


def test_interactive_header_uses_legacy_console_safe_status_text() -> None:
    plain = _header().renderable.plain
    plain.encode("cp1252")
    assert "[+] ENGINE ONLINE" in plain
    assert "[-] REMOTE AI OFF BY DEFAULT" in plain
    assert "●" not in plain
    assert "○" not in plain
