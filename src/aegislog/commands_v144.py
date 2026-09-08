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
    _explain_menu,
    _menu_action_error,
    _native_choice,
    _native_menu,
    _path,
    _resolve_demo,
    _run_inline_command,
)
from .commands_v13 import live_dashboard
from .commands_v14 import live_multi
from .console_pages import commands_reference, system_check
from .theme import ACCENT, ACCENT_SOFT, HIGH, INCIDENT, INFO, MUTED, SUCCESS, WARNING

console = Console()
_NARROW_MENU_BREAKPOINT = 72
_WIDE_MENU_BREAKPOINT = 118


def _frame_width(screen_width: int | None = None) -> int:
    """Use the full available terminal viewport with a one-cell safety margin."""
    width = console.size.width if screen_width is None else screen_width
    return max(1, width - 2)


def _header(screen_width: int | None = None) -> Panel:
    """Render the AegisLog terminal identity as a compact branded command banner."""
    frame_width = _frame_width(screen_width)
    banner = Text()

    if frame_width >= 76:
        banner.append("    /\\      ", style=f"bold {ACCENT}")
        banner.append("AEGISLOG", style=f"bold {ACCENT}")
        banner.append("  SECURITY OPERATIONS CONSOLE", style="bold white")
        banner.append("  v1.6.1\n", style=MUTED)
        banner.append("   /  \\     ", style=f"bold {INFO}")
        banner.append("READY", style=f"bold {SUCCESS}")
        banner.append("    LOCAL-FIRST", style=f"bold {ACCENT_SOFT}")
        banner.append("    READ-ONLY MONITORING", style=MUTED)
        banner.append("\n", style=MUTED)
        banner.append("  /_/\\_\\    ", style=f"bold {INCIDENT}")
        banner.append("REMOTE AI / OPT-IN", style=MUTED)
        banner.append("    DEFENSIVE ANALYSIS", style=f"bold {INFO}")
    else:
        banner.append("AEGISLOG", style=f"bold {ACCENT}")
        banner.append("  SECURITY OPERATIONS  v1.6.1\n", style="bold white")
        banner.append("READY", style=f"bold {SUCCESS}")
        banner.append("  LOCAL-FIRST", style=f"bold {ACCENT_SOFT}")
        banner.append("\nREAD-ONLY MONITORING", style=MUTED)
        banner.append("  REMOTE AI / OPT-IN", style=MUTED)

    return Panel(
        banner,
        border_style=ACCENT,
        padding=(1, 2),
        width=frame_width,
    )


def _command_card(
    title: str,
    rows: list[tuple[str, str, str]],
    width: int,
    accent: str,
) -> Panel:
    """Build one colored command zone with strong visual hierarchy."""
    grid = Table.grid(expand=True, padding=(0, 1))
    grid.add_column(width=6, justify="center", no_wrap=True)
    grid.add_column(width=20, no_wrap=True)
    grid.add_column(ratio=1, overflow="fold")
    for key, action, description in rows:
        key_style = f"bold black on {accent}"
        action_style = f"bold {accent}"
        if key == "C":
            key_style = f"bold black on {WARNING}"
            action_style = f"bold {WARNING}"
        elif key == "Q":
            key_style = "bold white on red"
            action_style = f"bold {HIGH}"
        grid.add_row(
            Text(f" {key} ", style=key_style),
            Text(action, style=action_style),
            Text(description, style=MUTED),
        )
    return Panel(
        grid,
        title=Text(f" {title} ", style=f"bold {accent}"),
        title_align="left",
        border_style=accent,
        padding=(1, 1),
        width=width,
    )


