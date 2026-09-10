from __future__ import annotations

from rich.console import Group, RenderableType
from rich.table import Table
from rich.text import Text

from . import __version__
from . import commands_v144 as legacy
from .theme import ACCENT, DIM, MUTED, NEUTRAL, SUCCESS

_LEGACY_INLINE_COMMAND = legacy._run_inline_command
_NARROW_BREAKPOINT = 64
_COMPACT_BRAND_BREAKPOINT = 54


def _rule(width: int) -> Text:
    return Text("-" * max(1, width - 2), style=DIM)


def _brand_lockup(compact: bool = False, *, screen_width: int | None = None) -> RenderableType:
    """README-aligned AegisLog identity with responsive, Windows-safe ASCII layouts."""
    frame_width = legacy._frame_width(screen_width)
    if compact:
        line = Text()
        line.append("<> ", style=f"bold {ACCENT}")
        line.append("AEGISLOG", style=f"bold {NEUTRAL}")
        return line

    if frame_width < _COMPACT_BRAND_BREAKPOINT:
        mark = Text(" /\\\n|-/\\-|\n \\__/", style=ACCENT)
        name = Text("A E G I S L O G", style=f"bold {NEUTRAL}")
        subtitle = Text("DEFENSIVE LOG INVESTIGATION", style=f"bold {ACCENT}")
        if frame_width >= 36:
            posture = Text("LOCAL / READ-ONLY / DETERMINISTIC", style=MUTED)
        else:
            posture = Text("LOCAL / READ-ONLY\nDETERMINISTIC", style=MUTED)
        return Group(mark, name, subtitle, posture)

    crown = Text()
    crown.append("       /\\       ", style=ACCENT)
    crown.append("A E G I S L O G", style=f"bold {NEUTRAL}")

    shoulder = Text()
    shoulder.append("      /  \\      ", style=ACCENT)
    shoulder.append("DEFENSIVE LOG INVESTIGATION", style=f"bold {ACCENT}")

    body = Text()
    body.append("     /    \\     ", style=ACCENT)
    body.append("LOCAL-FIRST  /  READ-ONLY  /  DETERMINISTIC", style=MUTED)

    pulse = Text()
    pulse.append("    |---/\\_/\\---|", style=f"bold {NEUTRAL}")

    lower = Text("     \\      /    ", style=ACCENT)
    base = Text("      \\____/     ", style=ACCENT)
    return Group(crown, shoulder, body, pulse, lower, base)


def _header(screen_width: int | None = None) -> RenderableType:
    """Startup identity that scales from narrow consoles to wide terminals."""
    frame_width = legacy._frame_width(screen_width)
    version = Text()
    version.append("VERSION ", style=DIM)
    version.append(f"v{__version__}", style=MUTED)
    status = Text()
    status.append("+ ", style=SUCCESS)
    status.append("SYSTEM READY", style=f"bold {SUCCESS}")
    return Group(
        _brand_lockup(screen_width=screen_width),
        Text(""),
        _rule(frame_width),
        version,
        status,
    )


def _operation_header(
    title: str,
    subtitle: str,
    accent: str = ACCENT,
    *,
    screen_width: int | None = None,
) -> RenderableType:
    """Prominent workspace heading with compact brand signature."""
    frame_width = legacy._frame_width(screen_width)
    heading = Text(title.upper(), style=f"bold {accent}")
    context = Text(subtitle, style=NEUTRAL, overflow="fold")
    state = Text("LOCAL / READ-ONLY", style=MUTED)
    return Group(
        _brand_lockup(compact=True, screen_width=screen_width),
        Text(""),
        heading,
        context,
        Text(""),
        _rule(frame_width),
        state,
    )


