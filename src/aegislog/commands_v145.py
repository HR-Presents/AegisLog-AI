from __future__ import annotations

from rich import box
from rich.align import Align
from rich.console import Group, RenderableType
from rich.table import Table
from rich.text import Text

from . import __version__
from . import commands_v144 as legacy
from .theme import ACCENT, DIM, MUTED, NEUTRAL, SUCCESS

_LEGACY_INLINE_COMMAND = legacy._run_inline_command
_NARROW_BREAKPOINT = 72
_WIDE_BREAKPOINT = 104
_MAX_HOME_WIDTH = 112


def _screen_width(screen_width: int | None = None) -> int:
    width = legacy.console.size.width if screen_width is None else screen_width
    return max(1, width - 2)


def _frame_width(screen_width: int | None = None) -> int:
    """Keep Mission Control deliberately compact on very wide Windows terminals."""
    return min(_screen_width(screen_width), _MAX_HOME_WIDTH)


def _rule(width: int) -> Text:
    return Text("-" * max(16, width), style=DIM)


def _brand_lockup(compact: bool = False, *, screen_width: int | None = None) -> RenderableType:
    """Render a compact identity with status anchored to the same visual frame."""
    width = _frame_width(screen_width)
    if compact or width < _NARROW_BREAKPOINT:
        brand = Text()
        brand.append("/\\  AEGISLOG", style=f"bold {ACCENT}")
        brand.append(f"   v{__version__}\n", style=MUTED)
        brand.append("DEFENSIVE LOG INVESTIGATION\n", style=f"bold {NEUTRAL}")
        brand.append("LOCAL-FIRST  /  READ-ONLY  /  DETERMINISTIC", style=MUTED)
        brand.append("   + READY", style=f"bold {SUCCESS}")
        return brand

    grid = Table.grid(width=width, padding=(0, 1))
    grid.add_column(width=8, no_wrap=True)
    grid.add_column(ratio=1)
    grid.add_column(width=18, justify="right", no_wrap=True)

    mark = Text("  /\\\n /  \\\n/____\\", style=f"bold {ACCENT}")
    identity = Text()
    identity.append("A E G I S L O G\n", style=f"bold {NEUTRAL}")
    identity.append("DEFENSIVE LOG INVESTIGATION\n", style=f"bold {ACCENT}")
    identity.append("LOCAL-FIRST  /  READ-ONLY  /  DETERMINISTIC", style=MUTED)
    status = Text()
    status.append(f"v{__version__}\n", style=MUTED)
    status.append("+ READY", style=f"bold {SUCCESS}")
    grid.add_row(mark, identity, status)
    return grid


def _header(screen_width: int | None = None) -> RenderableType:
    width = _frame_width(screen_width)
    return Group(_brand_lockup(screen_width=screen_width), _rule(width))


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
        width=width,
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


def _menu_item(key: str, label: str, description: str) -> Text:
    item = Text()
    item.append(f"[{key}] ", style=f"bold {ACCENT}")
    item.append(label, style=f"bold {NEUTRAL}")
    item.append("\n     ")
    item.append(description, style=MUTED)
    return item


def _menu_column(title: str, rows: list[tuple[str, str, str]], width: int) -> RenderableType:
    heading = Text(title, style=f"bold {ACCENT}")
    rule = Text("-" * max(18, width - 1), style=DIM)
    body: list[RenderableType] = [heading, rule]
    for index, (key, label, description) in enumerate(rows):
        if index:
            body.append(Text(""))
        body.append(_menu_item(key, label, description))
    return Group(*body)


def _compact_menu(rows: list[tuple[str, str, str]]) -> RenderableType:
    body: list[RenderableType] = []
    for index, row in enumerate(rows):
        if index:
            body.append(Text(""))
        body.append(_menu_item(*row))
    return Group(*body)


def _menu(screen_width: int | None = None) -> RenderableType:
    """Render Mission Control as an operator dashboard, not a spreadsheet."""
    width = _frame_width(screen_width)
    investigation = [
        ("01", "ANALYZE LOG", "Analyze evidence and generate a report"),
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

    title = Text("MISSION CONTROL", style=f"bold {ACCENT}")
    if width < _NARROW_BREAKPOINT:
        return Group(
            title,
            Text("INVESTIGATE / MONITOR / SYSTEM", style=MUTED),
            Text(""),
            _compact_menu(investigation + monitoring + system),
        )

    if width >= _WIDE_BREAKPOINT:
        gap = 5
        column_width = max(36, (width - gap) // 2)
        top = Table.grid(width=width, padding=(0, gap // 2))
        top.add_column(width=column_width)
        top.add_column(width=column_width)
        top.add_row(
            _menu_column("INVESTIGATE", investigation, column_width),
            _menu_column("MONITOR", monitoring, column_width),
        )
        system_line = Text()
        system_line.append("SYSTEM", style=f"bold {ACCENT}")
        system_line.append("   ")
        for index, (key, label, _description) in enumerate(system):
            if index:
                system_line.append("      ")
            system_line.append(f"[{key}] ", style=f"bold {ACCENT}")
            system_line.append(label, style=f"bold {NEUTRAL}")
        return Group(title, Text(""), top, Text(""), system_line)

    return Group(
        title,
        Text("INVESTIGATE / MONITOR / SYSTEM", style=MUTED),
        Text(""),
        _compact_menu(investigation + monitoring + system),
    )


def _footer(screen_width: int | None = None) -> Text:
    width = _frame_width(screen_width)
    footer = Text()
    footer.append("01-09 Select", style=f"bold {ACCENT}")
    footer.append("   |   C Command Mode", style=MUTED)
    footer.append("   |   Q Exit", style=MUTED)
    if width >= 96:
        footer.append("   |   Ctrl+C stops live views", style=MUTED)
    return footer


def _home(screen_width: int | None = None) -> RenderableType:
    width = _frame_width(screen_width)
    content = Group(
        _header(screen_width),
        Text(""),
        _menu(screen_width),
        Text(""),
        _rule(width),
        _footer(screen_width),
    )
    # A bounded frame makes very wide Windows Terminal windows look intentional.
    # Keep it left-aligned with the interactive prompt rather than floating the UI.
    return Align.left(content, width=width)


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
