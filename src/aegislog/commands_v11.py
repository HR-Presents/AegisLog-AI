from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text

from .dashboard import analyze_dashboard, render_dashboard
from .plugins import apply_rules, load_rules
from .reporting import write_html_report
from .theme import ACCENT, MUTED, SUCCESS, WARNING
from .ui import bounded

console = Console()


def _report_ready_panel(report_path: Path) -> Panel:
    """Render a concise, operator-focused handoff after report generation."""
    body = Text()
    body.append("LOCATION  ", style=MUTED)
    body.append(str(report_path), style=f"bold {ACCENT}")
    body.append("\nSTATUS    ", style=MUTED)
    body.append("Generated locally / source unchanged", style=SUCCESS)
    body.append("\nNEXT      ", style=MUTED)
    body.append("Open in a browser to review, print, or save as PDF.", style="white")
    return Panel(
        body,
        title=Text(" REPORT READY ", style=f"bold {SUCCESS}"),
        title_align="left",
        border_style=SUCCESS,
        padding=(1, 2),
        expand=True,
    )


def dashboard(
    path: Path = typer.Argument(..., exists=True, dir_okay=False),
    timestamp_year: int | None = typer.Option(
        None,
        "--timestamp-year",
        min=1970,
        max=9999,
        help="Year to apply to RFC3164/syslog timestamps that omit a year. Never inferred automatically.",
    ),
) -> None:
    """Open the full terminal investigation dashboard for one log file."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        console=console,
    ) as progress:
        task = progress.add_task(f"Analyzing {path.name}...", total=None)
        data = analyze_dashboard(path, timestamp_year_hint=timestamp_year)
        progress.update(task, description="Building terminal dashboard...")
    console.print(bounded(render_dashboard(data, screen_width=console.size.width)))
    try:
        report_path = write_html_report(data)
    except OSError as exc:
        console.print(Text(f"Report could not be written: {exc}", style=WARNING))
    else:
        console.print()
        console.print(_report_ready_panel(report_path))


def analyze_dashboard_command(
    path: Path = typer.Argument(..., exists=True, dir_okay=False),
    plugins: bool = typer.Option(True, "--plugins/--no-plugins", help="Include local declarative detection packs."),
    timestamp_year: int | None = typer.Option(
        None,
        "--timestamp-year",
        min=1970,
        max=9999,
        help="Year to apply to RFC3164/syslog timestamps that omit a year. Never inferred automatically.",
    ),
) -> None:
    """Analyze a log and open the complete AegisLog terminal dashboard."""
    dashboard(path, timestamp_year=timestamp_year)
    if plugins:
        rules, errors = load_rules()
        if not rules and not errors:
            return
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            custom = apply_rules(handle.readlines(), rules)
        if errors:
            console.print(f"Rule-pack warnings: {len(errors)}. Run `aegislog plugins` for details.")
        if custom:
            console.print(
                f"Additional local rule-pack findings: {len(custom)}. "
                "Run `aegislog plugins` to inspect installed packs."
            )


def replace_analyze_command(app: typer.Typer) -> None:
    """Upgrade the legacy analyze callback without duplicating the public command."""
    for command in app.registered_commands:
        callback = getattr(command, "callback", None)
        if callback is not None and getattr(callback, "__name__", "") == "analyze":
            command.callback = analyze_dashboard_command
            command.name = "analyze"
            return
    raise RuntimeError("AegisLog analyze command was not registered")
