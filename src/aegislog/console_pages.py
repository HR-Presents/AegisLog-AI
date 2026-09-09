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


def system_check() -> None:
    """Render a compact operator-facing health overview."""
    sources = tuple(source_status())
    available_native = sum(1 for item in sources if item.available)
    console.print(_health_summary(available_native, len(sources)))
    console.print()

    table = Table(
        title="SYSTEM HEALTH",
        title_style=f"bold {ACCENT}",
        border_style=ACCENT_SOFT,
        expand=True,
        padding=(0, 1),
    )
    table.add_column("Component", min_width=14, ratio=2, style=ACCENT, overflow="fold")
    table.add_column("State", min_width=10, max_width=18, no_wrap=True)
    table.add_column("Details", min_width=18, ratio=4, overflow="fold")

    runtime = "Bundled Windows runtime" if getattr(sys, "frozen", False) else f"Python {sys.version.split()[0]}"
    table.add_row("Runtime", Text("READY", style=f"bold {SUCCESS}"), runtime)
    table.add_row("Platform", Text("READY", style=SUCCESS), platform.platform())
    table.add_row("Configuration", Text("READY", style=SUCCESS), str(config_dir()))
    table.add_row("Detection engine", Text("READY", style=f"bold {SUCCESS}"), "Local analysis")
    table.add_row("Incident intelligence", Text("READY", style=SUCCESS), "Local explanation and correlation")
    table.add_row("Watch profiles", Text("READY", style=SUCCESS), "Security / Auth / Web / Docker / Operations")
    table.add_row("Live file monitor", Text("READY", style=SUCCESS), "Read-only rolling analysis")
    table.add_row("Multi-source SOC", Text("READY", style=SUCCESS), "Local cross-source correlation")
    table.add_row("Command mode", Text("READY", style=SUCCESS), "Menu shortcuts and direct CLI commands")

    for item in sources:
        state = Text("READY", style=SUCCESS) if item.available else Text("NOT ON THIS OS", style=MUTED)
        table.add_row(item.label, state, item.detail)

    console.print(bounded(table))
    console.print(compact_footer("Health output reports capability and source availability; it does not modify host configuration."))


def commands_reference() -> None:
    """Render a readable command reference that folds cleanly on narrow screens."""
    executable = "AegisLog.exe" if getattr(sys, "frozen", False) else "aegislog"
    console.print(_command_summary(executable))
    console.print()

    table = Table(
        title="COMMAND REFERENCE",
        title_style=f"bold {ACCENT}",
        border_style=ACCENT_SOFT,
        expand=True,
        padding=(0, 1),
    )
    table.add_column("Command", min_width=18, ratio=4, style=ACCENT, overflow="fold")
    table.add_column("Purpose", min_width=18, ratio=3, overflow="fold")

    rows = (
        (executable, "Open the terminal control center"),
        (f"{executable} --help", "Show all CLI commands"),
        (f"{executable} dashboard <file>", "Analyze one log and open the investigation dashboard"),
        (f"{executable} incidents <file>", "List correlated incidents and confidence"),
        (f"{executable} explain <file> <incident-id>", "Explain one incident locally"),
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
    for command, purpose in rows:
        table.add_row(command, purpose)

    console.print(bounded(table))
    console.print(compact_footer("At the main console, the leading AegisLog.exe/aegislog token is optional."))
