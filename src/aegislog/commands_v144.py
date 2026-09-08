from __future__ import annotations

from pathlib import Path

from rich.console import Console, Group, RenderableType
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

from .commands_v11 import dashboard
from .commands_v12 import (
    _choose_profile,
    _command_prompt,
    _menu_action_error,
    _native_choice,
    _path,
    _resolve_demo,
    _run_inline_command,
)
from .commands_v13 import live_dashboard
from .commands_v14 import live_multi
from .console_pages import commands_reference, system_check
from .theme import (
    ACCENT,
    ACCENT_SOFT,
    HIGH,
    INCIDENT,
    INFO,
    MUTED,
    SUCCESS,
    WARNING,
    severity_text,
)

console = Console()
_NARROW_MENU_BREAKPOINT = 72
_WIDE_MENU_BREAKPOINT = 118


def _frame_width(screen_width: int | None = None) -> int:
    """Use the full available terminal viewport with a one-cell safety margin."""
    width = console.size.width if screen_width is None else screen_width
    return max(1, width - 2)


def _brand_mark() -> Text:
    mark = Text()
    mark.append(" /\\ ", style=f"bold {ACCENT}")
    mark.append("AEGIS", style=f"bold {ACCENT}")
    mark.append("LOG", style="bold white")
    return mark


def _header(screen_width: int | None = None) -> Panel:
    """Render the AegisLog terminal identity as a branded command banner."""
    frame_width = _frame_width(screen_width)
    banner = Text()
    if frame_width >= 90:
        banner.append("        /\\        ", style=f"bold {ACCENT}")
        banner.append("AEGISLOG", style=f"bold {ACCENT}")
        banner.append("  SECURITY OPERATIONS CONSOLE", style="bold white")
        banner.append("  v1.6.1\n", style=MUTED)
        banner.append("       /  \\       ", style=f"bold {INFO}")
        banner.append("READY", style=f"bold {SUCCESS}")
        banner.append("    LOCAL-FIRST", style=f"bold {ACCENT_SOFT}")
        banner.append("    READ-ONLY MONITORING", style=MUTED)
        banner.append("\n")
        banner.append("      / /\\ \\      ", style=f"bold {INCIDENT}")
        banner.append("REMOTE AI / OPT-IN", style=MUTED)
        banner.append("    DEFENSIVE ANALYSIS", style=f"bold {INFO}")
        banner.append("\n")
        banner.append("     /_/  \\_\\     ", style=f"bold {ACCENT}")
        banner.append("LOCAL SOC WORKSPACE", style=f"bold {ACCENT_SOFT}")
    elif frame_width >= 76:
        banner.append("    /\\      ", style=f"bold {ACCENT}")
        banner.append("AEGISLOG", style=f"bold {ACCENT}")
        banner.append("  SECURITY OPERATIONS CONSOLE", style="bold white")
        banner.append("  v1.6.1\n", style=MUTED)
        banner.append("   /  \\     ", style=f"bold {INFO}")
        banner.append("READY", style=f"bold {SUCCESS}")
        banner.append("    LOCAL-FIRST", style=f"bold {ACCENT_SOFT}")
        banner.append("\n")
        banner.append("  /_/\\_\\    ", style=f"bold {INCIDENT}")
        banner.append("READ-ONLY", style=MUTED)
        banner.append("    AI / OPT-IN", style=MUTED)
    else:
        banner.append("AEGISLOG", style=f"bold {ACCENT}")
        banner.append("  SECURITY OPERATIONS  v1.6.1\n", style="bold white")
        banner.append("READY", style=f"bold {SUCCESS}")
        banner.append("  LOCAL-FIRST", style=f"bold {ACCENT_SOFT}")
        banner.append("\nREAD-ONLY MONITORING", style=MUTED)
        banner.append("  REMOTE AI / OPT-IN", style=MUTED)
    return Panel(banner, border_style=ACCENT, padding=(1, 2), width=frame_width)


def _operation_header(
    title: str,
    subtitle: str,
    accent: str = ACCENT,
    *,
    screen_width: int | None = None,
) -> Panel:
    """Give every interactive workflow the same product-level identity."""
    width = _frame_width(screen_width)
    body = Text()
    body.append_text(_brand_mark())
    body.append("  //  ", style=MUTED)
    body.append(title, style=f"bold {accent}")
    body.append("\n")
    body.append(subtitle, style="bold white")
    body.append("\n\n")
    body.append("LOCAL", style=f"bold {SUCCESS}")
    body.append("  defensive processing    ", style=MUTED)
    body.append("READ-ONLY", style=f"bold {INFO}")
    body.append("  source preserved    ", style=MUTED)
    body.append("AI", style=f"bold {INCIDENT}")
    body.append("  opt-in only", style=MUTED)
    return Panel(
        body,
        title=Text(" ACTIVE WORKSPACE ", style=f"bold {accent}"),
        title_align="left",
        border_style=accent,
        padding=(1, 2),
        width=width,
    )


