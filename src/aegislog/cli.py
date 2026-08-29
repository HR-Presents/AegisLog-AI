from __future__ import annotations

import json
import platform
import time
from collections import Counter
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import __version__
from .ai import InvestigationContext, build_safe_prompt, local_answer
from .anomaly import score_events
from .collectors import CollectorError, docker as collect_docker, journal as collect_journal
from .config import load_config, save_config
from .engine import analyze_file, analyze_lines
from .incidents import correlate
from .parsers import parse_line
from .providers import ProviderError, run_provider
from .store import load_incidents, save_incidents

app = typer.Typer(help="AegisLog AI — defensive log intelligence in your terminal.", no_args_is_help=True)
console = Console()


def _render(path: Path) -> None:
    total, findings = analyze_file(path)
    counts = Counter(f.severity for f in findings)
    console.print(Panel.fit(f"[bold]AegisLog AI[/bold]  v{__version__}\n{path}"))
    console.print(f"Lines: [bold]{total}[/bold]  Findings: [bold]{len(findings)}[/bold]  Critical: {counts['CRITICAL']}  High: {counts['HIGH']}")
    table = Table(show_lines=True)
    table.add_column("Severity", width=10)
    table.add_column("Finding", width=34)
    table.add_column("Evidence")
    for finding in findings[:50]:
        table.add_row(finding.severity, finding.title, finding.evidence)
    console.print(table)


@app.command()
def analyze(path: Path = typer.Argument(..., exists=True, dir_okay=False)) -> None:
    """Analyze one log file for errors, suspicious activity, and anomalies."""
    _render(path)


@app.command()
def threats(path: Path = typer.Argument(..., exists=True, dir_okay=False)) -> None:
    """Show high-confidence security-relevant findings."""
    _, findings = analyze_file(path)
    security = [f for f in findings if f.severity in {"CRITICAL", "HIGH"}]
    for finding in security:
        console.print(f"[{finding.severity}] {finding.title}\n  {finding.evidence}\n  Next: {finding.recommendation}")
    if not security:
        console.print("No high-confidence high/critical findings detected by local rules.")


@app.command()
def anomalies(path: Path = typer.Argument(..., exists=True, dir_okay=False)) -> None:
    """Find rare local event classes using lightweight anomaly scoring."""
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    results = score_events([parse_line(line) for line in lines])
    if not results:
        console.print("No frequency anomalies detected in this sample.")
        return
    for item in results[:30]:
        console.print(f"[bold]{item.score:>5.1f}[/bold]  {item.key}  {item.reason}")


@app.command()
def incidents(path: Path = typer.Argument(..., exists=True, dir_okay=False), persist: bool = False) -> None:
    """Correlate findings into incidents and optionally persist them."""
    _, findings = analyze_file(path)
    items = correlate(findings)
    table = Table(show_lines=True)
    table.add_column("ID"); table.add_column("Severity"); table.add_column("Category"); table.add_column("Events"); table.add_column("Summary")
    for item in items:
        table.add_row(item.id, item.severity, item.category, str(item.count), item.title)
    console.print(table)
    if persist and items:
        console.print(f"Incident history updated: {save_incidents(str(path), items)}")


@app.command("history")
def incident_history(limit: int = 50) -> None:
    """Show previously persisted incident records."""
    records = load_incidents(limit)
    if not records:
        console.print("No persisted incidents yet. Run incidents <log> --persist.")
        return
    table = Table(show_lines=True)
    table.add_column("Recorded"); table.add_column("Severity"); table.add_column("Source"); table.add_column("Summary")
    for item in records:
        table.add_row(item.get("recorded_at", ""), item.get("severity", ""), item.get("source", ""), item.get("title", ""))
    console.print(table)


