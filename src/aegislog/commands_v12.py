from __future__ import annotations

import os
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

from .commands_v11 import dashboard
from .commands_v13 import live_dashboard
from .commands_v14 import live_multi
from .config import config_dir

console = Console()

_DEMO_LOG = """Aug 29 12:01:01 demo sshd[1001]: Failed password for root from 203.0.113.7 port 2201 ssh2
Aug 29 12:01:02 demo sshd[1002]: Failed password for root from 203.0.113.7 port 2202 ssh2
Aug 29 12:01:03 demo sshd[1003]: Failed password for root from 203.0.113.7 port 2203 ssh2
Aug 29 12:01:04 demo sshd[1004]: Failed password for admin from 203.0.113.7 port 2204 ssh2
Aug 29 12:01:05 demo sshd[1005]: Failed password for admin from 203.0.113.7 port 2205 ssh2
Aug 29 12:01:06 demo sshd[1006]: Failed password for ubuntu from 203.0.113.7 port 2206 ssh2
Aug 29 12:02:10 demo api[212]: ERROR database connection timeout
"""


def _clear() -> None:
    if os.environ.get("AEGISLOG_NO_CLEAR") != "1": console.clear()


def _header() -> Panel:
    body = Text("AEGISLOG AI", style="bold cyan"); body.append("\nSingle-file defensive log intelligence", style="dim")
    return Panel(body, border_style="cyan")


def _menu() -> Table:
    table = Table(show_header=False, box=None, padding=(0, 1)); table.add_column(style="bold cyan", width=4); table.add_column()
    table.add_row("1", "Analyze a log file"); table.add_row("2", "Open real-time dashboard"); table.add_row("3", "Open multi-source live SOC")
    table.add_row("4", "Analyze native system/container logs"); table.add_row("5", "Run built-in demo analysis"); table.add_row("6", "System check"); table.add_row("7", "Show useful commands"); table.add_row("Q", "Exit AegisLog")
    return table


def _resolve_demo() -> Path:
    bundled = Path.cwd() / "sample_logs" / "auth.log"
    if bundled.is_file(): return bundled
    demo = config_dir() / "demo_auth.log"
    try:
        if not demo.exists() or demo.read_text(encoding="utf-8") != _DEMO_LOG: demo.write_text(_DEMO_LOG, encoding="utf-8")
    except OSError:
        demo = Path.cwd() / "aegislog_demo_auth.log"; demo.write_text(_DEMO_LOG, encoding="utf-8")
    return demo


def _path(raw: str) -> Path | None:
    path = Path(raw.strip().strip('"').strip("'")).expanduser()
    if not path.exists(): console.print("[red]That path does not exist.[/red]"); return None
    if path.is_dir(): console.print("[yellow]Choose an actual log file, not a folder.[/yellow]"); return None
    return path


def _choose_log_file() -> Path | None:
    raw = Prompt.ask("[bold]Enter log file path[/bold]").strip(); return _path(raw) if raw else None


def _choose_log_files() -> list[Path]:
    raw = Prompt.ask("[bold]Enter 2+ log paths separated by semicolons[/bold]").strip(); paths: list[Path] = []
    for item in raw.split(";"):
        if not item.strip(): continue
        path = _path(item)
        if path is not None and path not in paths: paths.append(path)
    if len(paths) < 2: console.print("[yellow]Multi-source monitoring needs at least two different log files.[/yellow]"); return []
    return paths


def _native_menu() -> None:
    from .commands_v17 import native_analyze
    import platform
    choices = ["docker"]
    if platform.system() == "Windows": choices = ["windows", "docker"]
    elif platform.system() == "Linux": choices = ["journald", "docker"]
    source = Prompt.ask("Native source", choices=choices, default=choices[0])
    if source == "windows":
        channel = Prompt.ask("Windows channel", choices=["System", "Application", "Security"], default="System"); native_analyze(source, channel=channel)
    elif source == "docker":
        container = Prompt.ask("Docker container name or ID").strip()
        if container: native_analyze(source, container=container)
    else: native_analyze(source)


def _system_check() -> None:
    import platform
    from .native_collectors import source_status
    table = Table(title="AegisLog system check"); table.add_column("Check"); table.add_column("Status")
    runtime = "Bundled Windows runtime" if getattr(sys, "frozen", False) else f"Python {sys.version.split()[0]}"
    table.add_row("Runtime", runtime); table.add_row("Platform", platform.platform()); table.add_row("Configuration", str(config_dir())); table.add_row("Local engine", "READY"); table.add_row("Real-time monitor", "READY"); table.add_row("Multi-source correlation", "READY")
    for item in source_status(): table.add_row(item.label, "READY" if item.available else "NOT ON THIS OS")
    console.print(table)


def _commands() -> None:
    executable = "AegisLog.exe" if getattr(sys, "frozen", False) else "aegislog"
    table = Table(title="Useful commands"); table.add_column("Command", style="cyan"); table.add_column("Purpose")
    table.add_row(executable, "Open this terminal control center"); table.add_row(f"{executable} native-sources", "Show native OS/container sources"); table.add_row(f"{executable} native-analyze windows --channel Security", "Analyze Windows Event Logs"); table.add_row(f"{executable} native-analyze journald", "Analyze Linux journald"); table.add_row(f"{executable} native-analyze docker --container <name>", "Analyze Docker container logs"); table.add_row(f"{executable} live <file>", "Follow one growing log with the real-time dashboard"); table.add_row(f"{executable} live-multi <file1> <file2> ...", "Correlate multiple live logs in one terminal SOC"); table.add_row(f"{executable} dashboard <file>", "Analyze one log and show the investigation dashboard"); table.add_row(f"{executable} doctor", "Check the local AegisLog environment"); console.print(table)


def start() -> None:
    """Open the AegisLog one-terminal interactive control center."""
    while True:
        _clear(); console.print(_header()); console.print(_menu()); console.print()
        choice = Prompt.ask("Select", choices=["1", "2", "3", "4", "5", "6", "7", "q", "Q"], default="1")
        if choice.lower() == "q": console.print("[cyan]AegisLog closed safely.[/cyan]"); return
        if choice == "1":
            path = _choose_log_file()
            if path is not None: console.print(); dashboard(path)
        elif choice == "2":
            path = _choose_log_file()
            if path is not None: console.print(); live_dashboard(path)
        elif choice == "3":
            paths = _choose_log_files()
            if paths: console.print(); live_multi(paths)
        elif choice == "4": console.print(); _native_menu()
        elif choice == "5": console.print(); dashboard(_resolve_demo())
        elif choice == "6": _system_check()
        elif choice == "7": _commands()
        console.print(); Prompt.ask("Press Enter to return to the AegisLog menu", default="")
