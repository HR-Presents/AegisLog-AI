from __future__ import annotations

import tempfile
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .commands_v11 import dashboard
from .native_collectors import CollectorError, collect, source_status

console = Console()


def native_sources() -> None:
    """Show native operating-system and container log sources."""
    table = Table(title="Native log sources")
    table.add_column("Source")
    table.add_column("Status")
    table.add_column("Details")
    for item in source_status():
        table.add_row(item.label, "READY" if item.available else "NOT ON THIS OS", item.detail)
    console.print(table)


def _dashboard_lines(lines: list[str], source: str) -> None:
    if not lines:
        console.print(f"[yellow]No events were returned from {source}.[/yellow]")
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
        console.print(f"[red]Native collection failed:[/red] {exc}")
        raise typer.Exit(code=2) from exc
    console.print(f"[cyan]Collected {len(lines):,} events from {source}. Analyzing locally...[/cyan]")
    _dashboard_lines(lines, source)
