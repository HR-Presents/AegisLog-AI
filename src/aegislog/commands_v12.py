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
from .watch_profiles import get_profile, profile_choices

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
    if os.environ.get("AEGISLOG_NO_CLEAR") != "1":
        console.clear()


def _header() -> Panel:
    body = Text("AEGISLOG AI", style="bold cyan")
    body.append("\nSingle-file defensive log intelligence", style="dim")
    return Panel(body, border_style="cyan")


def _menu() -> Table:
    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column(style="bold cyan", width=4)
    table.add_column()
    table.add_row("1", "Analyze a log file")
    table.add_row("2", "Open real-time file dashboard")
    table.add_row("3", "Open multi-source live SOC")
    table.add_row("4", "Analyze native system/container logs")
    table.add_row("5", "Open native real-time monitor")
    table.add_row("6", "Explain an incident")
    table.add_row("7", "Run built-in demo analysis")
    table.add_row("8", "System check")
    table.add_row("9", "Show useful commands")
    table.add_row("Q", "Exit AegisLog")
    return table


def _resolve_demo() -> Path:
    bundled = Path.cwd() / "sample_logs" / "auth.log"
    if bundled.is_file():
        return bundled
    demo = config_dir() / "demo_auth.log"
    try:
        if not demo.exists() or demo.read_text(encoding="utf-8") != _DEMO_LOG:
            demo.write_text(_DEMO_LOG, encoding="utf-8")
    except OSError:
        demo = Path.cwd() / "aegislog_demo_auth.log"
        demo.write_text(_DEMO_LOG, encoding="utf-8")
    return demo


def _path(raw: str) -> Path | None:
    path = Path(raw.strip().strip('"').strip("'")).expanduser()
    if not path.exists():
        console.print("[red]That path does not exist.[/red]")
        return None
    if path.is_dir():
        console.print("[yellow]Choose an actual log file, not a folder.[/yellow]")
        return None
    return path


def _choose_log_file() -> Path | None:
    raw = Prompt.ask("[bold]Enter log file path[/bold]").strip()
    return _path(raw) if raw else None


def _choose_log_files() -> list[Path]:
    raw = Prompt.ask("[bold]Enter 2+ log paths separated by semicolons[/bold]").strip()
    paths: list[Path] = []
    for item in raw.split(";"):
        if not item.strip():
            continue
        path = _path(item)
        if path is not None and path not in paths:
            paths.append(path)
    if len(paths) < 2:
        console.print("[yellow]Multi-source monitoring needs at least two different log files.[/yellow]")
        return []
    return paths


def _choose_profile(default: str = "security") -> str:
    choices = list(profile_choices())
    selected = Prompt.ask("Watch profile", choices=choices, default=default)
    return get_profile(selected).key


def _native_choice() -> tuple[str, str, str] | None:
    import platform

    choices = ["docker"]
    if platform.system() == "Windows":
        choices = ["windows", "docker"]
    elif platform.system() == "Linux":
        choices = ["journald", "docker"]
    source = Prompt.ask("Native source", choices=choices, default=choices[0])
    channel = "System"
    container = ""
    if source == "windows":
        channel = Prompt.ask("Windows channel", choices=["System", "Application", "Security"], default="System")
    elif source == "docker":
        container = Prompt.ask("Docker container name or ID").strip()
        if not container:
            return None
    return source, channel, container


def _native_menu() -> None:
    from .commands_v17 import native_analyze

    choice = _native_choice()
    if choice is None:
        return
    source, channel, container = choice
    native_analyze(source, channel=channel, container=container)


def _native_live_menu() -> None:
    from .commands_v18 import native_live

    choice = _native_choice()
    if choice is None:
        return
    source, channel, container = choice
    profile = _choose_profile("docker" if source == "docker" else "security")
    native_live(source, channel=channel, container=container, profile=profile)


