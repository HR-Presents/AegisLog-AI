from __future__ import annotations

from rich import box
from rich.align import Align
from rich.console import Group, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from . import __version__
from . import commands_v144 as legacy
from .theme import ACCENT, ACCENT_SOFT, DIM, MUTED, NEUTRAL, SUCCESS

_LEGACY_INLINE_COMMAND = legacy._run_inline_command
_NARROW_BREAKPOINT = 72
_WIDE_BREAKPOINT = 92
_MAX_HOME_WIDTH = 98


def _screen_width(screen_width: int | None = None) -> int:
    width = legacy.console.size.width if screen_width is None else screen_width
    return max(1, width - 2)


def _frame_width(screen_width: int | None = None) -> int:
    """Keep Mission Control compact enough to read as one deliberate workspace."""
    return min(_screen_width(screen_width), _MAX_HOME_WIDTH)


def _rule(width: int) -> Text:
    return Text("-" * max(16, width), style=DIM)


def _falcon(compact: bool = False) -> Text:
    """ASCII-safe, front-facing falcon/eagle head mark for Windows terminals."""
    mark = Text()
    if compact:
        mark.append("<F>", style=f"bold {ACCENT}")
        return mark

    lines = (
        "     __/\\__",
        "  __/  /\\  \\__",
        " /    /  \\    \\",
        "|  __/ /\\ \\__  |",
        "| /  \\_\\/_/  \\ |",
        " \\    /\\    /",
        "  \\__/  \\__/",
        "     \\__/",
    )
    for index, line in enumerate(lines):
        if index:
            mark.append("\n")
        mark.append(line, style=f"bold {ACCENT}")
    return mark


def _brand_lockup(compact: bool = False, *, screen_width: int | None = None) -> RenderableType:
    """Render one compact Falcon identity block with integrated readiness state."""
    width = _frame_width(screen_width)
    if compact or width < _NARROW_BREAKPOINT:
        brand = Text()
        brand.append("<F>  AEGISLOG", style=f"bold {ACCENT}")
        brand.append(f"   v{__version__}", style=MUTED)
        brand.append("   [ READY ]\n", style=f"bold {SUCCESS}")
        brand.append("DEFENSIVE LOG INVESTIGATION\n", style=f"bold {NEUTRAL}")
        brand.append("LOCAL-FIRST  |  READ-ONLY  |  DETERMINISTIC", style=MUTED)
        return brand

    left_width = 20
    details = Table.grid(padding=(0, 2))
    details.add_column(width=left_width)
    details.add_column(ratio=1)
    details.add_row(_falcon(), _brand_text())
    return details


def _brand_text() -> RenderableType:
    name = Text("A E G I S L O G", style=f"bold {NEUTRAL}")
    status = Text()
    status.append(f"VERSION v{__version__}", style=MUTED)
    status.append("    ")
    status.append("[ SYSTEM READY ]", style=f"bold {SUCCESS}")
    subtitle = Text("DEFENSIVE LOG INVESTIGATION", style=f"bold {ACCENT}")
    posture = Text("LOCAL-FIRST  |  READ-ONLY  |  DETERMINISTIC", style=MUTED)
    return Group(name, status, Text(""), subtitle, posture)


def _header(screen_width: int | None = None) -> RenderableType:
    width = _frame_width(screen_width)
    return Panel(
        _brand_lockup(screen_width=screen_width),
        box=box.ASCII,
        border_style=ACCENT_SOFT,
        padding=(0, 1),
        width=width,
    )


def _operation_header(
    title: str,
    subtitle: str,
    accent: str = ACCENT,
    *,
    screen_width: int | None = None,
) -> RenderableType:
    width = _frame_width(screen_width)
    heading = Text()
    heading.append("<F> AEGISLOG", style=f"bold {NEUTRAL}")
    heading.append("  //  ", style=MUTED)
    heading.append(title.upper(), style=f"bold {accent}")
    context = Text(subtitle, style=NEUTRAL, overflow="fold")
    posture = Text("LOCAL / READ-ONLY / DETERMINISTIC", style=MUTED)
    return Panel(
        Group(heading, context, posture),
        title=Text(" ACTIVE WORKSPACE ", style=f"bold {accent}"),
        title_align="left",
        box=box.ASCII,
        border_style=ACCENT_SOFT,
        padding=(0, 1),
        width=width,
    )


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
    grid = Table.grid(expand=True, padding=(0, 1))
    grid.add_column(width=12 if compact else 16, no_wrap=True)
    grid.add_column(ratio=1, overflow="fold")
    for label, value in lines:
        primary = primary_label is not None and label == primary_label
        grid.add_row(
            Text(label.upper(), style=f"bold {accent}" if primary else MUTED),
            Text(value, style=NEUTRAL if primary else MUTED, overflow="fold"),
        )
    return Panel(
        grid,
        title=Text(f" {title.upper()} ", style=f"bold {accent}"),
        title_align="left",
        box=box.ASCII,
        border_style=ACCENT_SOFT,
        padding=(0, 1),
        width=width,
    )


