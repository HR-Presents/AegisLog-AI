from __future__ import annotations

import time
from pathlib import Path

import typer
from rich.console import Console
from rich.live import Live

from .live_ux import live_initial_status, live_startup_panel, live_stopped_status
from .realtime import RealtimeState, initial_cursor, read_new_lines_cursor, render_realtime
from .watch_profiles import get_profile

console = Console()


def live_dashboard(
    path: Path = typer.Argument(..., exists=True, dir_okay=False),
    from_start: bool = typer.Option(False, "--from-start", help="Analyze existing content before following new lines."),
    refresh: float = typer.Option(1.0, "--refresh", min=0.2, max=10.0, help="Dashboard refresh interval in seconds."),
    window: int = typer.Option(500, "--window", min=20, max=10000, help="Rolling analysis window in lines."),
    profile: str = typer.Option("all", "--profile", help="Watch profile: all, security, authentication, web, docker, operations."),
) -> None:
    """Follow a growing log file with an optional defensive watch profile."""
    try:
        selected = get_profile(profile)
    except ValueError as exc:
        raise typer.BadParameter(str(exc), param_hint="--profile") from exc
    state = RealtimeState(source=str(path), window_size=window, watch_profile=selected.key)
    cursor = initial_cursor(path, from_start=from_start)

    if from_start:
        initial, cursor = read_new_lines_cursor(path, cursor)
        state.ingest(initial)

    mode = "Existing content + new lines" if from_start else "New lines appended after startup"
    console.print(
        live_startup_panel(
            title="LIVE FILE MONITOR",
            sources=(str(path),),
            profile=selected.label,
            mode=mode,
            window=window,
            refresh=refresh,
        )
    )
    if from_start:
        console.print(render_realtime(state))
        console.print(live_initial_status("file", prefix="Initial scan complete."))

    try:
        with Live(
            render_realtime(state),
            console=console,
            refresh_per_second=max(1, int(round(1 / refresh))),
            screen=False,
            transient=False,
        ) as live:
            while True:
                if not path.exists():
                    live.update(render_realtime(state), refresh=True)
                    time.sleep(refresh)
                    continue
                lines, cursor = read_new_lines_cursor(path, cursor)
                if lines:
                    state.ingest(lines)
                live.update(render_realtime(state), refresh=True)
                time.sleep(refresh)
    except KeyboardInterrupt:
        console.print(live_stopped_status("File"))
