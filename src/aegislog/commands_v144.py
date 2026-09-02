from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.text import Text

from .commands_v11 import dashboard
from .commands_v12 import (
    _choose_log_file,
    _choose_log_files,
    _choose_profile,
    _command_prompt,
    _commands,
    _explain_menu,
    _header,
    _menu,
    _menu_action_error,
    _native_choice,
    _native_menu,
    _resolve_demo,
    _run_inline_command,
    _system_check,
)
from .commands_v13 import live_dashboard
from .commands_v14 import live_multi
from .theme import ACCENT, MUTED, SUCCESS, WARNING

console = Console()


def _pause_for_menu() -> None:
    """Wait for a plain Enter without Rich's empty-default `()` prompt."""
    try:
        console.input(f"\n[{MUTED}]Press Enter to return to the AegisLog menu[/{MUTED}]")
    except (KeyboardInterrupt, EOFError):
        pass


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
        console.print(
            Text(
                "Numbers are shortcuts. Live options load the current source first, then continue monitoring. "
                "Press Ctrl+C inside a live view to return here.",
                style=MUTED,
            )
        )
        try:
            from rich.prompt import Prompt

            choice = Prompt.ask(f"[bold {ACCENT}]Select or command[/bold {ACCENT}]", default="1").strip()
        except (KeyboardInterrupt, EOFError):
            console.print()
            console.print(Text("AegisLog closed safely.", style=SUCCESS))
            return

        lowered = choice.lower()
        if lowered == "q":
            console.print(Text("AegisLog closed safely.", style=SUCCESS))
            return

        try:
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
                    _launch_live_file(path, profile)
            elif choice == "3":
                paths = _choose_log_files()
                if paths:
                    profile = _choose_profile()
                    console.print()
                    _launch_live_multi_current(paths, profile)
            elif choice == "4":
                console.print()
                _native_menu()
            elif choice == "5":
                console.print()
                _native_live_current()
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