def _explain_menu() -> None:
    from .commands_v19 import explain
    from .investigation import load_investigation

    path = _choose_log_file()
    if path is None:
        return
    _, incidents, _ = load_investigation(path)
    if not incidents:
        console.print("[yellow]No correlated incidents were detected in this log.[/yellow]")
        return
    table = Table(title="Detected incidents")
    table.add_column("Incident ID", width=14)
    table.add_column("Severity", width=10)
    table.add_column("Confidence", justify="right", width=12)
    table.add_column("Summary")
    for item in incidents[:12]:
        table.add_row(item.id, item.severity, f"{item.confidence}%", Text(item.title))
    console.print(table)
    incident_id = Prompt.ask("Incident ID to explain", default=incidents[0].id).strip()
    if incident_id:
        explain(path, incident_id)


def _system_check() -> None:
    import platform

    from .native_collectors import source_status

    table = Table(title="AegisLog system check")
    table.add_column("Check")
    table.add_column("Status")
    runtime = "Bundled Windows runtime" if getattr(sys, "frozen", False) else f"Python {sys.version.split()[0]}"
    table.add_row("Runtime", runtime)
    table.add_row("Platform", platform.platform())
    table.add_row("Configuration", str(config_dir()))
    table.add_row("Local engine", "READY")
    table.add_row("Incident explanation", "READY — local only")
    table.add_row("Watch profiles", "READY — Security/Auth/Web/Docker/Operations")
    table.add_row("Real-time file monitor", "READY")
    table.add_row("Multi-source correlation", "READY")
    table.add_row("Native live monitor", "READY")
    for item in source_status():
        table.add_row(item.label, "READY" if item.available else "NOT ON THIS OS")
    console.print(table)


def _commands() -> None:
    executable = "AegisLog.exe" if getattr(sys, "frozen", False) else "aegislog"
    table = Table(title="Useful commands")
    table.add_column("Command", style="cyan")
    table.add_column("Purpose")
    table.add_row(executable, "Open this terminal control center")
    table.add_row(f"{executable} incidents <file>", "List correlated incidents and confidence")
    table.add_row(f"{executable} explain <file> <incident-id>", "Explain an incident locally in plain analyst language")
    table.add_row(f"{executable} mitre <file>", "Show evidence-supported MITRE ATT&CK context")
    table.add_row(f"{executable} native-sources", "Show native OS/container sources")
    table.add_row(f"{executable} live <file> --profile security", "Follow one log with a focused Security watch profile")
    table.add_row(f"{executable} live-multi <file1> <file2> --profile authentication", "Correlate multiple logs with an Authentication profile")
    table.add_row(f"{executable} native-live windows --channel Security --profile security", "Continuously monitor Windows Event Logs")
    table.add_row(f"{executable} native-live journald --profile operations", "Continuously monitor Linux operations signals")
    table.add_row(f"{executable} native-live docker --container <name> --profile docker", "Continuously monitor Docker-focused signals")
    table.add_row(f"{executable} dashboard <file>", "Analyze one log and show the investigation dashboard")
    table.add_row(f"{executable} doctor", "Check the local AegisLog environment")
    console.print(table)


def start() -> None:
    """Open the AegisLog one-terminal interactive control center."""
    while True:
        _clear()
        console.print(_header())
        console.print(_menu())
        console.print()
        choice = Prompt.ask("Select", choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "q", "Q"], default="1")
        if choice.lower() == "q":
            console.print("[cyan]AegisLog closed safely.[/cyan]")
            return
        if choice == "1":
            path = _choose_log_file()
            if path is not None:
                console.print()
                dashboard(path)
        elif choice == "2":
            path = _choose_log_file()
            if path is not None:
                profile = _choose_profile()
                console.print()
                live_dashboard(path, profile=profile)
        elif choice == "3":
            paths = _choose_log_files()
            if paths:
                profile = _choose_profile()
                console.print()
                live_multi(paths, profile=profile)
        elif choice == "4":
            console.print()
            _native_menu()
        elif choice == "5":
            console.print()
            _native_live_menu()
        elif choice == "6":
            console.print()
            _explain_menu()
        elif choice == "7":
            console.print()
            dashboard(_resolve_demo())
        elif choice == "8":
            _system_check()
        elif choice == "9":
            _commands()
        console.print()
        Prompt.ask("Press Enter to return to the AegisLog menu", default="")
