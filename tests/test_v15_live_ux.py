from __future__ import annotations

from rich.console import Console

from aegislog.live_ux import live_initial_status, live_startup_panel, live_stopped_status


def _render(renderable) -> str:
    console = Console(record=True, width=140)
    console.print(renderable)
    return console.export_text()


def test_live_startup_panel_surfaces_operator_context() -> None:
    output = _render(
        live_startup_panel(
            title="MULTI-SOURCE SOC MONITOR",
            sources=("auth.log", "web.log"),
            profile="Security",
            mode="Existing content + new lines",
            window=1000,
            refresh=1.0,
            extra="Trend window 60s",
        )
    )
    assert "MULTI-SOURCE SOC MONITOR" in output
    assert "Security" in output
    assert "Existing content + new lines" in output
    assert "1,000 lines" in output
    assert "auth.log" in output and "web.log" in output
    assert "read-only" in output
    assert "Ctrl+C" in output


def test_live_status_messages_make_state_explicit() -> None:
    initial = _render(live_initial_status("native"))
    stopped = _render(live_stopped_status("Native"))
    assert "Initial native scan complete" in initial
    assert "remains active" in initial
    assert "Native monitoring stopped safely" in stopped
    assert "No host configuration or source data was modified" in stopped
