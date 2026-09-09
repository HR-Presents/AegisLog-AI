from __future__ import annotations

from rich.console import Group, RenderableType
from rich.table import Table
from rich.text import Text

from . import __version__
from . import commands_v144 as legacy
from .theme import ACCENT, MUTED, NEUTRAL, SUCCESS, WARNING

_LEGACY_INLINE_COMMAND = legacy._run_inline_command


def _rule(width: int) -> Text:
    return Text("─" * max(24, width - 2), style="grey35")


def _header(screen_width: int | None = None) -> RenderableType:
    """Quiet product header: identity first, status second, no decorative frame."""
    frame_width = legacy._frame_width(screen_width)
    title = Text()
    title.append("AEGISLOG", style=f"bold {NEUTRAL}")
    title.append(f"  v{__version__}", style=MUTED)

    subtitle = Text("Defensive log investigation", style=MUTED)
    status = Text()
    status.append("● ", style=SUCCESS)
    status.append("READY", style=f"bold {SUCCESS}")
    status.append("   LOCAL-FIRST", style=MUTED)
    status.append("   READ-ONLY", style=MUTED)
    status.append("   DEFENSIVE", style=MUTED)
    return Group(title, subtitle, _rule(frame_width), status)


def _operation_header(
    title: str,
    subtitle: str,
    accent: str = ACCENT,
    *,
    screen_width: int | None = None,
) -> RenderableType:
    """Flat workspace title with hierarchy created by type and spacing, not boxes."""
    frame_width = legacy._frame_width(screen_width)
    heading = Text()
    heading.append("AEGISLOG", style=f"bold {NEUTRAL}")
    heading.append(" / ", style=MUTED)
    heading.append(title.upper(), style=f"bold {accent}")
    return Group(
        heading,
        Text(subtitle, style=MUTED),
        _rule(frame_width),
        Text("LOCAL  •  READ-ONLY", style=MUTED),
    )


def _input_panel(
    title: str,
    lines: list[tuple[str, str]],
    accent: str = ACCENT,
    *,
    screen_width: int | None = None,
    primary_label: str | None = None,
) -> RenderableType:
    """Aligned workspace guidance without nested border chrome."""
    grid = Table.grid(expand=True, padding=(0, 2))
    grid.add_column(width=14, no_wrap=True)
    grid.add_column(ratio=1, overflow="fold")
    for label, value in lines:
        is_primary = primary_label is not None and label == primary_label
        grid.add_row(
            Text(label, style=f"bold {accent}" if is_primary else MUTED),
            Text(value, style=NEUTRAL if is_primary else MUTED),
        )
    return Group(Text(title.upper(), style=f"bold {accent}"), Text(""), grid)


def _menu_row(key: str, label: str, description: str) -> RenderableType:
    row = Table.grid(expand=True, padding=(0, 1))
    row.add_column(width=4, no_wrap=True)
    row.add_column(width=19, no_wrap=True)
    row.add_column(ratio=1, overflow="fold")
    row.add_row(
        Text(key, style=f"bold {ACCENT}"),
        Text(label, style=f"bold {NEUTRAL}"),
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
    footer.append("01-09", style=NEUTRAL)
    footer.append("    C command mode    Q exit", style=MUTED)
    return Group(_header(screen_width), Text(""), _menu(screen_width), Text(""), footer)


def _run_inline_command(raw: str) -> None:
    # AI Analyst is intentionally absent from the product surface.
    if raw.strip().lower() in {"a", "ai", "ai-analyst", "ask"}:
        legacy.console.print(
            "AI Analyst is not part of AegisLog. Use deterministic investigation commands instead.",
            style=MUTED,
        )
        return
    _LEGACY_INLINE_COMMAND(raw)


def start() -> None:
    """Run the minimal terminal shell over the deterministic investigation engine."""
    original_home = legacy._home
    original_inline = legacy._run_inline_command
    original_input_panel = legacy._input_panel
    original_operation_header = legacy._operation_header
    try:
        legacy._home = _home
        legacy._run_inline_command = _run_inline_command
        legacy._input_panel = _input_panel
        legacy._operation_header = _operation_header
        legacy.start()
    finally:
        legacy._home = original_home
        legacy._run_inline_command = original_inline
        legacy._input_panel = original_input_panel
        legacy._operation_header = original_operation_header


__all__ = ["start"]
