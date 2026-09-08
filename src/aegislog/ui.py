from __future__ import annotations

from rich.align import Align
from rich.console import RenderableType
from rich.panel import Panel
from rich.text import Text

from .theme import ACCENT, ACCENT_SOFT, MUTED

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
    """Render the shared AegisLog page header using the full terminal width."""
    text = Text()
    text.append("AEGISLOG", style=f"bold {ACCENT}")
    text.append(" // ", style=MUTED)
    text.append(title.upper(), style="bold white")
    if version:
        text.append(f"  v{version}", style=MUTED)
    if subtitle:
        text.append("\n")
        text.append(subtitle, style=MUTED)
    return Panel(text, border_style=border_style, padding=(0, 1), expand=True)


def compact_footer(text: str, *, max_width: int = MAX_CONTENT_WIDTH) -> RenderableType:
    """Render operator guidance across the active terminal viewport."""
    return Align.left(Text(text, style=MUTED))