def _input_panel(
    title: str,
    lines: list[tuple[str, str]],
    accent: str = ACCENT,
    *,
    screen_width: int | None = None,
) -> Panel:
    frame_width = _frame_width(screen_width)
    grid = Table.grid(expand=True, padding=(0, 1))
    grid.add_column(width=12 if frame_width < 60 else 16, no_wrap=True)
    grid.add_column(ratio=1, overflow="fold")
    for label, value in lines:
        grid.add_row(Text(label, style=f"bold {accent}"), Text(value, style=MUTED))
    return Panel(
        grid,
        title=Text(f" {title} ", style=f"bold {accent}"),
        title_align="left",
        border_style=accent,
        padding=(1, 2),
        width=frame_width,
    )


def _command_card(title: str, rows: list[tuple[str, str, str]], width: int, accent: str) -> Panel:
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
    system = [
        ("07", "DEMO", "Open the built-in investigation dataset"),
        ("08", "HEALTH", "Inspect engine and collector readiness"),
        ("09", "COMMANDS", "Browse the complete command reference"),
    ]
    control = [
        ("C", "COMMAND MODE", "Open the direct-command interface"),
        ("Q", "EXIT", "Close AegisLog safely"),
    ]
    if frame_width < _NARROW_MENU_BREAKPOINT:
        table = Table.grid(expand=True, padding=(0, 1))
        table.add_column(width=5, justify="center", no_wrap=True)
        table.add_column(ratio=1, overflow="fold")
        sections = (
            ("OPERATIONS", core, ACCENT),
            ("INVESTIGATE", investigate, INCIDENT),
            ("SYSTEM / TOOLS", system, INFO),
            ("CONTROL", control, WARNING),
        )
        for heading, rows, accent in sections:
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
        right = Group(
            _command_card("SYSTEM / TOOLS", system, right_width, INFO),
            _command_card("CONTROL", control, right_width, WARNING),
        )
        layout = Table.grid(expand=True, padding=0)
        layout.add_column(width=left_width)
        layout.add_column(width=gap)
        layout.add_column(width=right_width)
        layout.add_row(left, Text(""), right)
        return layout
    return Group(
        _command_card("OPERATIONS", core, frame_width, ACCENT),
        _command_card("INVESTIGATION", investigate, frame_width, INCIDENT),
        _command_card("SYSTEM / TOOLS", system, frame_width, INFO),
        _command_card("CONTROL", control, frame_width, WARNING),
    )


def _home(screen_width: int | None = None) -> RenderableType:
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
    try:
        console.input(f"\n[{MUTED}]press Enter to return to console[/{MUTED}]")
    except (KeyboardInterrupt, EOFError):
        pass


def _choose_single_file_workspace(
    title: str,
    subtitle: str,
    accent: str = ACCENT,
    *,
    output_note: str,
) -> Path | None:
    """Collect one path without dropping out of the branded workspace."""
    while True:
        console.clear()
        console.print(_operation_header(title, subtitle, accent))
        console.print()
        console.print(
            _input_panel(
                "SOURCE INPUT",
                [
                    ("INPUT", "Drag a log file here or paste its full path"),
                    ("DEMO", "Type demo to use the built-in investigation dataset"),
                    ("BACK", "Type back to return to Mission Control"),
                    ("OUTPUT", output_note),
                ],
                accent,
            )
        )
        console.print()
        raw = Prompt.ask(f"[bold {accent}]log source[/bold {accent}]").strip()
        if not raw or raw.lower() in {"b", "back", "cancel"}:
            return None
        if raw.lower() in {"demo", "sample"}:
            return _resolve_demo()
        path = _path(raw)
        if path is not None:
            return path
        _pause_for_menu()


