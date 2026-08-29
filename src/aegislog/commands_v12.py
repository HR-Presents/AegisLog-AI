from __future__ import annotations

import os
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

from .commands_v11 import dashboard
from .config import config_dir

console = Console()


def _clear() -> None:
    if os.environ.get("AEGISLOG_NO_CLEAR") != "1":
        console.clear()


def _header() -> Panel:
    title = Text("AEGISLOG AI", style="bold cyan")
    subtitle = Text("One-terminal defensive log intelligence", style="dim")
    body = Text()
    body.append_text(title)
    body.append("\n")
    body.append_text(subtitle)
    return Panel(body, border_style="cyan")


def _menu() -> Table:
    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column(style="bold cyan", width=4)
    table.add_column()
    table.add_row("1", "Analyze a log file")
    table.add_row("2", "Analyze bundled demo log")
    table.add_row("3", "System check")
    table.add_row("4", "Show useful commands")
    table.add_row("Q", "Exit AegisLog")
    return table


def _resolve_demo() -> Path | None:
    candidates = [
        Path.cwd() / "sample_logs" / "auth.log",
        Path.cwd().parent / "sample_logs" / "auth.log",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def _choose_log_file() -> Path | None:
    raw = Prompt.ask("[bold]Enter log file path[/bold]").strip().strip('"').strip("'")
    if not raw:
        return None
    path = Path(raw).expanduser()
    if not path.exists():
        console.print("[red]That path does not exist.[/red]")
        return None
    if path.is_dir():
        console.print("[yellow]You selected a folder. Choose an actual log file such as auth.log, syslog, or app.log.[/yellow]")
        return None
    return path


def _system_check() -> None:
    import platform
    import sys

    table = Table(title="AegisLog system check")
    table.add_column("Check")
    table.add_column("Status")
    table.add_row("Python", sys.version.split()[0])
    table.add_row("Platform", platform.platform())
    table.add_row("Configuration", str(config_dir()))
    table.add_row("Local engine", "READY")
    console.print(table)


def _commands() -> None:
    table = Table(title="Useful commands")
    table.add_column("Command", style="cyan")
    table.add_column("Purpose")
    table.add_row("aegislog start", "Open this terminal control center")
    table.add_row("aegislog dashboard <file>", "Analyze one log and show the investigation dashboard")
    table.add_row("aegislog analyze <file>", "Analyze a log with dashboard and local rule packs")
    table.add_row("aegislog stream <file>", "Run bounded-memory streaming analysis")
    table.add_row("aegislog report", "Generate a report from stored analysis data")
    table.add_row("aegislog doctor", "Check the local AegisLog environment")
    console.print(table)


def start() -> None:
    """Open the AegisLog one-terminal interactive control center."""
    while True:
        _clear()
        console.print(_header())
        console.print(_menu())
        console.print()
        choice = Prompt.ask("Select", choices=["1", "2", "3", "4", "q", "Q"], default="1")

        if choice.lower() == "q":
            console.print("[cyan]AegisLog closed safely.[/cyan]")
            return

        if choice == "1":
            path = _choose_log_file()
            if path is not None:
                console.print()
                dashboard(path)
        elif choice == "2":
            path = _resolve_demo()
            if path is None:
                console.print("[yellow]The bundled sample log could not be found. Choose option 1 and select a log file manually.[/yellow]")
            else:
                console.print()
                dashboard(path)
        elif choice == "3":
            _system_check()
        elif choice == "4":
            _commands()

        console.print()
        Prompt.ask("Press Enter to return to the AegisLog menu", default="")