def _input_panel(
    title: str,
    lines: list[tuple[str, str]],
    accent: str = ACCENT,
    *,
    screen_width: int | None = None,
    primary_label: str | None = None,
) -> RenderableType:
    """Responsive task guidance that folds metadata instead of clipping it."""
    frame_width = legacy._frame_width(screen_width)
    padding = (0, 1) if frame_width < _NARROW_BREAKPOINT else (0, 2)
    label_width = 8 if frame_width < 44 else 10 if frame_width < 60 else 14
    grid = Table.grid(expand=True, padding=padding)
    grid.add_column(width=label_width, no_wrap=True)
    grid.add_column(ratio=1, overflow="fold")
    for label, value in lines:
        is_primary = primary_label is not None and label == primary_label
        grid.add_row(
            Text(label.upper(), style=f"bold {ACCENT}" if is_primary else MUTED, overflow="ellipsis"),
            Text(value, style=NEUTRAL if is_primary else MUTED, overflow="fold"),
        )
    return Group(Text(title.upper(), style=f"bold {NEUTRAL}"), Text(""), grid)


def _menu_row(key: str, label: str, description: str, *, compact: bool) -> RenderableType:
    row = Table.grid(expand=True, padding=(0, 1))
    row.add_column(width=4, no_wrap=True)
    if compact:
        row.add_column(ratio=1, overflow="fold")
        body = Text(label.upper(), style=f"bold {NEUTRAL}")
        body.append("\n")
        body.append(description, style=MUTED)
        row.add_row(Text(key, style=f"bold {ACCENT}"), body)
    else:
        row.add_column(width=18, no_wrap=True)
        row.add_column(ratio=1, overflow="fold")
        row.add_row(
            Text(key, style=f"bold {ACCENT}"),
            Text(label.upper(), style=f"bold {NEUTRAL}"),
            Text(description, style=MUTED, overflow="fold"),
        )
    return row


def _menu(screen_width: int | None = None) -> RenderableType:
    """Professional command index with compact fallback for narrow terminals."""
    frame_width = legacy._frame_width(screen_width)
    compact = frame_width < _NARROW_BREAKPOINT
    rows: list[RenderableType] = [
        Text("INVESTIGATION", style=f"bold {ACCENT}"),
        _menu_row("01", "Analyze", "Investigate a log and generate an evidence report", compact=compact),
        _menu_row("06", "Incidents", "Review correlated evidence chains", compact=compact),
        _menu_row("04", "Native logs", "Inspect operating-system or container telemetry", compact=compact),
        Text(""),
        Text("MONITORING", style=f"bold {ACCENT}"),
        _menu_row("02", "Live monitor", "Watch one log source continuously", compact=compact),
        _menu_row("03", "Multi-source", "Correlate activity across live sources", compact=compact),
        _menu_row("05", "Native monitor", "Watch native telemetry read-only", compact=compact),
        Text(""),
        Text("SYSTEM", style=f"bold {ACCENT}"),
        _menu_row("07", "Demo", "Run the built-in investigation dataset", compact=compact),
        _menu_row("08", "Health", "Check engine and collector readiness", compact=compact),
        _menu_row("09", "Help", "Open the command reference", compact=compact),
    ]
    return Group(*rows, _rule(frame_width))


def _footer(screen_width: int | None = None) -> Text:
    frame_width = legacy._frame_width(screen_width)
    footer = Text()
    if frame_width < 38:
        footer.append("01-09 SELECT", style=f"bold {NEUTRAL}")
        footer.append("\nC COMMAND  Q EXIT", style=MUTED)
    elif frame_width < _NARROW_BREAKPOINT:
        footer.append("01-09 SELECT", style=f"bold {NEUTRAL}")
        footer.append("  |  C COMMAND  |  Q EXIT", style=MUTED)
    else:
        footer.append("SELECT", style=f"bold {NEUTRAL}")
        footer.append("  >  ", style=f"bold {ACCENT}")
        footer.append("01-09", style=NEUTRAL)
        footer.append("     C command mode     Q exit", style=MUTED)
    return footer


def _home(screen_width: int | None = None) -> RenderableType:
    return Group(
        _header(screen_width),
        Text(""),
        _menu(screen_width),
        Text(""),
        _footer(screen_width),
    )


def _run_inline_command(raw: str) -> None:
    if raw.strip().lower() in {"a", "ai", "ai-analyst", "ask"}:
        legacy.console.print(
            "AI Analyst is not part of AegisLog. Use deterministic investigation commands instead.",
            style=MUTED,
        )
        return
    _LEGACY_INLINE_COMMAND(raw)


def start() -> None:
    """Run the branded terminal shell over the deterministic investigation engine."""
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
