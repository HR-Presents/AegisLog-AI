from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

from .commands_v11 import dashboard
from .commands_v12 import (
    _choose_log_file,
    _choose_profile,
    _command_prompt,
    _commands,
    _explain_menu,
    _menu_action_error,
    _native_choice,
    _native_menu,
    _path,
    _resolve_demo,
    _run_inline_command,
    _system_check,
)
from .commands_v13 import live_dashboard
from .commands_v14 import live_multi
from .theme import ACCENT, ACCENT_SOFT, HIGH, MUTED, SUCCESS, WARNING

console = Console()


def _header() -> Panel:
    """Render a compact, analyst-focused SOC console header."""
    line = Text()
    line.append("AEGISLOG", style=f"bold {ACCENT}")
    line.append(" // SECURITY OPERATIONS CONSOLE", style="bold white")
    line.append("  v1.6.1", style=MUTED)
    status = Text()
    status.append("● ENGINE ONLINE", style=f"bold {SUCCESS}")
    status.append("    ● LOCAL MODE", style=f"bold {ACCENT_SOFT}")
    status.append("    ○ REMOTE AI OFF BY DEFAULT", style=MUTED)
    body = Text.assemble(line, "\n", status)
    return Panel(body, border_style=ACCENT_SOFT, padding=(0, 1))


def _menu() -> Table:
    """Render a dense command matrix that reads like an analyst console."""
    table = Table(show_header=False, box=None, padding=(0, 1), expand=True)
    table.add_column(width=4, justify="right", style=f"bold {ACCENT}", no_wrap=True)
    table.add_column(width=24, style="bold white", no_wrap=True)
    table.add_column(style=MUTED)

    def section(label: str) -> None:
        table.add_row("", Text(f"── {label}", style=f"bold {ACCENT_SOFT}"), "")

    section("OPERATIONS")
    table.add_row("01", "ANALYZE LOG", "Static log investigation")
    table.add_row("02", "LIVE MONITOR", "Real-time event monitoring")
    table.add_row("03", "MULTI-SOURCE SOC", "Correlate multiple log sources")
    section("INVESTIGATION")
    table.add_row("04", "NATIVE LOGS", "System and container telemetry")
    table.add_row("05", "NATIVE MONITOR", "Live native telemetry")
    table.add_row("06", "INCIDENT INTEL", "Explain a correlated incident")
    section("TOOLS")
    table.add_row("07", "DEMO", "Run demonstration dataset")
    table.add_row("08", "HEALTH", "Engine diagnostics")
    table.add_row("09", "COMMANDS", "CLI reference")
    table.add_row("C", Text("COMMAND MODE", style=f"bold {ACCENT}"), "Run a direct AegisLog command")
    table.add_row("Q", Text("EXIT", style=f"bold {HIGH}"), "Close the console")
    return table


def _pause_for_menu() -> None:
    """Wait for a plain Enter without Rich's empty-default prompt."""
    try:
        console.input(f"\n[{MUTED}]press Enter to return to console[/{MUTED}]")
    except (KeyboardInterrupt, EOFError):
        pass


def _choose_multisource_files() -> list[Path]:
    """Collect multi-source paths one at a time for a drag-and-drop friendly UX."""
    console.print(Text("Add at least two different log files. Enter each file separately.", style=MUTED))
    console.print(Text("After file 2, choose Start monitoring or keep adding more files.", style=MUTED))
    paths: list[Path] = []
    number = 1
    while True:
        raw = Prompt.ask(f"[bold]Log file {number}[/bold]").strip()
        if not raw:
            console.print(Text("Enter an existing log file, or type back to cancel.", style=WARNING))
            continue
        if raw.lower() in {"b", "back", "cancel"}:
            return []
        path = _path(raw)
        if path is None:
            continue
        resolved = path.resolve()
        if any(existing.resolve() == resolved for existing in paths):
            console.print(Text("That file is already selected. Choose a different log file.", style=WARNING))
            continue
        paths.append(path)
        console.print(Text(f"Added file {len(paths)}: {path.name}", style=SUCCESS))
        number += 1
        if len(paths) >= 2:
            more = Prompt.ask("Next", choices=["start", "add", "back"], default="start")
            if more == "start":
                return paths
            if more == "back":
                return []


