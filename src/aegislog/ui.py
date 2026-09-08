from __future__ import annotations

from rich.align import Align
from rich.console import RenderableType
from rich.constrain import Constrain
from rich.panel import Panel
from rich.text import Text

from .theme import ACCENT, ACCENT_SOFT, MUTED

MAX_CONTENT_WIDTH = 112
MAX_HOME_WIDTH = 88


def bounded(renderable: RenderableType, max_width: int = MAX_CONTENT_WIDTH) -> RenderableType:
    """Keep dense console views readable on ultrawide terminals without harming narrow screens."""
    return Constrain(renderable, width=max(1, max_width))


def console_title(
    title: str,
    *,
    subtitle: str = "",
    version: str | None = None,
    max_width: int = MAX_CONTENT_WIDTH,
    border_style: str = ACCENT_SOFT,
) -> RenderableType:
    """Render the shared AegisLog page header with one consistent visual hierarchy."""
    text = Text()
    text.append("AEGISLOG", style=f"bold {ACCENT}")
    text.append(" // ", style=MUTED)
    text.append(title.upper(), style="bold white")
    if version:
        text.append(f"  v{version}", style=MUTED)
    if subtitle:
        text.append("\n")
        text.append(subtitle, style=MUTED)
    return bounded(Panel(text, border_style=border_style, padding=(0, 1)), max_width=max_width)


def compact_footer(text: str, *, max_width: int = MAX_CONTENT_WIDTH) -> RenderableType:
    """Keep operator guidance visually attached to the page instead of floating across the terminal."""
    return bounded(Align.left(Text(text, style=MUTED)), max_width=max_width)
