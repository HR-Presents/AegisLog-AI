from __future__ import annotations

import json
import platform
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import typer
from rich.console import Console
from rich.markup import escape
from rich.table import Table
from rich.text import Text

from . import __version__
from .anomaly import score_events
from .baseline import compare as compare_baseline
from .collectors import CollectorError, docker as collect_docker, journal as collect_journal
from .database import add_incidents, get_incident, list_incidents, timeline as database_timeline
from .engine import analyze_file
from .exporters import write_report
from .hunt import extract_indicators, search_incidents
from .incidents import correlate
from .live import RollingAnalyzer
from .parsers import parse_line
from .plugins import apply_rules, load_rules, plugin_dir
from .theme import ACCENT, MUTED, NEUTRAL, severity_text

app = typer.Typer(help="AegisLog — deterministic defensive log investigation in your terminal.", no_args_is_help=True)
console = Console()


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"AegisLog {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Show the installed AegisLog version and exit.",
    ),
) -> None:
    """Defensive log intelligence and investigation from the terminal."""


def _flat_table(*columns: tuple[str, dict]) -> Table:
    table = Table(box=None, expand=True, padding=(0, 2), header_style=MUTED)
    for title, kwargs in columns:
        table.add_column(title, **kwargs)
    return table


def _render(path: Path) -> None:
    total, findings = analyze_file(path)
    counts = Counter(f.severity for f in findings)
    title = Text("AEGISLOG / ANALYZE", style=f"bold {NEUTRAL}")
    console.print(title)
    console.print(Text(str(path), style=MUTED))
    console.print(Text("─" * 48, style="grey35"))
    console.print(f"{total:,} events   {len(findings):,} findings   {counts['CRITICAL']} critical   {counts['HIGH']} high")
    console.print()
    table = _flat_table(
        ("Severity", {"width": 10}),
        ("Finding", {"width": 34}),
        ("Evidence", {"ratio": 1, "overflow": "fold"}),
    )
    for finding in findings[:50]:
        table.add_row(severity_text(finding.severity), escape(finding.title), escape(finding.evidence))
    console.print(table)


@app.command()
def analyze(path: Path = typer.Argument(..., exists=True, dir_okay=False), plugins: bool = True) -> None:
    """Analyze one log file, optionally including local rule plugins."""
    _render(path)
    if plugins:
        rules, errors = load_rules()
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        custom = apply_rules(lines, rules)
        for error in errors:
            console.print(f"Plugin warning: {escape(error)}")
        for finding in custom[:50]:
            console.print(f"[PLUGIN/{finding.severity}] {escape(finding.title)} | {escape(finding.evidence)}")


@app.command()
def threats(path: Path = typer.Argument(..., exists=True, dir_okay=False)) -> None:
    """Show high-confidence security-relevant findings."""
    _, findings = analyze_file(path)
    security = [f for f in findings if f.severity in {"CRITICAL", "HIGH"}]
    for finding in security:
        console.print(f"[{finding.severity}] {escape(finding.title)}\n  {escape(finding.evidence)}\n  Next: {escape(finding.recommendation)}")
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
        console.print(f"[bold]{item.score:>5.1f}[/bold]  {escape(item.key)}  {escape(item.reason)}")


@app.command()
def incidents(path: Path = typer.Argument(..., exists=True, dir_okay=False), persist: bool = False) -> None:
    """Correlate findings into incidents and optionally persist them in SQLite."""
    _, findings = analyze_file(path)
    items = correlate(findings)
    table = _flat_table(
        ("ID", {}), ("Severity", {}), ("Category", {}), ("Events", {}), ("Summary", {"ratio": 1, "overflow": "fold"})
    )
    for item in items:
        table.add_row(item.id, severity_text(item.severity), escape(item.category), str(item.count), escape(item.title))
    console.print(table)
    if persist and items:
        count = add_incidents(str(path), datetime.now(timezone.utc).isoformat(), items)
        console.print(f"Persisted {count} incident records to the AegisLog database.")


