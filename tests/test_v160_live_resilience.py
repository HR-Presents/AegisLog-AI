from __future__ import annotations

from rich.console import Console

from aegislog.live_ux import live_source_status, live_stopped_status


def _render(renderable: object) -> str:
    console = Console(record=True, width=180)
    console.print(renderable)
    return console.export_text()


def test_missing_source_status_is_read_only_and_retry_focused() -> None:
    output = _render(live_source_status("auth.log", available=False))

    assert "Source temporarily unavailable" in output
    assert "auth.log" in output
    assert "retry read-only polling" in output


def test_recovered_source_status_confirms_automatic_resume() -> None:
    output = _render(live_source_status("auth.log", available=True))

    assert "Source recovered" in output
    assert "Monitoring resumed automatically" in output
    assert "safe cursor" in output


def test_degraded_stop_keeps_no_host_change_boundary() -> None:
    output = _render(live_stopped_status("File", degraded=True))

    assert "monitoring stopped safely" in output
    assert "No host configuration or source data was modified" in output
