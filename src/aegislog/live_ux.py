from __future__ import annotations

from collections.abc import Iterable

from rich.console import Group, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .theme import ACCENT, ACCENT_SOFT, MUTED, SUCCESS, WARNING


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
    """Render a consistent, operator-focused summary before live monitoring begins."""
    source_list = tuple(str(source) for source in sources)
    summary = Table.grid(expand=True)
    summary.add_column(style=MUTED, width=18)
    summary.add_column(style="white")
    summary.add_row("Profile", Text(profile, style=f"bold {ACCENT}"))
    summary.add_row("Mode", mode)
    summary.add_row("Rolling window", f"{window:,} lines")
    summary.add_row("Refresh", f"{refresh:g}s")
    summary.add_row("Sources", str(len(source_list)))
    if extra:
        summary.add_row("Collector", extra)

    sources_table = Table(title="Monitoring targets", title_style=f"bold {ACCENT}", border_style=ACCENT_SOFT, expand=True)
    sources_table.add_column("#", justify="right", width=4, style=MUTED)
    sources_table.add_column("Source")
    for index, source in enumerate(source_list, start=1):
        sources_table.add_row(str(index), Text(source))

    guidance = Text("Live analysis is read-only. ", style=SUCCESS)
    guidance.append("The dashboard refreshes in place; press Ctrl+C to stop safely.", style=MUTED)
    return Group(
        Panel(summary, title=title, subtitle="AegisLog real-time defensive monitoring", border_style=ACCENT),
        sources_table,
        Panel(guidance, title="Operator guidance", border_style=ACCENT_SOFT),
    )


def live_initial_status(kind: str, *, prefix: str | None = None) -> Text:
    message = prefix or f"Initial {kind} scan complete."
    status = Text(f"{message} ", style=f"bold {SUCCESS}")
    status.append("Live monitoring remains active and will refresh when new telemetry arrives.", style=MUTED)
    return status


def live_stopped_status(kind: str, *, degraded: bool = False) -> Text:
    style = WARNING if degraded else SUCCESS
    status = Text(f"\n{kind} monitoring stopped safely. ", style=f"bold {style}")
    status.append("No host configuration or source data was modified.", style=MUTED)
    return status
