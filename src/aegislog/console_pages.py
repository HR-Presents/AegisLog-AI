from __future__ import annotations

import platform
import sys

from rich.console import Console
from rich.table import Table
from rich.text import Text

from .config import config_dir
from .native_collectors import source_status
from .theme import ACCENT, ACCENT_SOFT, MUTED, SUCCESS
from .ui import bounded, compact_footer

console = Console()
_NARROW_PAGE_BREAKPOINT = 72


def _health_summary(available_native: int, total_native: int) -> Text:
    """Render a compact capability summary before the detailed health table."""
    line = Text()
    line.append("CORE CAPABILITIES", style=MUTED)
    line.append("  READY", style=f"bold {SUCCESS}")
    line.append("  /  ", style=MUTED)
    line.append("NATIVE SOURCES", style=MUTED)
    line.append(f"  {available_native}/{total_native}", style=f"bold {ACCENT}")
    line.append("  /  HOST CHECK  READ-ONLY", style=MUTED)
    return line


def _command_summary(executable: str) -> Text:
    """Render the three highest-value command entry points before the full reference."""
    line = Text()
    line.append("START", style=MUTED)
    line.append(f"  {executable}", style=f"bold {ACCENT}")
    line.append("  /  ANALYZE", style=MUTED)
    line.append(f"  {executable} dashboard <file>", style=f"bold {ACCENT}")
    line.append("  /  HELP", style=MUTED)
    line.append(f"  {executable} --help", style=f"bold {ACCENT}")
    return line


def _health_table(rows: list[tuple[str, Text, str]], screen_width: int) -> Table:
    """Render detailed health data without crushing three columns on narrow terminals."""
    compact = screen_width < _NARROW_PAGE_BREAKPOINT
    table = Table(
        title="SYSTEM HEALTH",
        title_style=f"bold {ACCENT}",
        border_style=ACCENT_SOFT,
        expand=True,
        padding=(0, 1),
    )
    if compact:
        table.add_column("Component", min_width=12, ratio=2, style=ACCENT, overflow="fold")
        table.add_column("Status / Details", min_width=18, ratio=4, overflow="fold")
        for component, state, detail in rows:
            body = Text()
            body.append_text(state)
            body.append("\n")
            body.append(detail, style=MUTED)
            table.add_row(component, body)
    else:
        table.add_column("Component", min_width=14, ratio=2, style=ACCENT, overflow="fold")
        table.add_column("State", min_width=10, max_width=18, no_wrap=True)
        table.add_column("Details", min_width=18, ratio=4, overflow="fold")
        for component, state, detail in rows:
            table.add_row(component, state, detail)
    return table


def _command_table(rows: tuple[tuple[str, str], ...], screen_width: int) -> Table:
    """Keep command help readable on narrow terminals without horizontal crowding."""
    compact = screen_width < _NARROW_PAGE_BREAKPOINT
    table = Table(
        title="COMMAND REFERENCE",
        title_style=f"bold {ACCENT}",
        border_style=ACCENT_SOFT,
        expand=True,
        padding=(0, 1),
    )
    if compact:
        table.add_column("Command / Purpose", ratio=1, overflow="fold")
        for command, purpose in rows:
            body = Text(command, style=f"bold {ACCENT}")
            body.append("\n")
            body.append(purpose, style=MUTED)
            table.add_row(body)
    else:
        table.add_column("Command", min_width=18, ratio=4, style=ACCENT, overflow="fold")
        table.add_column("Purpose", min_width=18, ratio=3, overflow="fold")
        for command, purpose in rows:
            table.add_row(command, purpose)
    return table


def system_check() -> None:
    """Render a compact operator-facing health overview."""
    sources = tuple(source_status())
    available_native = sum(1 for item in sources if item.available)
    console.print(_health_summary(available_native, len(sources)))
    console.print()

    runtime = "Bundled Windows runtime" if getattr(sys, "frozen", False) else f"Python {sys.version.split()[0]}"
    rows: list[tuple[str, Text, str]] = [
        ("Runtime", Text("READY", style=f"bold {SUCCESS}"), runtime),
        ("Platform", Text("READY", style=SUCCESS), platform.platform()),
        ("Configuration", Text("READY", style=SUCCESS), str(config_dir())),
        ("Detection engine", Text("READY", style=f"bold {SUCCESS}"), "Local analysis"),
        ("Incident intelligence", Text("READY", style=SUCCESS), "Local explanation and correlation"),
        ("AI analyst", Text("READY", style=SUCCESS), "Local default; Ollama and remote providers optional"),
        ("Watch profiles", Text("READY", style=SUCCESS), "Security / Auth / Web / Docker / Operations"),
        ("Live file monitor", Text("READY", style=SUCCESS), "Read-only rolling analysis"),
        ("Multi-source SOC", Text("READY", style=SUCCESS), "Local cross-source correlation"),
        ("Command mode", Text("READY", style=SUCCESS), "Menu shortcuts and direct CLI commands"),
    ]
    for item in sources:
        state = Text("READY", style=SUCCESS) if item.available else Text("NOT ON THIS OS", style=MUTED)
        rows.append((item.label, state, item.detail))

    console.print(bounded(_health_table(rows, console.size.width)))
    console.print(compact_footer("Health output reports capability and source availability; it does not modify host configuration."))


def commands_reference() -> None:
    """Render a readable command reference that folds cleanly on narrow screens."""
    executable = "AegisLog.exe" if getattr(sys, "frozen", False) else "aegislog"
    console.print(_command_summary(executable))
    console.print()

    rows = (
        (executable, "Open the terminal control center"),
        (f"{executable} --help", "Show all CLI commands"),
        (f"{executable} dashboard <file>", "Analyze one log and open the investigation dashboard"),
        (f"{executable} incidents <file>", "List correlated incidents and confidence"),
        (f"{executable} explain <file> <incident-id>", "Explain one incident locally"),
        (f"{executable} ai-analyst <file> --provider local", "Ask the optional AI analyst; local is the default"),
        (f"{executable} mitre <file>", "Show evidence-supported MITRE ATT&CK context"),
        (f"{executable} native-sources", "Show native OS and container sources"),
        (f"{executable} native-analyze windows --channel Security", "Analyze Windows Security events"),
        (f"{executable} live <file> --profile security", "Follow one log with a focused watch profile"),
        (f"{executable} live-multi <file1> <file2> --profile authentication", "Correlate multiple growing logs"),
        (f"{executable} native-live windows --channel Security --profile security", "Monitor Windows Event Logs continuously"),
        (f"{executable} native-live journald --profile operations", "Monitor Linux operations signals"),
        (f"{executable} native-live docker --container <name> --profile docker", "Monitor Docker-focused signals"),
        (f"{executable} doctor", "Check the local AegisLog environment"),
    )

    console.print(bounded(_command_table(rows, console.size.width)))
    console.print(compact_footer("At the main console, the leading AegisLog.exe/aegislog token is optional."))
