from __future__ import annotations

import time

import typer
from rich.console import Console
from rich.live import Live
from rich.text import Text

from .live_ux import live_initial_status, live_startup_panel, live_stopped_status
from .native_collectors import CollectorError
from .native_live import NativeLivePoller
from .realtime import RealtimeState, render_realtime
from .theme import WARNING
from .watch_profiles import get_profile

console = Console()


def native_live(
    source: str = typer.Argument(..., help="windows, journald, or docker"),
    refresh: float = typer.Option(2.0, "--refresh", min=0.5, max=30.0, help="Native source polling interval in seconds."),
    window: int = typer.Option(500, "--window", min=20, max=10000, help="Rolling analysis window in lines."),
    limit: int = typer.Option(300, "--limit", min=1, max=5000, help="Events requested from the source on each poll."),
    from_start: bool = typer.Option(False, "--from-start", help="Include the current source snapshot before following new events."),
    channel: str = typer.Option("System", "--channel", help="Windows: System, Application, or Security"),
    container: str = typer.Option("", "--container", help="Docker container name or ID"),
    profile: str = typer.Option("all", "--profile", help="Watch profile: all, security, authentication, web, docker, operations."),
) -> None:
    """Continuously collect a native source into a profile-focused AegisLog dashboard."""
    normalized = source.strip().lower()
    try:
        selected = get_profile(profile)
    except ValueError as exc:
        raise typer.BadParameter(str(exc), param_hint="--profile") from exc
    poller = NativeLivePoller(normalized, limit=limit, channel=channel, container=container)
    state = RealtimeState(source=f"native:{normalized}", window_size=window, watch_profile=selected.key)
    try:
        initial = poller.prime(include_existing=from_start)
    except CollectorError as exc:
        message = Text("Native live collection failed: ", style="bold bright_red")
        message.append(str(exc))
        console.print(message)
        raise typer.Exit(code=2) from exc
    if initial:
        state.ingest(initial)

    collector_detail = f"limit={limit}"
    if normalized == "windows":
        collector_detail += f", channel={channel}"
    elif normalized == "docker" and container:
        collector_detail += f", container={container}"
    console.print(
        live_startup_panel(
            title="NATIVE TELEMETRY MONITOR",
            sources=(f"native:{normalized}",),
            profile=selected.label,
            mode="Current snapshot + new events" if from_start else "New native events after startup",
            window=window,
            refresh=refresh,
            extra=collector_detail,
        )
    )
    if from_start:
        console.print(render_realtime(state))
        console.print(live_initial_status("native", prefix="Initial native scan complete."))

    try:
        with Live(
            render_realtime(state),
            console=console,
            refresh_per_second=max(1, int(round(1 / refresh))),
            screen=False,
            transient=False,
        ) as live:
            while True:
                try:
                    lines = poller.poll()
                    if lines:
                        state.ingest(lines)
                except CollectorError as exc:
                    live.update(render_realtime(state), refresh=True)
                    warning = Text("Native source temporarily unavailable: ", style=f"bold {WARNING}")
                    warning.append(str(exc))
                    console.print(warning)
                    time.sleep(refresh)
                    continue
                live.update(render_realtime(state), refresh=True)
                time.sleep(refresh)
    except KeyboardInterrupt:
        console.print(live_stopped_status("Native"))
