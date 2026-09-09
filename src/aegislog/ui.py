from __future__ import annotations

from rich.align import Align
from rich.console import Group, RenderableType
from rich.panel import Panel
from rich.text import Text

from .theme import ACCENT, ACCENT_SOFT, MUTED, SUCCESS

# Kept for compatibility with older callers/tests. The V3 terminal design no
# longer caps content to a narrow fixed column on wide terminals.
MAX_CONTENT_WIDTH = 0
MAX_HOME_WIDTH = 0


def bounded(renderable: RenderableType, max_width: int = MAX_CONTENT_WIDTH) -> RenderableType:
    """Render across the available terminal viewport.

    ``max_width`` is retained for API compatibility, but V3 intentionally does
    not force a narrow fixed-width column on wide screens.
    """
    return renderable


def console_title(
    title: str,
    *,
    subtitle: str = "",
    version: str | None = None,
    max_width: int = MAX_CONTENT_WIDTH,
    border_style: str = ACCENT_SOFT,
) -> RenderableType:
    """Render shared AegisLog page chrome with clear product and page hierarchy."""
    heading = Text()
    heading.append("AEGIS", style=f"bold {ACCENT}")
    heading.append("LOG", style="bold white")
    heading.append("  //  ", style=MUTED)
    heading.append(title.upper(), style="bold white")
    if version:
        heading.append(f"  v{version}", style=MUTED)

    status = Text()
    status.append("READY", style=f"bold {SUCCESS}")
    status.append("  LOCAL-FIRST", style=f"bold {ACCENT_SOFT}")
    status.append("  READ-ONLY", style=MUTED)

    body: list[RenderableType] = [heading, status]
    if subtitle:
        body.insert(1, Text(subtitle, style=MUTED))

    return Panel(
        Group(*body),
        border_style=border_style,
        padding=(0, 1),
        expand=True,
    )


def compact_footer(text: str, *, max_width: int = MAX_CONTENT_WIDTH) -> RenderableType:
    """Render operator guidance across the active terminal viewport."""
    footer = Text()
    footer.append("NEXT  ", style=f"bold {ACCENT_SOFT}")
    footer.append(text, style=MUTED)
    return Align.left(footer)