def _launch_live_file(path: Path, profile: str) -> None:
    """Interactive live mode starts with the current file so it never looks frozen."""
    try:
        live_dashboard(path, from_start=True, refresh=1.0, window=500, profile=profile)
    except KeyboardInterrupt:
        console.print(Text("Live monitoring stopped — returning to the AegisLog menu.", style=SUCCESS))
    except Exception as exc:
        _menu_action_error("Real-time file dashboard", exc)


def _launch_live_multi_current(paths: list[Path], profile: str) -> None:
    try:
        live_multi(
            paths,
            from_start=True,
            refresh=1.0,
            window=1000,
            trend_seconds=60,
            profile=profile,
        )
    except KeyboardInterrupt:
        console.print(Text("Multi-source monitoring stopped — returning to the AegisLog menu.", style=SUCCESS))
    except Exception as exc:
        _menu_action_error("Multi-source live SOC", exc)


def _native_live_current() -> None:
    from .commands_v18 import native_live

    choice = _native_choice()
    if choice is None:
        return
    source, channel, container = choice
    profile = _choose_profile("docker" if source == "docker" else "security")
    try:
        native_live(
            source,
            refresh=2.0,
            window=500,
            limit=300,
            from_start=True,
            channel=channel,
            container=container,
            profile=profile,
        )
    except KeyboardInterrupt:
        console.print(Text("Native monitoring stopped — returning to the AegisLog menu.", style=SUCCESS))
    except Exception as exc:
        _menu_action_error("Native real-time monitor", exc)


def start() -> None:
    """Open the hardened one-terminal control center used by the packaged EXE."""
    while True:
        console.clear()
        console.print(_header())
        console.print(_menu())
        console.print()
        console.print(Text("Ctrl+C exits a live view and returns here. Remote AI remains opt-in.", style=MUTED))
        try:
            choice = Prompt.ask(f"[bold {ACCENT}]aegis@console ›[/bold {ACCENT}]", default="1").strip()
        except (KeyboardInterrupt, EOFError):
            console.print()
            console.print(Text("AegisLog closed safely.", style=SUCCESS))
            return

        lowered = choice.lower()
        if lowered == "q":
            console.print(Text("AegisLog closed safely.", style=SUCCESS))
            return

        try:
            if choice in {"1", "01"}:
                path = _choose_log_file()
                if path is not None:
                    console.print()
                    dashboard(path, timestamp_year=None)
            elif choice in {"2", "02"}:
                path = _choose_log_file()
                if path is not None:
                    profile = _choose_profile()
                    console.print()
                    _launch_live_file(path, profile)
            elif choice in {"3", "03"}:
                paths = _choose_multisource_files()
                if paths:
                    profile = _choose_profile()
                    console.print()
                    _launch_live_multi_current(paths, profile)
            elif choice in {"4", "04"}:
                console.print()
                _native_menu()
            elif choice in {"5", "05"}:
                console.print()
                _native_live_current()
            elif choice in {"6", "06"}:
                console.print()
                _explain_menu()
            elif choice in {"7", "07"}:
                console.print()
                dashboard(_resolve_demo(), timestamp_year=None)
            elif choice in {"8", "08"}:
                _system_check()
            elif choice in {"9", "09"}:
                _commands()
            elif lowered == "c":
                _command_prompt()
            elif lowered in {"help", "commands", "?"}:
                _commands()
            else:
                console.print()
                _run_inline_command(choice)
        except KeyboardInterrupt:
            console.print()
            console.print(Text("Stopped — returning to the AegisLog menu.", style=WARNING))
            continue

        _pause_for_menu()
