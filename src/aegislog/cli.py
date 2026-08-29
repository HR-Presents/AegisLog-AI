from __future__ import annotations

import json
import platform
from collections import Counter
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import __version__
from .engine import analyze_file

app = typer.Typer(help="AegisLog AI — defensive log intelligence in your terminal.", no_args_is_help=True)
console = Console()


def _render(path: Path) -> None:
    total, findings = analyze_file(path)
    counts = Counter(f.severity for f in findings)
    console.print(Panel.fit(f"[bold]AegisLog AI[/bold]  v{__version__}\n{path}"))
    console.print(f"Lines analyzed: [bold]{total}[/bold]   Findings: [bold]{len(findings)}[/bold]   Critical: {counts['CRITICAL']}   High: {counts['HIGH']}")
    table = Table(show_lines=True)
    table.add_column("Severity", width=10)
    table.add_column("Finding", width=34)
    table.add_column("Evidence")
    for finding in findings[:50]:
        table.add_row(finding.severity, finding.title, finding.evidence)
    console.print(table)
    if findings:
        console.print("\n[bold]Recommended investigation[/bold]")
        for finding in findings[:8]:
            console.print(f"• {finding.recommendation}")


@app.command()
def analyze(path: Path = typer.Argument(..., exists=True, dir_okay=False)) -> None:
    """Analyze one log file for errors, suspicious activity, and anomalies."""
    _render(path)


@app.command()
def threats(path: Path = typer.Argument(..., exists=True, dir_okay=False)) -> None:
    """Show security-relevant findings from a log file."""
    _, findings = analyze_file(path)
    security = [f for f in findings if f.severity in {"CRITICAL", "HIGH"}]
    for finding in security:
        console.print(f"[{finding.severity}] {finding.title}\n  {finding.evidence}\n  Next: {finding.recommendation}")
    if not security:
        console.print("No high-confidence high/critical findings detected by local rules.")


@app.command()
def report(path: Path = typer.Argument(..., exists=True, dir_okay=False), output: Path = Path("aegislog-report.json")) -> None:
    """Write a machine-readable JSON analysis report."""
    total, findings = analyze_file(path)
    payload = {"source": str(path), "lines": total, "findings": [f.__dict__ for f in findings]}
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    console.print(f"Report written to {output}")


@app.command()
def doctor() -> None:
    """Check the local AegisLog runtime."""
    console.print(f"AegisLog AI {__version__}")
    console.print(f"Python: {platform.python_version()}")
    console.print(f"Platform: {platform.platform()}")
    console.print("Local detection engine: ready")
    console.print("AI provider: optional; local analysis works without one")


@app.command()
def scan(path: Path = typer.Argument(Path("/var/log"))) -> None:
    """Scan readable .log files under a directory."""
    if not path.exists() or not path.is_dir():
        raise typer.BadParameter("scan path must be an existing directory")
    files = list(path.rglob("*.log"))[:100]
    console.print(f"Scanning {len(files)} log files under {path}")
    for file in files:
        try:
            _, findings = analyze_file(file)
        except (OSError, PermissionError):
            continue
        serious = sum(f.severity in {"CRITICAL", "HIGH"} for f in findings)
        if findings:
            console.print(f"{file}: {len(findings)} findings ({serious} high/critical)")


if __name__ == "__main__":
    app()
