from __future__ import annotations

from pathlib import Path

from rich.console import Console, Group, RenderableType
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
_MAX_HOME_WIDTH = 88
_NARROW_MENU_BREAKPOINT = 64


def _frame_width(screen_width: int | None = None) -> int:
    """Return a compact content width that never grows wider than the terminal."""
    width = console.size.width if screen_width is None else screen_width
    return max(1, min(max(width - 2, 1), _MAX_HOME_WIDTH))


def _header(screen_width: int | None = None) -> Panel:
    """Render a compact command-center identity and runtime posture."""
    frame_width = _frame_width(screen_width)
    title = Text()
    title.append("AEGISLOG", style=f"bold {ACCENT}")
    title.append(" // SECURITY OPERATIONS", style="bold white")
    title.append("  v1.6.1", style=MUTED)

    status = Text()
    separator = "   " if frame_width >= 76 else "\n"
    status.append("READY", style=f"bold {SUCCESS}")
    status.append(separator)
    status.append("LOCAL", style=f"bold {ACCENT_SOFT}")
    status.append(separator)
    status.append("REMOTE AI: OPT-IN", style=MUTED)

    return Panel(
        Text.assemble(title, "\n", status),
        border_style=ACCENT_SOFT,
        padding=(0, 1),
        width=frame_width,
    )


def _menu(screen_width: int | None = None) -> Table:
    """Render the command matrix with a deliberate narrow-screen fallback."""
    frame_width = _frame_width(screen_width)
    narrow = frame_width < _NARROW_MENU_BREAKPOINT
    table = Table(
        show_header=not narrow,
        header_style=MUTED,
        box=None,
        padding=(0, 1),
        expand=False,
        width=frame_width,
    )
    table.add_column("KEY" if not narrow else "", max_width=4, justify="right", style=f"bold {ACCENT}", no_wrap=True)

    if narrow:
        table.add_column(ratio=1, overflow="fold")
    else:
        table.add_column("ACTION", min_width=16, max_width=20, style="bold white", overflow="fold")
        table.add_column("PURPOSE", min_width=20, ratio=1, style=MUTED, overflow="fold")

    def section(label: str) -> None:
        heading = Text(f"-- {label}", style=f"bold {ACCENT_SOFT}")
        if narrow:
            table.add_row("", heading)
        else:
            table.add_row("", heading, "")

    def action(key: str, command: str | Text, description: str) -> None:
        if narrow:
            body = Text()
            if isinstance(command, Text):
                body.append_text(command)
            else:
                body.append(command, style="bold white")
            body.append("\n")
            body.append(description, style=MUTED)
            table.add_row(key, body)
        else:
            table.add_row(key, command, description)

    section("OPERATIONS")
    action("01", "ANALYZE LOG", "Static log investigation")
    action("02", "LIVE MONITOR", "Real-time event monitoring")
    action("03", "MULTI-SOURCE SOC", "Correlate multiple log sources")
    section("INVESTIGATION")
    action("04", "NATIVE LOGS", "System and container telemetry")
    action("05", "NATIVE MONITOR", "Live native telemetry")
    action("06", "INCIDENT INTEL", "Explain a correlated incident")
    section("TOOLS")
    action("07", "DEMO", "Run demonstration dataset")
    action("08", "HEALTH", "Engine diagnostics")
    action("09", "COMMANDS", "CLI reference")
    action("C", Text("COMMAND MODE", style=f"bold {ACCENT}"), "Run a direct AegisLog command")
    action("Q", Text("EXIT", style=f"bold {HIGH}"), "Close the console")
    return table


def _home(screen_width: int | None = None) -> RenderableType:
    """Render one left-anchored SOC shell at every terminal width."""
    frame_width = _frame_width(screen_width)
    menu_panel = Panel(
        _menu(screen_width),
        title=Text("OPERATOR MENU", style=f"bold {ACCENT_SOFT}"),
        title_align="left",
        border_style=ACCENT_SOFT,
        padding=(0, 0),
        width=frame_width,
    )
    if frame_width < 48:
        footer = Text("Ctrl+C: stop live | AI: opt-in", style=MUTED)
    else:
        footer = Text("Ctrl+C stops live views safely | Remote AI requires explicit opt-in", style=MUTED)
    return Group(_header(screen_width), menu_panel, footer)


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
        console.print(Text("Live monitoring stopped - returning to the AegisLog menu.", style=SUCCESS))
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
        console.print(Text("Multi-source monitoring stopped - returning to the AegisLog menu.", style=SUCCESS))
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
        console.print(Text("Native monitoring stopped - returning to the AegisLog menu.", style=SUCCESS))
    except Exception as exc:
        _menu_action_error("Native real-time monitor", exc)


def start() -> None:
    """Open the hardened one-terminal control center used by the packaged EXE."""
    while True:
        console.clear()
        console.print(_home(console.size.width))
        console.print()
        try:
            raw_choice = console.input(f"[bold {ACCENT}]aegis@console > [/bold {ACCENT}]")
            choice = raw_choice.strip() or "1"
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
            console.print(Text("Stopped - returning to the AegisLog menu.", style=WARNING))
            continue

        _pause_for_menu()
