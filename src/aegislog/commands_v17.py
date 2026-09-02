from __future__ import annotations

import tempfile
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table
from rich.text import Text

from .commands_v11 import dashboard
from .native_collectors import CollectorError, collect, source_status
from .native_diagnostics import failure_guidance, source_state
from .theme import ACCENT, MUTED, SUCCESS, WARNING

console = Console()


def native_sources() -> None:
    """Show native operating-system and container log sources."""
    table = Table(title="Native log sources", border_style=ACCENT)
    table.add_column("Source", style=ACCENT)
    table.add_column("Status")
    table.add_column("Details", style=MUTED)
    for item in source_status():
        label, style = source_state(item)
        table.add_row(Text(item.label), Text(label, style=style), Text(item.detail))
    console.print(table)
    console.print(
        Text(
            "Native collectors are read-only. Unsupported sources stay disabled; unavailable sources should be fixed at the source/permission layer rather than by changing host policy.",
            style=MUTED,
        )
    )


def _dashboard_lines(lines: list[str], source: str) -> None:
    if not lines:
        message = Text("No events were returned from ", style=WARNING)
        message.append(source)
        message.append(".", style=WARNING)
        console.print(message)
        return
    path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".log", prefix="aegislog-native-", delete=False) as handle:
            handle.writelines(lines)
            path = Path(handle.name)
        dashboard(path)
    finally:
        if path is not None:
            path.unlink(missing_ok=True)


def native_analyze(
    source: str = typer.Argument(..., help="windows, journald, or docker"),
    limit: int = typer.Option(300, "--limit", min=1, max=5000),
    channel: str = typer.Option("System", "--channel", help="Windows: System, Application, or Security"),
    container: str = typer.Option("", "--container", help="Docker container name or ID"),
) -> None:
    """Collect a read-only native log snapshot and analyze it locally."""
    source = source.strip().lower()
    try:
        lines = collect(source, limit=limit, channel=channel, container=container)
    except CollectorError as exc:
        message = Text("Native collection failed: ", style="bold bright_red")
        message.append(str(exc))
        console.print(message)
        console.print(failure_guidance(source, str(exc)))
        raise typer.Exit(code=2) from exc
    message = Text(f"Collected {len(lines):,} events", style=SUCCESS)
    message.append(" from ")
    message.append(source, style=ACCENT)
    message.append(". Analyzing locally...", style=MUTED)
    console.print(message)
    _dashboard_lines(lines, source)