@app.command("history")
def incident_history(limit: int = 50, severity: str = "") -> None:
    """Show persisted SQLite incident records."""
    records = list_incidents(limit, severity or None)
    if not records:
        console.print("No persisted incidents yet. Run incidents <log> --persist.")
        return
    table = _flat_table(
        ("DB ID", {}), ("Recorded", {}), ("Severity", {}), ("Source", {}), ("Summary", {"ratio": 1, "overflow": "fold"})
    )
    for item in records:
        table.add_row(str(item["id"]), escape(item["recorded_at"]), item["severity"], escape(item["source"]), escape(item["title"]))
    console.print(table)


@app.command("incident")
def incident_detail(incident_id: int) -> None:
    """Inspect one persisted incident and its evidence."""
    item = get_incident(incident_id)
    if item is None:
        console.print(f"Incident {incident_id} was not found.")
        raise typer.Exit(1)
    console.print(Text(f"INCIDENT {incident_id} / {escape(item['title'])}", style=f"bold {ACCENT}"))
    console.print(Text("─" * 48, style="grey35"))
    console.print(f"Severity   {escape(item['severity'])}")
    console.print(f"Category   {escape(item['category'])}")
    console.print(f"Source     {escape(item['source'])}")
    console.print(f"Recorded   {escape(item['recorded_at'])}")
    console.print(f"Events     {item['event_count']}")
    console.print()
    for evidence in item["evidence"]:
        console.print(f"• {escape(str(evidence))}")


@app.command("timeline")
def timeline(limit: int = 100) -> None:
    """Show the persisted investigation timeline."""
    records = database_timeline(limit)
    if not records:
        console.print("No incident timeline exists yet.")
        return
    table = _flat_table(("Time", {}), ("ID", {}), ("Severity", {}), ("Category", {}), ("Summary", {"ratio": 1}))
    for item in records:
        table.add_row(escape(item["recorded_at"]), str(item["id"]), item["severity"], escape(item["category"]), escape(item["title"]))
    console.print(table)


@app.command("hunt")
def hunt(query: str = "", severity: str = "", category: str = "", source: str = "", limit: int = 100) -> None:
    """Search persisted incidents like a lightweight SOC investigation console."""
    results = search_incidents(query, severity, category, source, limit)
    table = _flat_table(("ID", {}), ("Time", {}), ("Severity", {}), ("Category", {}), ("Source", {}), ("Summary", {"ratio": 1}))
    for item in results:
        table.add_row(str(item.id), escape(item.recorded_at), item.severity, escape(item.category), escape(item.source), escape(item.title))
    console.print(table)


@app.command("indicators")
def indicators(path: Path = typer.Argument(..., exists=True, dir_okay=False)) -> None:
    """Extract defensive IP/domain indicators from a log sample."""
    values = extract_indicators(path.read_text(encoding="utf-8", errors="replace"))
    for kind, items in values.items():
        console.print(f"[bold]{kind}[/bold]")
        for item in items:
            console.print(f"  {escape(item)}")


@app.command("plugins")
def plugins() -> None:
    """List local detection rule plugins and loading errors."""
    rules, errors = load_rules()
    console.print(f"Plugin directory: {escape(str(plugin_dir()))}")
    for rule in rules:
        console.print(f"{escape(rule.id)}: [{rule.severity}] {escape(rule.title)} ({escape(rule.source)})")
    for error in errors:
        console.print(f"ERROR: {escape(error)}")
    if not rules and not errors:
        console.print("No local rule plugins installed.")


@app.command("baseline")
def baseline(
    baseline_path: Path = typer.Argument(..., exists=True, dir_okay=False),
    current_path: Path = typer.Argument(..., exists=True, dir_okay=False),
) -> None:
    """Compare current telemetry with a baseline log sample."""
    before = baseline_path.read_text(encoding="utf-8", errors="replace").splitlines()
    current = current_path.read_text(encoding="utf-8", errors="replace").splitlines()
    deltas = compare_baseline(before, current)
    table = _flat_table(("Event class", {"ratio": 1}), ("Baseline", {}), ("Current", {}), ("Ratio", {}))
    for item in deltas[:50]:
        table.add_row(item.key, str(item.baseline), str(item.current), f"{item.ratio:.2f}x")
    console.print(table)


