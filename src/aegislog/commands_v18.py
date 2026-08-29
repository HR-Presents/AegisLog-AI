from __future__ import annotations

import time

import typer
from rich.console import Console
from rich.live import Live

from .native_collectors import CollectorError
from .native_live import NativeLivePoller
from .realtime import RealtimeState, render_realtime

console = Console()


def native_live(
    source: str = typer.Argument(..., help="windows, journald, or docker"),
    refresh: float = typer.Option(2.0, "--refresh", min=0.5, max=30.0, help="Native source polling interval in seconds."),
    window: int = typer.Option(500, "--window", min=20, max=10000, help="Rolling analysis window in lines."),
    limit: int = typer.Option(300, "--limit", min=1, max=5000, help="Events requested from the source on each poll."),
    from_start: bool = typer.Option(False, "--from-start", help="Include the current source snapshot before following new events."),
    channel: str = typer.Option("System", "--channel", help="Windows: System, Application, or Security"),
    container: str = typer.Option("", "--container", help="Docker container name or ID"),
) -> None:
    """Continuously collect a native source and feed the real-time AegisLog dashboard."""
    normalized = source.strip().lower()
    poller = NativeLivePoller(normalized, limit=limit, channel=channel, container=container)
    state = RealtimeState(source=f"native:{normalized}", window_size=window)
    try:
        initial = poller.prime(include_existing=from_start)
    except CollectorError as exc:
        console.print(f"[red]Native live collection failed:[/red] {exc}")
        raise typer.Exit(code=2) from exc
    if initial:
        state.ingest(initial)
    console.print("[cyan]Starting native real-time monitoring. Press Ctrl+C to stop safely.[/cyan]")
    try:
        with Live(render_realtime(state), console=console, refresh_per_second=max(1, int(round(1 / refresh))), screen=True) as live:
            while True:
                try:
                    lines = poller.poll()
                    if lines:
                        state.ingest(lines)
                except CollectorError as exc:
                    live.update(render_realtime(state))
                    console.print(f"[yellow]Native source temporarily unavailable:[/yellow] {exc}")
                    time.sleep(refresh)
                    continue
                live.update(render_realtime(state))
                time.sleep(refresh)
    except KeyboardInterrupt:
        console.print("\n[cyan]Native real-time monitoring stopped safely.[/cyan]")
