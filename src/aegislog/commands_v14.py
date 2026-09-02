from __future__ import annotations

import time
from pathlib import Path

import typer
from rich.console import Console
from rich.live import Live

from .live_ux import live_initial_status, live_startup_panel, live_stopped_status
from .multisource import MultiSourceState, initial_cursors, poll_sources, render_multisource
from .watch_profiles import get_profile

console = Console()


def live_multi(
    paths: list[Path] = typer.Argument(..., exists=True, dir_okay=False, help="Two or more log files to monitor together."),
    from_start: bool = typer.Option(False, "--from-start", help="Analyze existing content before following new lines."),
    refresh: float = typer.Option(1.0, "--refresh", min=0.2, max=10.0, help="Dashboard refresh interval in seconds."),
    window: int = typer.Option(1000, "--window", min=20, max=20000, help="Unified rolling correlation window in lines."),
    trend_seconds: int = typer.Option(60, "--trend-seconds", min=10, max=3600, help="Window used for live event-rate calculation."),
    profile: str = typer.Option("all", "--profile", help="Watch profile: all, security, authentication, web, docker, operations."),
) -> None:
    """Monitor multiple growing log files in one profile-focused real-time terminal SOC."""
    unique = tuple(dict.fromkeys(path.resolve() for path in paths))
    if len(unique) < 2:
        raise typer.BadParameter("Provide at least two different log files for multi-source monitoring.")
    try:
        selected = get_profile(profile)
    except ValueError as exc:
        raise typer.BadParameter(str(exc), param_hint="--profile") from exc
    state = MultiSourceState(
        sources=unique,
        window_size=window,
        trend_seconds=trend_seconds,
        watch_profile=selected.key,
    )
    cursors = initial_cursors(unique, from_start=from_start)
    if from_start:
        batches, cursors = poll_sources(unique, cursors)
        for path, lines in batches:
            state.ingest(path, lines)

    mode = "Existing content + new lines" if from_start else "New lines appended after startup"
    console.print(
        live_startup_panel(
            title="MULTI-SOURCE SOC MONITOR",
            sources=(str(path) for path in unique),
            profile=selected.label,
            mode=mode,
            window=window,
            refresh=refresh,
            extra=f"Trend window {trend_seconds}s",
        )
    )
    if from_start:
        console.print(render_multisource(state))
        console.print(live_initial_status("multi-source"))

    try:
        with Live(
            render_multisource(state),
            console=console,
            refresh_per_second=max(1, int(round(1 / refresh))),
            screen=False,
            transient=False,
        ) as live:
            while True:
                batches, cursors = poll_sources(unique, cursors)
                for path, lines in batches:
                    state.ingest(path, lines)
                live.update(render_multisource(state), refresh=True)
                time.sleep(refresh)
    except KeyboardInterrupt:
        console.print(live_stopped_status("Multi-source"))