def _choose_multisource_files() -> list[Path]:
    paths: list[Path] = []
    number = 1
    while True:
        console.clear()
        console.print(
            _operation_header(
                "MULTI-SOURCE SOC",
                "Build a live correlation workspace across multiple telemetry sources.",
                INCIDENT,
            )
        )
        console.print()
        selected = ", ".join(path.name for path in paths) if paths else "No sources selected yet"
        console.print(
            _input_panel(
                "TELEMETRY SOURCES",
                [
                    ("SELECTED", selected),
                    ("REQUIRED", "At least two different existing log files"),
                    ("INPUT", "Add one path at a time; drag-and-drop is supported"),
                    ("CONTROL", "Type back to cancel"),
                ],
                INCIDENT,
            )
        )
        console.print()
        raw = Prompt.ask(f"[bold {INCIDENT}]log source {number}[/bold {INCIDENT}]").strip()
        if not raw:
            continue
        if raw.lower() in {"b", "back", "cancel"}:
            return []
        path = _path(raw)
        if path is None:
            continue
        resolved = path.resolve()
        if any(existing.resolve() == resolved for existing in paths):
            console.print(Text("That source is already selected.", style=WARNING))
            _pause_for_menu()
            continue
        paths.append(path)
        number += 1
        if len(paths) >= 2:
            more = Prompt.ask("Next", choices=["start", "add", "back"], default="start")
            if more == "start":
                return paths
            if more == "back":
                return []


def _choose_profile_workspace(
    title: str,
    subtitle: str,
    *,
    default: str = "security",
    accent: str = INFO,
) -> str:
    console.clear()
    console.print(_operation_header(title, subtitle, accent))
    console.print()
    console.print(
        _input_panel(
            "WATCH PROFILE",
            [
                ("SECURITY", "Balanced defensive detection across common security signals"),
                ("AUTH", "Authentication failures, account activity, and brute-force patterns"),
                ("WEB", "Web/API errors and suspicious request activity"),
                ("DOCKER", "Container-focused operational and security signals"),
                ("OPERATIONS", "Availability, runtime, and service-health signals"),
            ],
            accent,
        )
    )
    console.print()
    return _choose_profile(default)


def _choose_native_workspace(title: str, subtitle: str, accent: str) -> tuple[str, str, str] | None:
    console.clear()
    console.print(_operation_header(title, subtitle, accent))
    console.print()
    console.print(
        _input_panel(
            "NATIVE SOURCE",
            [
                ("WINDOWS", "Windows Event Logs when running on Windows"),
                ("JOURNALD", "systemd journal when running on Linux"),
                ("DOCKER", "Container logs when Docker is available"),
                ("ACCESS", "Read-only collection; AegisLog does not change host configuration"),
            ],
            accent,
        )
    )
    console.print()
    return _native_choice()


def _run_analysis_workspace(path: Path, title: str, subtitle: str, accent: str = ACCENT) -> None:
    console.clear()
    console.print(_operation_header(title, subtitle, accent))
    console.print()
    console.print(
        _input_panel(
            "INVESTIGATION STATUS",
            [
                ("SOURCE", str(path)),
                ("ENGINE", "Local defensive analysis"),
                ("SOURCE MODE", "Read-only"),
                ("REPORT", "HTML investigation report will be written automatically"),
            ],
            accent,
        )
    )
    console.print()
    dashboard(path, timestamp_year=None)


def _launch_live_file(path: Path, profile: str) -> None:
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


def _launch_native_analysis(choice: tuple[str, str, str]) -> None:
    from .commands_v17 import native_analyze

    source, channel, container = choice
    try:
        native_analyze(source, limit=300, channel=channel, container=container)
    except Exception as exc:
        _menu_action_error("Native analysis", exc)


def _launch_native_live(choice: tuple[str, str, str], profile: str) -> None:
    from .commands_v18 import native_live

    source, channel, container = choice
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


def _incident_workspace() -> None:
    from .commands_v19 import explain
    from .investigation import load_investigation

    path = _choose_single_file_workspace(
        "INCIDENT INTELLIGENCE",
        "Select a source to reconstruct evidence chains and explain correlated activity.",
        INCIDENT,
        output_note="Local incident list and evidence-backed explanation",
    )
    if path is None:
        return

    console.clear()
    console.print(
        _operation_header(
            "INCIDENT INTELLIGENCE",
            "Review correlated incidents before opening the evidence explanation.",
            INCIDENT,
        )
    )
    console.print()
    try:
        _, incidents, _ = load_investigation(path)
    except Exception as exc:
        _menu_action_error("Incident intelligence", exc)
        return
    if not incidents:
        console.print(
            _input_panel(
                "INCIDENT STATUS",
                [
                    ("SOURCE", str(path)),
                    ("RESULT", "No correlated incidents were detected in this log"),
                    ("NEXT", "Return to Mission Control or analyze a different source"),
                ],
                WARNING,
            )
        )
        return

    table = Table(
        title="INCIDENT QUEUE",
        title_style=f"bold {INCIDENT}",
        border_style=INCIDENT,
        expand=True,
        padding=(0, 1),
    )
    table.add_column("Incident ID", width=14, style=INCIDENT, no_wrap=True)
    table.add_column("Severity", width=10)
    table.add_column("Confidence", justify="right", width=12, style=ACCENT)
    table.add_column("Summary", ratio=1, overflow="fold")
    for item in incidents[:12]:
        table.add_row(
            Text(item.id, style=INCIDENT),
            severity_text(item.severity),
            f"{item.confidence}%",
            Text(item.title),
        )
    console.print(table)
    console.print()
    incident_id = Prompt.ask("Incident ID to explain", default=incidents[0].id).strip()
    if not incident_id:
        return
    console.clear()
    console.print(
        _operation_header(
            "INCIDENT EXPLANATION",
            "Local evidence-backed explanation for the selected correlated incident.",
            INCIDENT,
        )
    )
    console.print()
    explain(path, incident_id)


