from __future__ import annotations

from rich.align import Align
from rich.console import Group, RenderableType
from rich.text import Text

from .theme import ACCENT, MUTED, NEUTRAL, SUCCESS

MAX_CONTENT_WIDTH = 0
MAX_HOME_WIDTH = 0


def bounded(renderable: RenderableType, max_width: int = MAX_CONTENT_WIDTH) -> RenderableType:
    """Render across the available terminal viewport."""
    return renderable


def console_title(
    title: str,
    *,
    subtitle: str = "",
    version: str | None = None,
    max_width: int = MAX_CONTENT_WIDTH,
    border_style: str = ACCENT,
) -> RenderableType:
    """Render quiet shared page chrome without enclosing every page in a panel."""
    heading = Text()
    heading.append("AEGISLOG", style=f"bold {NEUTRAL}")
    heading.append(" / ", style=MUTED)
    heading.append(title.upper(), style=f"bold {ACCENT}")
    if version:
        heading.append(f"  v{version}", style=MUTED)

    rule = Text("─" * 48, style="grey35")
    status = Text()
    status.append("● ", style=SUCCESS)
    status.append("READY", style=f"bold {SUCCESS}")
    status.append("   LOCAL-FIRST   READ-ONLY", style=MUTED)

    body: list[RenderableType] = [heading]
    if subtitle:
        body.append(Text(subtitle, style=MUTED))
    body.extend([rule, status])
    return Group(*body)


def compact_footer(text: str, *, max_width: int = MAX_CONTENT_WIDTH) -> RenderableType:
    """Render low-emphasis operator guidance."""
    footer = Text()
    footer.append("›  ", style=f"bold {ACCENT}")
    footer.append(text, style=MUTED)
    return Align.left(footer)