@app.command()
def collect(
    source: str = typer.Argument(..., help="journal or docker"),
    target: str = "",
    lines: int = 300,
    output: Path = Path("aegislog-collected.log"),
) -> None:
    """Collect bounded recent telemetry from journald or a Docker container."""
    try:
        result = collect_journal(lines, target or None) if source == "journal" else collect_docker(target, lines) if source == "docker" else None
        if result is None:
            raise typer.BadParameter("source must be journal or docker")
    except CollectorError as exc:
        console.print(f"Collection failed: {escape(str(exc))}")
        raise typer.Exit(1)
    output.write_text("\n".join(result.lines) + "\n", encoding="utf-8")
    console.print(f"Collected {len(result.lines)} lines from {escape(result.source)} -> {escape(str(output))}")


@app.command()
def watch(path: Path = typer.Argument(..., exists=True, dir_okay=False), interval: float = 1.0, window: int = 200) -> None:
    """Follow a growing log file with stateful rolling correlation until Ctrl+C."""
    analyzer = RollingAnalyzer(window_size=window)
    console.print(f"Watching {escape(str(path))} with a {window}-line correlation window. Press Ctrl+C to stop.")
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            handle.seek(0, 2)
            while True:
                line = handle.readline()
                if not line:
                    time.sleep(max(interval, 0.1))
                    continue
                findings = analyzer.push(line)
                event = parse_line(line)
                for finding in findings:
                    console.print(f"[{finding.severity}] {escape(finding.title)} | {escape(finding.evidence)}")
                if not findings and event.level in {"error", "warning"}:
                    console.print(f"[{event.level.upper()}] {escape(event.message)}")
    except KeyboardInterrupt:
        console.print("Watch stopped.")


@app.command()
def report(path: Path = typer.Argument(..., exists=True, dir_okay=False), output: Path = Path("aegislog-report.json")) -> None:
    """Write JSON, Markdown, or HTML analysis reports."""
    total, findings = analyze_file(path)
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    anomaly_results = score_events([parse_line(line) for line in lines])
    incident_results = correlate(findings)
    if output.suffix.lower() in {".md", ".markdown", ".html", ".htm"}:
        write_report(output, str(path), total, findings, incident_results)
    else:
        payload = {
            "schema_version": 1,
            "tool_version": __version__,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source": str(path),
            "lines": total,
            "findings": [f.__dict__ for f in findings],
            "anomalies": [a.__dict__ for a in anomaly_results],
            "incidents": [{**i.__dict__, "evidence": list(i.evidence)} for i in incident_results],
        }
        output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    console.print(f"Report written to {escape(str(output))}")


@app.command()
def doctor() -> None:
    """Check the local AegisLog runtime."""
    console.print(f"AegisLog {__version__}")
    console.print(f"Python: {platform.python_version()}")
    console.print(f"Platform: {escape(platform.platform())}")
    console.print("Detection engine: ready")
    console.print("Mode: local / deterministic / read-only", style=MUTED)


@app.command()
def scan(path: Path = typer.Argument(Path("/var/log"))) -> None:
    """Scan readable log files under a directory."""
    if not path.exists() or not path.is_dir():
        raise typer.BadParameter("scan path must be an existing directory")
    files = [p for p in path.rglob("*") if p.is_file() and (p.suffix in {".log", ".txt"} or "log" in p.name.lower())][:100]
    console.print(f"Scanning {len(files)} candidate log files under {escape(str(path))}")
    for file in files:
        try:
            _, findings = analyze_file(file)
        except (OSError, PermissionError):
            continue
        serious = sum(f.severity in {"CRITICAL", "HIGH"} for f in findings)
        if findings:
            console.print(f"{escape(str(file))}: {len(findings)} findings ({serious} high/critical)")


if __name__ == "__main__":
    app()