def start() -> None:
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
        console.clear()
        try:
            if choice in {"1", "01"}:
                path = _choose_single_file_workspace(
                    "ANALYZE LOG",
                    "Start a static defensive investigation and produce a complete report.",
                    ACCENT,
                    output_note="HTML investigation report generated automatically after analysis",
                )
                if path is not None:
                    _run_analysis_workspace(
                        path,
                        "ANALYZE LOG",
                        "Static defensive investigation with automatic report generation.",
                        ACCENT,
                    )
            elif choice in {"2", "02"}:
                path = _choose_single_file_workspace(
                    "LIVE MONITOR",
                    "Open a continuous read-only detection session for one log source.",
                    INFO,
                    output_note="Continuous terminal dashboard; Ctrl+C returns to Mission Control",
                )
                if path is not None:
                    profile = _choose_profile_workspace(
                        "LIVE MONITOR",
                        f"Configure continuous detection for {path.name}.",
                        default="security",
                        accent=INFO,
                    )
                    console.clear()
                    _launch_live_file(path, profile)
            elif choice in {"3", "03"}:
                paths = _choose_multisource_files()
                if paths:
                    profile = _choose_profile_workspace(
                        "MULTI-SOURCE SOC",
                        f"Configure correlation across {len(paths)} selected telemetry sources.",
                        default="security",
                        accent=INCIDENT,
                    )
                    console.clear()
                    _launch_live_multi_current(paths, profile)
            elif choice in {"4", "04"}:
                native_choice = _choose_native_workspace(
                    "NATIVE LOGS",
                    "Inspect supported operating-system or container telemetry.",
                    INCIDENT,
                )
                if native_choice is not None:
                    console.clear()
                    console.print(
                        _operation_header(
                            "NATIVE LOGS",
                            "Collecting a bounded read-only snapshot from the selected native source.",
                            INCIDENT,
                        )
                    )
                    console.print()
                    _launch_native_analysis(native_choice)
            elif choice in {"5", "05"}:
                native_choice = _choose_native_workspace(
                    "NATIVE MONITOR",
                    "Watch supported native telemetry continuously in read-only mode.",
                    INFO,
                )
                if native_choice is not None:
                    source = native_choice[0]
                    profile = _choose_profile_workspace(
                        "NATIVE MONITOR",
                        f"Configure the live {source} telemetry workspace.",
                        default="docker" if source == "docker" else "security",
                        accent=INFO,
                    )
                    console.clear()
                    _launch_native_live(native_choice, profile)
            elif choice in {"6", "06"}:
                _incident_workspace()
            elif choice in {"7", "07"}:
                _run_analysis_workspace(
                    _resolve_demo(),
                    "DEMO INVESTIGATION",
                    "Run the built-in defensive dataset through the complete analysis pipeline.",
                    ACCENT,
                )
            elif choice in {"8", "08"}:
                console.print(
                    _operation_header(
                        "SYSTEM HEALTH",
                        "Inspect engine, runtime, and collector readiness.",
                        SUCCESS,
                    )
                )
                console.print()
                system_check()
            elif choice in {"9", "09"}:
                console.print(
                    _operation_header(
                        "COMMAND REFERENCE",
                        "Browse supported AegisLog workflows and direct commands.",
                        INFO,
                    )
                )
                console.print()
                commands_reference()
            elif lowered == "c":
                console.print(
                    _operation_header(
                        "COMMAND MODE",
                        "Direct access to the AegisLog command interface.",
                        WARNING,
                    )
                )
                console.print()
                _command_prompt()
            elif lowered in {"help", "commands", "?"}:
                console.print(
                    _operation_header(
                        "COMMAND REFERENCE",
                        "Browse supported AegisLog workflows and direct commands.",
                        INFO,
                    )
                )
                console.print()
                commands_reference()
            else:
                _run_inline_command(choice)
        except KeyboardInterrupt:
            console.print()
            console.print(Text("Stopped - returning to the AegisLog menu.", style=WARNING))
            continue
        _pause_for_menu()
