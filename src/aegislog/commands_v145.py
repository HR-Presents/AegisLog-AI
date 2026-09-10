from __future__ import annotations

from rich import box
from rich.console import Group, RenderableType
from rich.table import Table
from rich.text import Text

from . import __version__
from . import commands_v144 as legacy
from .theme import ACCENT, DIM, MUTED, NEUTRAL, SUCCESS

_LEGACY_INLINE_COMMAND = legacy._run_inline_command
_NARROW_BREAKPOINT = 72
_WIDE_BREAKPOINT = 112


def _frame_width(screen_width: int | None = None) -> int:
    return legacy._frame_width(screen_width)


def _rule(width: int) -> Text:
    return Text("-" * max(16, width), style=DIM)


def _brand_lockup(compact: bool = False, *, screen_width: int | None = None) -> RenderableType:
    """A compact, Windows-safe product identity that scales with the viewport."""
    width = _frame_width(screen_width)
    if compact:
        line = Text()
        line.append("/\\ ", style=f"bold {ACCENT}")
        line.append("AEGISLOG", style=f"bold {NEUTRAL}")
        return line

    if width < _NARROW_BREAKPOINT:
        brand = Text()
        brand.append("/\\  AEGISLOG\n", style=f"bold {ACCENT}")
        brand.append("DEFENSIVE LOG INVESTIGATION\n", style=f"bold {NEUTRAL}")
        brand.append("LOCAL-FIRST / READ-ONLY / DETERMINISTIC", style=MUTED)
        return brand

    grid = Table.grid(expand=True, padding=(0, 2))
    grid.add_column(width=16, no_wrap=True)
    grid.add_column(ratio=1)
    grid.add_column(width=24, justify="right", no_wrap=True)

    mark = Text("    /\\\n   /  \\\n  |---/\\_/\\---|\n    \\____/", style=f"bold {ACCENT}")
    identity = Text()
    identity.append("A E G I S L O G\n", style=f"bold {NEUTRAL}")
    identity.append("DEFENSIVE LOG INVESTIGATION\n", style=f"bold {ACCENT}")
    identity.append("LOCAL-FIRST  /  READ-ONLY  /  DETERMINISTIC", style=MUTED)
    status = Text()
    status.append(f"VERSION v{__version__}\n", style=MUTED)
    status.append("+ SYSTEM READY", style=f"bold {SUCCESS}")
    grid.add_row(mark, identity, status)
    return grid


def _header(screen_width: int | None = None) -> RenderableType:
    width = _frame_width(screen_width)
    return Group(_brand_lockup(screen_width=screen_width), Text(""), _rule(width))


def _operation_header(
    title: str,
    subtitle: str,
    accent: str = ACCENT,
    *,
    screen_width: int | None = None,
) -> RenderableType:
    width = _frame_width(screen_width)
    heading = Text()
    heading.append("/\\ AEGISLOG", style=f"bold {NEUTRAL}")
    heading.append("  //  ", style=MUTED)
    heading.append(title.upper(), style=f"bold {accent}")
    context = Text(subtitle, style=NEUTRAL, overflow="fold")
    posture = Text("LOCAL / READ-ONLY  /  DETERMINISTIC", style=MUTED)
    return Group(heading, context, _rule(width), posture)


def _input_panel(
    title: str,
    lines: list[tuple[str, str]],
    accent: str = ACCENT,
    *,
    screen_width: int | None = None,
    primary_label: str | None = None,
) -> RenderableType:
    width = _frame_width(screen_width)
    compact = width < _NARROW_BREAKPOINT
    grid = Table(
        box=box.ASCII,
        expand=True,
        padding=(0, 1),
        border_style=DIM,
        show_header=True,
        header_style=f"bold {accent}",
    )
    grid.add_column(title.upper(), width=12 if compact else 16, no_wrap=True)
    grid.add_column("DETAIL", ratio=1, overflow="fold")
    for label, value in lines:
        primary = primary_label is not None and label == primary_label
        grid.add_row(
            Text(label.upper(), style=f"bold {accent}" if primary else MUTED),
            Text(value, style=NEUTRAL if primary else MUTED, overflow="fold"),
        )
    return grid