def _menu_item(key: str, label: str, description: str) -> Text:
    item = Text()
    item.append(f"[{key}] ", style=f"bold {ACCENT}")
    item.append(label, style=f"bold {NEUTRAL}")
    item.append("\n     ")
    item.append(description, style=MUTED)
    return item


def _menu_panel(title: str, rows: list[tuple[str, str, str]], width: int) -> Panel:
    body: list[RenderableType] = []
    for index, row in enumerate(rows):
        if index:
            body.append(Text(""))
        body.append(_menu_item(*row))
    return Panel(
        Group(*body),
        title=Text(f" {title} ", style=f"bold {ACCENT}"),
        title_align="left",
        box=box.ASCII,
        border_style=ACCENT_SOFT,
        padding=(0, 1),
        width=width,
    )


def _compact_menu(rows: list[tuple[str, str, str]]) -> RenderableType:
    body: list[RenderableType] = []
    for index, row in enumerate(rows):
        if index:
            body.append(Text(""))
        body.append(_menu_item(*row))
    return Panel(
        Group(*body),
        box=box.ASCII,
        border_style=ACCENT_SOFT,
        padding=(0, 1),
    )


def _system_panel(system: list[tuple[str, str, str]], width: int) -> Panel:
    grid = Table.grid(expand=True, padding=(0, 1))
    for _ in system:
        grid.add_column(ratio=1)
    cells: list[Text] = []
    for key, label, description in system:
        cell = Text()
        cell.append(f"[{key}] ", style=f"bold {ACCENT}")
        cell.append(label, style=f"bold {NEUTRAL}")
        cell.append("  ")
        cell.append(description, style=MUTED)
        cells.append(cell)
    grid.add_row(*cells)
    return Panel(
        grid,
        title=Text(" SYSTEM ", style=f"bold {ACCENT}"),
        title_align="left",
        box=box.ASCII,
        border_style=ACCENT_SOFT,
        padding=(0, 1),
        width=width,
    )


def _menu(screen_width: int | None = None) -> RenderableType:
    """Render Mission Control as one compact, centered operator workspace."""
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
        ("07", "DEMO", "Built-in dataset"),
        ("08", "HEALTH", "Engine readiness"),
        ("09", "HELP", "Command reference"),
    ]

    title = Text("MISSION CONTROL", style=f"bold {ACCENT}")
    hierarchy = Text("INVESTIGATION  /  MONITORING  /  SYSTEM", style=MUTED)
    if width < _NARROW_BREAKPOINT:
        return Group(title, hierarchy, Text(""), _compact_menu(investigation + monitoring + system))

    if width >= _WIDE_BREAKPOINT:
        gap = 2
        column_width = (width - gap) // 2
        top = Table.grid(padding=0)
        top.add_column(width=column_width)
        top.add_column(width=gap)
        top.add_column(width=column_width)
        top.add_row(
            _menu_panel("INVESTIGATE", investigation, column_width),
            Text(""),
            _menu_panel("MONITOR", monitoring, column_width),
        )
        return Group(title, hierarchy, Text(""), top, _system_panel(system, width))

    return Group(title, hierarchy, Text(""), _compact_menu(investigation + monitoring + system))


def _footer(screen_width: int | None = None) -> Text:
    width = _frame_width(screen_width)
    footer = Text()
    footer.append("01-09 Select", style=f"bold {ACCENT}")
    footer.append("   |   C Command Mode", style=MUTED)
    footer.append("   |   Q Exit", style=MUTED)
    if width >= 92:
        footer.append("   |   Ctrl+C stops live views", style=MUTED)
    return footer


def _home(screen_width: int | None = None) -> RenderableType:
    frame_width = _frame_width(screen_width)
    available = _screen_width(screen_width)
    content = Group(
        _header(screen_width),
        Text(""),
        _menu(screen_width),
        Text(""),
        _rule(frame_width),
        _footer(screen_width),
    )
    return Align.center(content, width=available, pad=False)


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
