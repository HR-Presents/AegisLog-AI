from __future__ import annotations

from rich import box
from rich.align import Align
from rich.console import Group, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from . import commands_v144 as legacy
from .theme import ACCENT, ACCENT_SOFT, DIM, MUTED, NEUTRAL, SUCCESS

_LEGACY_INLINE_COMMAND = legacy._run_inline_command
_NARROW_BREAKPOINT = 72
_WIDE_BREAKPOINT = 96
_MAX_HOME_WIDTH = 112


def _screen_width(screen_width: int | None = None) -> int:
    width = legacy.console.size.width if screen_width is None else screen_width
    return max(1, width - 2)


def _frame_width(screen_width: int | None = None) -> int:
    return min(_screen_width(screen_width), _MAX_HOME_WIDTH)


def _rule(width: int) -> Text:
    return Text("-" * max(16, width), style=DIM)


def _wordmark(compact: bool = False) -> Text:
    mark = Text(justify="center")
    if compact:
        mark.append("AEGISLOG", style=f"bold {ACCENT}")
        return mark
    lines = (
        r"    _    _____ ____ ___ ____  _     ___   ____ ",
        r"   / \  | ____/ ___|_ _/ ___|| |   / _ \ / ___|",
        r"  / _ \ |  _|| |  _ | |\___ \| |  | | | | |  _ ",
        r" / ___ \| |__| |_| || | ___) | |__| |_| | |_| |",
        r"/_/   \_\_____\____|___|____/|_____\___/ \____|",
    )
    for index, line in enumerate(lines):
        if index:
            mark.append("\n")
        mark.append(line, style=f"bold {ACCENT}")
    return mark


def _brand_lockup(compact: bool = False, *, screen_width: int | None = None) -> RenderableType:
    width = _frame_width(screen_width)
    if compact or width < _NARROW_BREAKPOINT:
        body = Text(justify="center")
        body.append("AEGISLOG\n", style=f"bold {ACCENT}")
        body.append("DEFENSIVE LOG INVESTIGATION\n", style=f"bold {NEUTRAL}")
        body.append("MADE BY HR-PRESENTS\n", style=f"bold {ACCENT}")
        body.append("LOCAL-FIRST  |  READ-ONLY  |  DETERMINISTIC", style=MUTED)
        return body
    return Group(
        Align.center(_wordmark()),
        Align.center(Text("DEFENSIVE LOG INVESTIGATION", style=f"bold {NEUTRAL}")),
        Align.center(Text("MADE BY HR-PRESENTS", style=f"bold {ACCENT}")),
        Align.center(Text("LOCAL-FIRST  |  READ-ONLY  |  DETERMINISTIC", style=MUTED)),
    )


def _header(screen_width: int | None = None) -> RenderableType:
    return Panel(
        _brand_lockup(screen_width=screen_width),
        box=box.ASCII,
        border_style=ACCENT_SOFT,
        padding=(1, 1),
        width=_frame_width(screen_width),
    )


def _operation_header(title: str, subtitle: str, accent: str = ACCENT, *, screen_width: int | None = None) -> RenderableType:
    width = _frame_width(screen_width)
    heading = Text()
    heading.append("AEGISLOG", style=f"bold {NEUTRAL}")
    heading.append("  //  ", style=MUTED)
    heading.append(title.upper(), style=f"bold {accent}")
    return Panel(
        Group(
            heading,
            Text(subtitle, style=NEUTRAL, overflow="fold"),
            Text("LOCAL / READ-ONLY / DETERMINISTIC", style=MUTED),
            Text("MADE BY HR-PRESENTS", style=f"bold {ACCENT}"),
        ),
        title=Text(" ACTIVE WORKSPACE ", style=f"bold {accent}"),
        title_align="left",
        box=box.ASCII,
        border_style=ACCENT_SOFT,
        padding=(0, 1),
        width=width,
    )


def _input_panel(title: str, lines: list[tuple[str, str]], accent: str = ACCENT, *, screen_width: int | None = None, primary_label: str | None = None) -> RenderableType:
    width = _frame_width(screen_width)
    compact = width < _NARROW_BREAKPOINT
    grid = Table.grid(expand=True, padding=(0, 1))
    grid.add_column(width=12 if compact else 16, no_wrap=True)
    grid.add_column(ratio=1, overflow="fold")
    for label, value in lines:
        primary = primary_label is not None and label == primary_label
        grid.add_row(Text(label.upper(), style=f"bold {accent}" if primary else MUTED), Text(value, style=NEUTRAL if primary else MUTED, overflow="fold"))
    return Panel(grid, title=Text(f" {title.upper()} ", style=f"bold {accent}"), title_align="left", box=box.ASCII, border_style=ACCENT_SOFT, padding=(0, 1), width=width)


def _action_line(key: str, label: str, description: str, *, primary: bool = False) -> Text:
    line = Text(no_wrap=True, overflow="crop")
    line.append(f"[{key}] ", style=f"bold {ACCENT}")
    line.append(f"{label:<16}", style=f"bold {NEUTRAL}")
    line.append(description, style=NEUTRAL if primary else MUTED)
    return line


def _primary_panel(width: int) -> Panel:
    body = Group(
        _action_line("01", "ANALYZE LOG", "Investigate a log file and create a report", primary=True),
        Text("     Deterministic findings, incidents and evidence", style=MUTED, no_wrap=True, overflow="crop"),
    )
    return Panel(body, title=Text(" INVESTIGATE ", style=f"bold {ACCENT}"), title_align="left", box=box.ASCII, border_style=ACCENT, padding=(1, 1), width=width)