def _menu_table(rows: list[tuple[str, str, str]], heading: str) -> Table:
    table = Table(
        box=box.ASCII,
        expand=True,
        padding=(0, 1),
        border_style=DIM,
        show_header=True,
        header_style=f"bold {ACCENT}",
    )
    table.add_column(heading, width=5, justify="center", no_wrap=True)
    table.add_column("ACTION", width=18, no_wrap=True)
    table.add_column("PURPOSE", ratio=1, overflow="fold")
    for key, label, description in rows:
        table.add_row(
            Text(key, style=f"bold {ACCENT}"),
            Text(label, style=f"bold {NEUTRAL}"),
            Text(description, style=MUTED),
        )
    return table


def _compact_menu(rows: list[tuple[str, str, str]]) -> Table:
    table = Table(box=box.ASCII, expand=True, padding=(0, 1), border_style=DIM, show_header=False)
    table.add_column(width=4, no_wrap=True)
    table.add_column(ratio=1, overflow="fold")
    for key, label, description in rows:
        body = Text(label, style=f"bold {NEUTRAL}")
        body.append("\n")
        body.append(description, style=MUTED)
        table.add_row(Text(key, style=f"bold {ACCENT}"), body)
    return table


def _menu(screen_width: int | None = None) -> RenderableType:
    """Use the full viewport: two balanced work areas on wide terminals, one on narrow."""
    width = _frame_width(screen_width)
    investigation = [
        ("01", "ANALYZE", "Analyze a log and generate an evidence report"),
        ("06", "INCIDENTS", "Review correlated evidence chains"),
        ("04", "NATIVE LOGS", "Inspect OS or container telemetry"),
    ]
    monitoring = [
        ("02", "LIVE MONITOR", "Watch one log source continuously"),
        ("03", "MULTI-SOURCE", "Correlate activity across live sources"),
        ("05", "NATIVE MONITOR", "Watch native telemetry read-only"),
    ]
    system = [
        ("07", "DEMO", "Run the built-in investigation dataset"),
        ("08", "HEALTH", "Check engine and collector readiness"),
        ("09", "HELP", "Open the command reference"),
    ]

    if width < _NARROW_BREAKPOINT:
        return Group(
            Text("MISSION CONTROL", style=f"bold {ACCENT}"),
            Text("INVESTIGATION / MONITORING / SYSTEM", style=MUTED),
            _compact_menu(investigation + monitoring + system),
        )

    if width >= _WIDE_BREAKPOINT:
        top = Table.grid(expand=True, padding=(0, 1))
        top.add_column(ratio=1)
        top.add_column(ratio=1)
        top.add_row(_menu_table(investigation, "INV"), _menu_table(monitoring, "MON"))
        return Group(
            Text("MISSION CONTROL", style=f"bold {ACCENT}"),
            Text("INVESTIGATION                         MONITORING", style=MUTED),
            Text(""),
            top,
            Text(""),
            Text("SYSTEM", style=MUTED),
            _menu_table(system, "SYS"),
        )

    return Group(
        Text("MISSION CONTROL", style=f"bold {ACCENT}"),
        Text("INVESTIGATION / MONITORING / SYSTEM", style=MUTED),
        Text(""),
        _menu_table(investigation + monitoring + system, "KEY"),
    )


def _footer(screen_width: int | None = None) -> Text:
    width = _frame_width(screen_width)
    footer = Text()
    footer.append("01-09 select", style=f"bold {ACCENT}")
    footer.append("    Q quit", style=MUTED)
    if width >= 44:
        footer.append("    C command mode", style=MUTED)
    if width >= 86:
        footer.append("    CTRL+C STOPS LIVE VIEWS", style=MUTED)
    return footer


def _home(screen_width: int | None = None) -> RenderableType:
    width = _frame_width(screen_width)
    return Group(
        _header(screen_width),
        Text(""),
        _menu(screen_width),
        Text(""),
        _rule(width),
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
    """Run the responsive terminal shell over the deterministic investigation engine."""
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
