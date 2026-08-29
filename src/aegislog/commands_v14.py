from __future__ import annotations

import time
from pathlib import Path

import typer
from rich.console import Console
from rich.live import Live

from .multisource import MultiSourceState, initial_offsets, poll_sources, render_multisource

console = Console()


def live_multi(
    paths: list[Path] = typer.Argument(..., exists=True, dir_okay=False, help="Two or more log files to monitor together."),
    from_start: bool = typer.Option(False, "--from-start", help="Analyze existing content before following new lines."),
    refresh: float = typer.Option(1.0, "--refresh", min=0.2, max=10.0, help="Dashboard refresh interval in seconds."),
    window: int = typer.Option(1000, "--window", min=20, max=20000, help="Unified rolling correlation window in lines."),
    trend_seconds: int = typer.Option(60, "--trend-seconds", min=10, max=3600, help="Window used for live event-rate calculation."),
) -> None:
    """Monitor multiple growing log files in one correlated real-time terminal SOC."""
    unique = tuple(dict.fromkeys(path.resolve() for path in paths))
    if len(unique) < 2:
        raise typer.BadParameter("Provide at least two different log files for multi-source monitoring.")
    state = MultiSourceState(sources=unique, window_size=window, trend_seconds=trend_seconds)
    offsets = initial_offsets(unique, from_start=from_start)
    if from_start:
        batches, offsets = poll_sources(unique, offsets)
        for path, lines in batches:
            state.ingest(path, lines)

    console.print("[cyan]Starting AegisLog multi-source real-time SOC. Press Ctrl+C to stop safely.[/cyan]")
    try:
        with Live(render_multisource(state), console=console, refresh_per_second=max(1, int(round(1 / refresh))), screen=True) as live:
            while True:
                batches, offsets = poll_sources(unique, offsets)
                for path, lines in batches:
                    state.ingest(path, lines)
                live.update(render_multisource(state))
                time.sleep(refresh)
    except KeyboardInterrupt:
        console.print("\n[cyan]Multi-source monitoring stopped safely.[/cyan]")
