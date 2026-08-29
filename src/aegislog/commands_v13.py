from __future__ import annotations

import time
from pathlib import Path

import typer
from rich.console import Console
from rich.live import Live

from .realtime import RealtimeState, initial_cursor, read_new_lines_cursor, render_realtime

console = Console()


def live_dashboard(
    path: Path = typer.Argument(..., exists=True, dir_okay=False),
    from_start: bool = typer.Option(False, "--from-start", help="Analyze existing content before following new lines."),
    refresh: float = typer.Option(1.0, "--refresh", min=0.2, max=10.0, help="Dashboard refresh interval in seconds."),
    window: int = typer.Option(500, "--window", min=20, max=10000, help="Rolling analysis window in lines."),
) -> None:
    """Follow a growing log file and render a continuously updating terminal dashboard."""
    state = RealtimeState(source=str(path), window_size=window)
    cursor = initial_cursor(path, from_start=from_start)

    if from_start:
        initial, cursor = read_new_lines_cursor(path, cursor)
        state.ingest(initial)

    console.print("[cyan]Starting AegisLog real-time monitor. Press Ctrl+C to stop safely.[/cyan]")
    try:
        with Live(render_realtime(state), console=console, refresh_per_second=max(1, int(round(1 / refresh))), screen=True) as live:
            while True:
                if not path.exists():
                    live.update(render_realtime(state))
                    time.sleep(refresh)
                    continue
                lines, cursor = read_new_lines_cursor(path, cursor)
                if lines:
                    state.ingest(lines)
                live.update(render_realtime(state))
                time.sleep(refresh)
    except KeyboardInterrupt:
        console.print("\n[cyan]Real-time monitoring stopped safely.[/cyan]")