@app.command("ask")
def ask_log(question: str, path: Path = typer.Argument(..., exists=True, dir_okay=False), local: bool = False) -> None:
    """Ask a defensive investigation question using local analysis or configured AI."""
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    _, findings = analyze_file(path)
    context = InvestigationContext(question=question, findings=findings, log_excerpt=lines[-80:])
    cfg = load_config()
    provider = str(cfg.get("ai_provider", "none"))
    if local or provider == "none":
        console.print(Panel(local_answer(context), title=f"Investigation: {question}"))
        return
    try:
        response = run_provider(provider, build_safe_prompt(context), str(cfg.get("model", "")), cfg.get("base_url"))
        console.print(Panel(response.text, title=f"AI Investigation — {response.provider}/{response.model}"))
    except ProviderError as exc:
        console.print(f"AI provider unavailable: {exc}\nFalling back to local analysis.")
        console.print(Panel(local_answer(context), title=f"Investigation: {question}"))


@app.command()
def collect(source: str = typer.Argument(..., help="journal or docker"), target: str = "", lines: int = 300, output: Path = Path("aegislog-collected.log")) -> None:
    """Collect bounded recent telemetry from journald or a Docker container."""
    try:
        result = collect_journal(lines, target or None) if source == "journal" else collect_docker(target, lines) if source == "docker" else None
        if result is None:
            raise typer.BadParameter("source must be journal or docker")
    except CollectorError as exc:
        console.print(f"Collection failed: {exc}")
        raise typer.Exit(1)
    output.write_text("\n".join(result.lines) + "\n", encoding="utf-8")
    console.print(f"Collected {len(result.lines)} lines from {result.source} -> {output}")


@app.command()
def watch(path: Path = typer.Argument(..., exists=True, dir_okay=False), interval: float = 1.0) -> None:
    """Follow a growing log file and analyze new events until Ctrl+C."""
    console.print(f"Watching {path}. Press Ctrl+C to stop.")
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            handle.seek(0, 2)
            while True:
                line = handle.readline()
                if not line:
                    time.sleep(max(interval, 0.1)); continue
                findings = analyze_lines([line]); event = parse_line(line)
                for finding in findings:
                    console.print(f"[{finding.severity}] {finding.title} | {finding.evidence}")
                if not findings and event.level in {"error", "warning"}:
                    console.print(f"[{event.level.upper()}] {event.message}")
    except KeyboardInterrupt:
        console.print("Watch stopped.")


@app.command()
def report(path: Path = typer.Argument(..., exists=True, dir_okay=False), output: Path = Path("aegislog-report.json")) -> None:
    """Write a machine-readable JSON analysis report."""
    total, findings = analyze_file(path)
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    anomaly_results = score_events([parse_line(line) for line in lines]); incident_results = correlate(findings)
    payload = {"source": str(path), "lines": total, "findings": [f.__dict__ for f in findings], "anomalies": [a.__dict__ for a in anomaly_results], "incidents": [{**i.__dict__, "evidence": list(i.evidence)} for i in incident_results]}
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8"); console.print(f"Report written to {output}")


@app.command()
def config(provider: str = "none", model: str = "", base_url: str = "") -> None:
    """Set non-secret provider preferences. API keys must stay in environment variables."""
    path = save_config({"ai_provider": provider, "model": model, "base_url": base_url or None})
    console.print(f"Configuration saved to {path}")


@app.command()
def doctor() -> None:
    """Check the local AegisLog runtime."""
    cfg = load_config()
    console.print(f"AegisLog AI {__version__}\nPython: {platform.python_version()}\nPlatform: {platform.platform()}")
    console.print("Local detection engine: ready")
    console.print(f"AI provider preference: {cfg.get('ai_provider', 'none')}  model: {cfg.get('model', '') or '(default)'}")


@app.command()
def scan(path: Path = typer.Argument(Path("/var/log"))) -> None:
    """Scan readable log files under a directory."""
    if not path.exists() or not path.is_dir(): raise typer.BadParameter("scan path must be an existing directory")
    files = [p for p in path.rglob("*") if p.is_file() and (p.suffix in {".log", ".txt"} or "log" in p.name.lower())][:100]
    console.print(f"Scanning {len(files)} candidate log files under {path}")
    for file in files:
        try: _, findings = analyze_file(file)
        except (OSError, PermissionError): continue
        serious = sum(f.severity in {"CRITICAL", "HIGH"} for f in findings)
        if findings: console.print(f"{file}: {len(findings)} findings ({serious} high/critical)")


if __name__ == "__main__": app()