def _menu(screen_width: int | None = None) -> RenderableType:
    """Render responsive command zones that use wide terminals intentionally."""
    frame_width = _frame_width(screen_width)
    core = [
        ("01", "ANALYZE LOG", "Static investigation + automatic HTML report"),
        ("02", "LIVE MONITOR", "Watch one log with continuous detection"),
        ("03", "MULTI-SOURCE SOC", "Correlate multiple live sources"),
    ]
    investigate = [
        ("04", "NATIVE LOGS", "Inspect Windows, Linux, or container telemetry"),
        ("05", "NATIVE MONITOR", "Watch supported native telemetry read-only"),
        ("06", "INCIDENT INTEL", "Reconstruct incidents and evidence chains"),
    ]
    tools = [
        ("07", "DEMO", "Open the built-in investigation dataset"),
        ("08", "HEALTH", "Inspect engine and collector readiness"),
        ("09", "COMMANDS", "Browse the complete command reference"),
        ("C", "COMMAND MODE", "Open the direct-command interface"),
        ("Q", "EXIT", "Close AegisLog safely"),
    ]

    if frame_width < _NARROW_MENU_BREAKPOINT:
        table = Table.grid(expand=True, padding=(0, 1))
        table.add_column(width=5, justify="center", no_wrap=True)
        table.add_column(ratio=1, overflow="fold")
        for heading, rows, accent in (
            ("OPERATIONS", core, ACCENT),
            ("INVESTIGATE", investigate, INCIDENT),
            ("SYSTEM", tools, INFO),
        ):
            table.add_row("", Text(heading, style=f"bold {accent}"))
            for key, action, description in rows:
                body = Text(action, style=f"bold {accent}")
                body.append("\n")
                body.append(description, style=MUTED)
                table.add_row(Text(key, style=f"bold {accent}"), body)
        return Panel(
            table,
            title=Text(" MISSION CONTROL ", style=f"bold {ACCENT}"),
            title_align="left",
            border_style=ACCENT_SOFT,
            width=frame_width,
        )

    if frame_width >= _WIDE_MENU_BREAKPOINT:
        gap = 2
        left_width = (frame_width - gap) // 2
        right_width = frame_width - gap - left_width
        left = Group(
            _command_card("OPERATIONS", core, left_width, ACCENT),
            _command_card("INVESTIGATION", investigate, left_width, INCIDENT),
        )
        right = _command_card("SYSTEM / TOOLS", tools, right_width, INFO)
        layout = Table.grid(expand=True, padding=0)
        layout.add_column(width=left_width)
        layout.add_column(width=gap)
        layout.add_column(width=right_width)
        layout.add_row(left, Text(""), right)
        return layout

    return Group(
        _command_card("OPERATIONS", core, frame_width, ACCENT),
        _command_card("INVESTIGATION", investigate, frame_width, INCIDENT),
        _command_card("SYSTEM / TOOLS", tools, frame_width, INFO),
    )


def _home(screen_width: int | None = None) -> RenderableType:
    """Render the responsive SOC command-center home."""
    footer = Text()
    footer.append("SELECT", style=f"bold {ACCENT}")
    footer.append("  01-09 / C     ", style=MUTED)
    footer.append("REPORT", style=f"bold {SUCCESS}")
    footer.append("  auto on analysis     ", style=MUTED)
    footer.append("CTRL+C", style=f"bold {WARNING}")
    footer.append("  stop live view     ", style=MUTED)
    footer.append("AI", style=f"bold {INCIDENT}")
    footer.append("  opt-in only", style=MUTED)
    return Group(_header(screen_width), Text(""), _menu(screen_width), Text(""), footer)


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
        live_multi(paths, from_start=True, refresh=1.0, window=1000, trend_seconds=60, profile=profile)
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
        native_live(source, refresh=2.0, window=500, limit=300, from_start=True, channel=channel, container=container, profile=profile)
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

        # Treat every selection as a new screen. This prevents the home menu from
        # being pushed upward above command output and keeps the console app-like.
        console.clear()

        try:
            if choice in {"1", "01"}:
                path = _choose_log_file()
                if path is not None:
                    console.clear()
                    dashboard(path, timestamp_year=None)
            elif choice in {"2", "02"}:
                path = _choose_log_file()
                if path is not None:
                    profile = _choose_profile()
                    console.clear()
                    _launch_live_file(path, profile)
            elif choice in {"3", "03"}:
                paths = _choose_multisource_files()
                if paths:
                    profile = _choose_profile()
                    console.clear()
                    _launch_live_multi_current(paths, profile)
            elif choice in {"4", "04"}:
                _native_menu()
            elif choice in {"5", "05"}:
                _native_live_current()
            elif choice in {"6", "06"}:
                _explain_menu()
            elif choice in {"7", "07"}:
                dashboard(_resolve_demo(), timestamp_year=None)
            elif choice in {"8", "08"}:
                system_check()
            elif choice in {"9", "09"}:
                commands_reference()
            elif lowered == "c":
                _command_prompt()
            elif lowered in {"help", "commands", "?"}:
                commands_reference()
            else:
                _run_inline_command(choice)
        except KeyboardInterrupt:
            console.print()
            console.print(Text("Stopped - returning to the AegisLog menu.", style=WARNING))
            continue

        _pause_for_menu()
