from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .behavior import compare_windows
from .correlation import correlate_entities
from .engine import analyze_file
from .streaming import analyze_stream

console = Console()


def stream(path: Path = typer.Argument(..., exists=True, dir_okay=False), chunk_size: int = 2000) -> None:
    """Analyze a large log file incrementally with bounded memory."""
    summary = analyze_stream(path, chunk_size=chunk_size)
    console.print(f"Lines: {summary.lines}  Chunks: {summary.chunks}  Findings retained: {len(summary.findings)}")
    table = Table(show_lines=True)
    table.add_column("Severity")
    table.add_column("Count")
    for severity, count in sorted(summary.severities.items()):
        table.add_row(severity, str(count))
    console.print(table)


def entities(path: Path = typer.Argument(..., exists=True, dir_okay=False), limit: int = 50) -> None:
    """Correlate IP, user, host, service and container entities in findings."""
    _, findings = analyze_file(path)
    links = correlate_entities(findings)
    table = Table(show_lines=True)
    table.add_column("Score")
    table.add_column("Type")
    table.add_column("Entity")
    table.add_column("Events")
    table.add_column("Categories")
    table.add_column("Severities")
    for item in links[: max(1, min(limit, 500))]:
        table.add_row(str(item.score), item.entity_type, item.entity, str(item.event_count), ", ".join(item.categories), ", ".join(item.severities))
    console.print(table)


def behavior(
    baseline: list[Path] = typer.Option(..., "--baseline", exists=True, dir_okay=False),
    current: Path = typer.Option(..., "--current", exists=True, dir_okay=False),
) -> None:
    """Compare a current log window against multiple historical baseline windows."""
    baseline_windows = [path.read_text(encoding="utf-8", errors="replace").splitlines() for path in baseline]
    current_lines = current.read_text(encoding="utf-8", errors="replace").splitlines()
    deltas = compare_windows(baseline_windows, current_lines)
    table = Table(show_lines=True)
    table.add_column("Bucket")
    table.add_column("Key")
    table.add_column("Baseline avg")
    table.add_column("Current")
    table.add_column("Ratio")
    for item in deltas[:100]:
        table.add_row(item.bucket, item.key, f"{item.baseline:.2f}", str(item.current), f"{item.ratio:.2f}x")
    console.print(table)
