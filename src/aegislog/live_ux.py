from __future__ import annotations

from collections.abc import Iterable

from rich.console import Group, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .theme import ACCENT, ACCENT_SOFT, MUTED, SUCCESS, WARNING
from .ui import bounded


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
    """Render one compact operator card before a live monitor takes over the terminal."""
    source_list = tuple(str(source) for source in sources)

    heading = Text()
    heading.append("AEGISLOG", style=f"bold {ACCENT}")
    heading.append(" // ", style=MUTED)
    heading.append(title, style="bold white")
    heading.append("\nREAD-ONLY LIVE SESSION", style=f"bold {SUCCESS}")

    summary = Table.grid(expand=True, padding=(0, 1))
    summary.add_column(style=MUTED, min_width=10, max_width=16)
    summary.add_column(style="white", ratio=1, overflow="fold")
    summary.add_row("Profile", Text(profile, style=f"bold {ACCENT}"))
    summary.add_row("Mode", mode)
    summary.add_row("Window", f"{window:,} lines")
    summary.add_row("Refresh", f"{refresh:g}s")
    if extra:
        summary.add_row("Collector", extra)

    targets = Table(show_header=False, box=None, padding=(0, 1), expand=True)
    targets.add_column("#", justify="right", min_width=2, max_width=4, style=ACCENT)
    targets.add_column("Target", ratio=1, overflow="fold")
    for index, source in enumerate(source_list, start=1):
        targets.add_row(str(index), Text(source))

    guidance = Text("Ctrl+C stops safely. ", style=f"bold {SUCCESS}")
    guidance.append("No source data or host configuration is modified.", style=MUTED)

    body = Group(
        heading,
        Text(""),
        summary,
        Text("\nMONITORING TARGETS", style=f"bold {ACCENT_SOFT}"),
        targets,
        Text(""),
        guidance,
    )
    return bounded(Panel(body, border_style=ACCENT, padding=(1, 1)))


def live_initial_status(kind: str, *, prefix: str | None = None) -> Text:
    message = prefix or f"Initial {kind} scan complete."
    status = Text(f"{message} ", style=f"bold {SUCCESS}")
    status.append("Live monitoring remains active and will refresh when new telemetry arrives.", style=MUTED)
    return status


def live_source_status(source: str, *, available: bool) -> Text:
    """Render a one-line source transition without implying host modification."""
    if available:
        status = Text("SOURCE RECOVERED  ", style=f"bold {SUCCESS}")
        status.append(source, style="white")
        status.append("  monitoring resumed from the safe cursor", style=MUTED)
        return status
    status = Text("SOURCE UNAVAILABLE  ", style=f"bold {WARNING}")
    status.append(source, style="white")
    status.append("  retaining the current dashboard and retrying read-only polling", style=MUTED)
    return status


def live_stopped_status(kind: str, *, degraded: bool = False) -> Text:
    style = WARNING if degraded else SUCCESS
    status = Text(f"\n{kind.upper()} MONITOR STOPPED  ", style=f"bold {style}")
    status.append("No host configuration or source data was modified.", style=MUTED)
    return status
