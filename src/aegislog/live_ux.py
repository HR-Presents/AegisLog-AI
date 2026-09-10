from __future__ import annotations

from collections.abc import Iterable
from shutil import get_terminal_size

from rich.console import Group, RenderableType
from rich.table import Table
from rich.text import Text

from .theme import ACCENT, MUTED, NEUTRAL, SUCCESS, WARNING
from .ui import bounded


def _screen_width() -> int:
    return max(32, get_terminal_size((80, 24)).columns)


def live_startup_panel(
    *,
    title: str,
    sources: Iterable[str],
    profile: str,
    mode: str,
    window: int,
    refresh: float,
    extra: str = "",
) -> RenderableType:
    """Render a calm, width-aware live-session summary before monitoring takes over."""
    source_list = tuple(str(source) for source in sources)
    width = _screen_width()
    narrow = width < 60

    heading = Text()
    heading.append("AEGISLOG", style=f"bold {NEUTRAL}")
    heading.append(" / ", style=MUTED)
    heading.append(title.upper(), style=f"bold {ACCENT}")
    status = Text("+ LIVE", style=f"bold {SUCCESS}")
    status.append("  READ-ONLY" if narrow else "   READ-ONLY SESSION", style=MUTED)

    summary = Table.grid(expand=True, padding=(0, 1 if narrow else 2))
    summary.add_column(style=MUTED, min_width=7 if narrow else 10, max_width=12 if narrow else 16)
    summary.add_column(style=NEUTRAL, ratio=1, overflow="fold")
    summary.add_row("Profile", Text(profile, style=f"bold {ACCENT}"))
    summary.add_row("Mode", mode)
    summary.add_row("Window", f"{window:,} lines")
    summary.add_row("Refresh", f"{refresh:g}s")
    if extra:
        summary.add_row("Collector", extra)

    targets = Table(show_header=False, box=None, padding=(0, 1 if narrow else 2), expand=True)
    targets.add_column("#", justify="right", min_width=1 if narrow else 2, max_width=3 if narrow else 4, style=ACCENT)
    targets.add_column("Target", ratio=1, overflow="fold")
    for index, source in enumerate(source_list, start=1):
        targets.add_row(str(index), Text(source, style=NEUTRAL))

    guidance = Text("Live analysis is read-only. ", style=MUTED)
    guidance.append("Ctrl+C stops safely; source data and host configuration are never modified.", style=MUTED)

    rule_width = max(20, min(width - 2, 48))
    return bounded(
        Group(
            heading,
            Text("-" * rule_width, style="grey35"),
            status,
            Text(""),
            summary,
            Text("\nMONITORING TARGETS", style=f"bold {MUTED}"),
            targets,
            Text(""),
            guidance,
        )
    )


def live_initial_status(kind: str, *, prefix: str | None = None) -> Text:
    message = prefix or f"Initial {kind} scan complete."
    status = Text(f"{message} ", style=f"bold {SUCCESS}")
    status.append("Monitoring remains active and refreshes when new telemetry arrives.", style=MUTED)
    return status


def live_source_status(source: str, *, available: bool) -> Text:
    if available:
        status = Text("+ Source recovered: ", style=f"bold {SUCCESS}")
        status.append(source, style=NEUTRAL)
        status.append(". Monitoring resumed automatically from the safe cursor.", style=MUTED)
        return status
    status = Text("! Source temporarily unavailable: ", style=f"bold {WARNING}")
    status.append(source, style=NEUTRAL)
    status.append(". Retaining the current dashboard; retry read-only polling.", style=MUTED)
    return status


def live_stopped_status(kind: str, *, degraded: bool = False) -> Text:
    style = WARNING if degraded else SUCCESS
    status = Text(f"\n{kind} monitoring stopped safely. ", style=f"bold {style}")
    status.append("No host configuration or source data was modified.", style=MUTED)
    return status
