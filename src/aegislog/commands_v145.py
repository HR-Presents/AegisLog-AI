from __future__ import annotations

from rich.console import Group, RenderableType
from rich.table import Table
from rich.text import Text

from . import __version__
from . import commands_v144 as legacy
from .theme import ACCENT, MUTED, SUCCESS

_LEGACY_INLINE_COMMAND = legacy._run_inline_command


def _rule(width: int) -> Text:
    return Text("─" * max(24, width - 2), style="grey35")


def _header(screen_width: int | None = None) -> RenderableType:
    """Quiet product header: identity first, status second, no decorative frame."""
    frame_width = legacy._frame_width(screen_width)
    title = Text()
    title.append("AEGISLOG", style="bold white")
    title.append(f"  v{__version__}", style=MUTED)

    subtitle = Text("Defensive log investigation", style=MUTED)
    status = Text()
    status.append("● ", style=SUCCESS)
    status.append("READY", style=f"bold {SUCCESS}")
    status.append("   LOCAL-FIRST", style=MUTED)
    status.append("   READ-ONLY", style=MUTED)
    status.append("   DEFENSIVE", style=MUTED)
    return Group(title, subtitle, _rule(frame_width), status)


def _menu_row(key: str, label: str, description: str) -> RenderableType:
    row = Table.grid(expand=True, padding=(0, 1))
    row.add_column(width=4, no_wrap=True)
    row.add_column(width=19, no_wrap=True)
    row.add_column(ratio=1, overflow="fold")
    row.add_row(
        Text(key, style=f"bold {ACCENT}"),
        Text(label, style="bold white"),
        Text(description, style=MUTED),
    )
    return row


def _menu(screen_width: int | None = None) -> RenderableType:
    """Minimal navigation with one clear hierarchy and no nested menu panels."""
    frame_width = legacy._frame_width(screen_width)
    rows: list[RenderableType] = [
        Text("INVESTIGATE", style="bold grey70"),
        _menu_row("01", "Analyze", "Investigate a log and generate a report"),
        _menu_row("06", "Incidents", "Review correlated evidence chains"),
        _menu_row("04", "Native logs", "Inspect operating-system or container telemetry"),
        Text(""),
        Text("MONITOR", style="bold grey70"),
        _menu_row("02", "Live monitor", "Watch one log source continuously"),
        _menu_row("03", "Multi-source", "Correlate activity across live sources"),
        _menu_row("05", "Native monitor", "Watch native telemetry read-only"),
        Text(""),
        Text("TOOLS", style="bold grey70"),
        _menu_row("07", "Demo", "Run the built-in investigation dataset"),
        _menu_row("08", "Health", "Check engine and collector readiness"),
        _menu_row("09", "Help", "Open the command reference"),
    ]
    return Group(*rows, _rule(frame_width))


def _home(screen_width: int | None = None) -> RenderableType:
    footer = Text()
    footer.append("Select an action", style=MUTED)
    footer.append("  ›  ", style=f"bold {ACCENT}")
    footer.append("01-09", style="white")
    footer.append("    C command mode    Q exit", style=MUTED)
    return Group(_header(screen_width), Text(""), _menu(screen_width), Text(""), footer)


def _run_inline_command(raw: str) -> None:
    # AI Analyst was intentionally removed from the interactive product surface.
    if raw.strip().lower() in {"a", "ai", "ai-analyst", "ask"}:
        legacy.console.print("AI Analyst is not part of AegisLog. Use deterministic investigation commands instead.", style=MUTED)
        return
    _LEGACY_INLINE_COMMAND(raw)


def start() -> None:
    """Run the minimal navigation shell over the deterministic investigation engine."""
    original_home = legacy._home
    original_inline = legacy._run_inline_command
    try:
        legacy._home = _home
        legacy._run_inline_command = _run_inline_command
        legacy.start()
    finally:
        legacy._home = original_home
        legacy._run_inline_command = original_inline


__all__ = ["start"]