def _tools_panel(width: int) -> Panel:
    rows = (
        ("02", "LIVE MONITOR", "Watch one log source"),
        ("03", "MULTI-SOURCE", "Correlate live sources"),
        ("04", "NATIVE LOGS", "Inspect native telemetry"),
        ("05", "NATIVE MONITOR", "Watch native telemetry"),
        ("06", "INCIDENTS", "Review evidence chains"),
    )
    return Panel(Group(*[_action_line(*row) for row in rows]), title=Text(" MONITOR & INVESTIGATE ", style=f"bold {ACCENT}"), title_align="left", box=box.ASCII, border_style=ACCENT_SOFT, padding=(1, 1), width=width)


def _utility_panel(width: int) -> Panel:
    rows = (("07", "DEMO", "Quick start dataset"), ("08", "HEALTH", "Engine diagnostics"), ("09", "HELP", "Command reference"))
    return Panel(Group(*[_action_line(*row) for row in rows]), title=Text(" UTILITIES ", style=f"bold {ACCENT}"), title_align="left", box=box.ASCII, border_style=ACCENT_SOFT, padding=(1, 1), width=width)


def _status_panel(width: int) -> Panel:
    grid = Table.grid(expand=True, padding=(0, 1))
    grid.add_column(width=9, no_wrap=True)
    grid.add_column(ratio=1, overflow="crop", no_wrap=True)
    grid.add_row(Text("STATUS", style=MUTED), Text("SYSTEM READY", style=f"bold {SUCCESS}"))
    grid.add_row(Text("MODE", style=MUTED), Text("LOCAL", style=NEUTRAL))
    grid.add_row(Text("DATA", style=MUTED), Text("READ-ONLY", style=NEUTRAL))
    grid.add_row(Text("ENGINE", style=MUTED), Text("DETERMINISTIC", style=NEUTRAL))
    return Panel(grid, title=Text(" SYSTEM ", style=f"bold {ACCENT}"), title_align="left", box=box.ASCII, border_style=ACCENT_SOFT, padding=(1, 1), width=width)


def _quick_info_panel(width: int) -> Panel:
    grid = Table.grid(expand=True, padding=(0, 1))
    grid.add_column(width=9, no_wrap=True)
    grid.add_column(ratio=1, no_wrap=True, overflow="crop")
    for label, value in (("REPORTS", "./reports/"), ("CONFIG", "./config/"), ("PROJECT", "HR-Presents/AegisLog-AI"), ("OWNER", "HR-PRESENTS")):
        grid.add_row(Text(label, style=MUTED), Text(value, style=ACCENT if label != "OWNER" else NEUTRAL, no_wrap=True, overflow="crop"))
    return Panel(grid, title=Text(" QUICK INFO ", style=f"bold {ACCENT}"), title_align="left", box=box.ASCII, border_style=ACCENT_SOFT, padding=(1, 1), width=width)


def _menu(screen_width: int | None = None) -> RenderableType:
    width = _frame_width(screen_width)
    if width < _NARROW_BREAKPOINT:
        rows = [
            ("01", "ANALYZE LOG", "Investigate a log"), ("02", "LIVE MONITOR", "Watch a source"),
            ("03", "MULTI-SOURCE", "Correlate sources"), ("04", "NATIVE LOGS", "Inspect telemetry"),
            ("05", "NATIVE MONITOR", "Watch telemetry"), ("06", "INCIDENTS", "Review evidence"),
            ("07", "DEMO", "Quick start"), ("08", "HEALTH", "Diagnostics"), ("09", "HELP", "Reference"),
        ]
        return Group(_status_panel(width), Text(""), Panel(Group(*[_action_line(*row) for row in rows]), title=Text(" COMMAND CENTER ", style=f"bold {ACCENT}"), title_align="left", box=box.ASCII, border_style=ACCENT_SOFT, padding=(1, 1), width=width))

    if width >= _WIDE_BREAKPOINT:
        gap = 2
        left_width = 70 if width >= 108 else 64
        right_width = width - gap - left_width
        left = Group(_primary_panel(left_width), Text(""), _tools_panel(left_width), Text(""), _utility_panel(left_width))
        right = Group(_status_panel(right_width), Text(""), _quick_info_panel(right_width))
        layout = Table.grid(padding=0)
        layout.add_column(width=left_width)
        layout.add_column(width=gap)
        layout.add_column(width=right_width)
        layout.add_row(left, Text(""), right)
        return layout

    return Group(_primary_panel(width), Text(""), _tools_panel(width), Text(""), _utility_panel(width), Text(""), _status_panel(width))


def _footer(screen_width: int | None = None) -> Text:
    width = _frame_width(screen_width)
    footer = Text(overflow="crop", no_wrap=True)
    footer.append("[01-09] Select", style=f"bold {ACCENT}")
    footer.append("   |   type a command", style=NEUTRAL)
    footer.append("   |   Q Exit", style=MUTED)
    if width >= 100:
        footer.append("   |   Ctrl+C stops live views", style=MUTED)
    return footer


def _home(screen_width: int | None = None) -> RenderableType:
    frame_width = _frame_width(screen_width)
    available = _screen_width(screen_width)
    content = Group(_header(screen_width), Text(""), _menu(screen_width), Text(""), _rule(frame_width), _footer(screen_width))
    return Align.center(content, width=available, pad=False)


def _run_inline_command(raw: str) -> None:
    if raw.strip().lower() in {"a", "ai", "ai-analyst", "ask"}:
        legacy.console.print("AI Analyst is not part of AegisLog. Use deterministic investigation commands instead.", style=MUTED)
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
