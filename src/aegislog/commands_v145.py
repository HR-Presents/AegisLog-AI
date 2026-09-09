from __future__ import annotations

from rich.console import Group, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from . import commands_v144 as legacy
from .commands_ai import interactive_ai_analyst
from .theme import ACCENT, HIGH, INCIDENT, INFO, MUTED, WARNING

_LEGACY_INLINE_COMMAND = legacy._run_inline_command


def _input_panel(
    title: str,
    lines: list[tuple[str, str]],
    accent: str = ACCENT,
    *,
    screen_width: int | None = None,
    primary_label: str | None = None,
) -> Panel:
    """Render readable generic panels while reserving stronger emphasis for primary input."""
    frame_width = legacy._frame_width(screen_width)
    grid = Table.grid(expand=True, padding=(0, 1))
    grid.add_column(width=11 if frame_width < 60 else 14, no_wrap=True)
    grid.add_column(ratio=1, overflow="fold")
    for label, value in lines:
        if primary_label is not None and label == primary_label:
            grid.add_row(
                Text(f"▶ {label}", style=f"bold {accent}"),
                Text(value, style="bold white"),
            )
        elif primary_label is None:
            grid.add_row(
                Text(label, style=f"bold {accent}"),
                Text(value, style="white"),
            )
        else:
            grid.add_row(Text(label, style=MUTED), Text(value, style=MUTED))
    return Panel(
        grid,
        title=Text(f" {title} ", style=f"bold {accent}"),
        title_align="left",
        border_style=legacy.ACCENT_SOFT,
        padding=(0, 1),
        width=frame_width,
    )


def _menu(screen_width: int | None = None) -> RenderableType:
    """Render Mission Control with the optional AI analyst clearly discoverable."""
    frame_width = legacy._frame_width(screen_width)
    operations = [
        ("01", "ANALYZE LOG", "Static investigation and HTML report"),
        ("02", "LIVE MONITOR", "Continuous detection for one log"),
        ("03", "MULTI-SOURCE SOC", "Correlate multiple live sources"),
    ]
    investigation = [
        ("04", "NATIVE LOGS", "Inspect OS or container telemetry"),
        ("05", "NATIVE MONITOR", "Watch native telemetry read-only"),
        ("06", "INCIDENT INTEL", "Review correlated evidence chains"),
        ("A", "AI ANALYST", "Ask Local, Ollama, or opt-in remote AI"),
    ]
    system = [
        ("07", "DEMO", "Run the built-in investigation dataset"),
        ("08", "HEALTH", "Check engine and collector readiness"),
        ("09", "COMMANDS", "Open the command reference"),
    ]
    control = [
        ("C", "COMMAND MODE", "Open the direct command interface"),
        ("Q", "EXIT", "Close AegisLog safely"),
    ]

    left_sections = (
        ("OPERATIONS", operations, ACCENT),
        ("INVESTIGATION", investigation, INCIDENT),
    )
    right_sections = (
        ("SYSTEM / TOOLS", system, INFO),
        ("CONTROL", control, WARNING),
    )

    if frame_width < legacy._NARROW_MENU_BREAKPOINT:
        content: RenderableType = legacy._menu_column(
            left_sections + right_sections,
            compact=True,
        )
    elif frame_width >= legacy._WIDE_MENU_BREAKPOINT:
        layout = Table.grid(expand=True, padding=(0, 2))
        layout.add_column(ratio=1)
        layout.add_column(ratio=1)
        layout.add_row(
            legacy._menu_column(left_sections, compact=False),
            legacy._menu_column(right_sections, compact=False),
        )
        content = layout
    else:
        content = legacy._menu_column(left_sections + right_sections, compact=False)

    return Panel(
        content,
        title=Text(" MISSION CONTROL ", style=f"bold {ACCENT}"),
        title_align="left",
        border_style=legacy.ACCENT_SOFT,
        padding=(1, 1),
        width=frame_width,
    )


def _home(screen_width: int | None = None) -> RenderableType:
    footer = Text()
    footer.append("01-09", style=f"bold {ACCENT}")
    footer.append(" run   ", style=MUTED)
    footer.append("A", style=f"bold {INCIDENT}")
    footer.append(" AI analyst   ", style=MUTED)
    footer.append("C", style=f"bold {WARNING}")
    footer.append(" command mode   ", style=MUTED)
    footer.append("Q", style=f"bold {HIGH}")
    footer.append(" exit   |   reports automatic   |   Ctrl+C stops live views", style=MUTED)
    return Group(legacy._header(screen_width), Text(""), _menu(screen_width), Text(""), footer)


def _ai_workspace() -> None:
    path = legacy._choose_single_file_workspace(
        "AI ANALYST",
        "Ask an optional AI assistant about deterministic AegisLog findings.",
        INCIDENT,
        output_note="Local by default; remote providers require explicit consent",
    )
    if path is None:
        return

    legacy.console.clear()
    legacy.console.print(
        legacy._operation_header(
            "AI ANALYST",
            "Provider-assisted investigation. Detection results remain deterministic and unchanged.",
            INCIDENT,
        )
    )
    legacy.console.print()
    interactive_ai_analyst(path)


def _run_inline_command(raw: str) -> None:
    if raw.strip().lower() in {"a", "ai", "ai-analyst"}:
        _ai_workspace()
        return
    _LEGACY_INLINE_COMMAND(raw)


def start() -> None:
    """Run the polished control center with the AI analyst extension enabled."""
    original_home = legacy._home
    original_inline = legacy._run_inline_command
    original_input_panel = legacy._input_panel
    try:
        legacy._home = _home
        legacy._run_inline_command = _run_inline_command
        legacy._input_panel = _input_panel
        legacy.start()
    finally:
        legacy._home = original_home
        legacy._run_inline_command = original_inline
        legacy._input_panel = original_input_panel


__all__ = ["start"]
