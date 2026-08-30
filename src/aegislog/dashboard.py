from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from rich.text import Text
from rich.markup import escape
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.timer import Timer
from textual.widgets import DataTable, Footer, Header, Input, Static, TabbedContent, TabPane

from .anomaly import Anomaly, score_events
from .engine import Finding, analyze_file
from .hunt import extract_indicators
from .incidents import Incident, correlate
from .parsers import parse_line


@dataclass(frozen=True)
class DashboardAnalysis:
    path: Path
    line_count: int
    findings: tuple[Finding, ...]
    incidents: tuple[Incident, ...]
    anomalies: tuple[Anomaly, ...]
    indicators: dict[str, list[str]]
    analyzed_at: str


def build_dashboard_analysis(path: Path) -> DashboardAnalysis:
    """Run the complete local analysis pipeline for the terminal dashboard."""
    line_count, findings = analyze_file(path)
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return DashboardAnalysis(
        path=path,
        line_count=line_count,
        findings=tuple(findings),
        incidents=tuple(correlate(findings)),
        anomalies=tuple(score_events([parse_line(line) for line in lines])),
        indicators=extract_indicators("\n".join(lines)),
        analyzed_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
    )


SEVERITY_COLORS = {
    "CRITICAL": "bold white on red",
    "HIGH": "bold #fb7185",
    "MEDIUM": "bold #facc15",
    "LOW": "#22d3ee",
    "INFO": "dim white",
}


class AegisDashboard(App[None]):
    """Interactive SOC-style command center for one analyzed log file."""

    TITLE = "AEGISLOG AI"
    SUB_TITLE = "SECURITY OPERATIONS COMMAND CENTER"
    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("f5", "refresh_analysis", "Re-analyze"),
        Binding("f6", "toggle_live", "Live mode"),
        Binding("f8", "export_report", "Export JSON"),
        Binding("escape", "clear_filter", "Clear filter", priority=True),
    ]
    CSS = """
    Screen { background: #030712; color: #dbeafe; }
    Header { background: #071a2e; color: #38bdf8; }
    Footer { background: #071a2e; color: #bae6fd; }
    #status-strip { height: 3; padding: 1 2; background: #07111f; color: #7dd3fc; border-bottom: solid #164e63; }
    #summary { height: 7; padding: 1 2; }
    .metric { width: 1fr; height: 5; margin: 0 1; padding: 1 2; border: round #1d4ed8; background: #0b1729; text-align: center; }
    #risk { border: round #dc2626; }
    #threats { border: round #f97316; }
    #filter { margin: 0 2 1 2; border: tall #2563eb; background: #07111f; }
    TabbedContent { margin: 0 1; background: #030712; }
    TabPane { padding: 1; background: #030712; }
    DataTable { height: 1fr; background: #07111f; border: round #164e63; }
    #finding-detail { height: 9; margin-top: 1; padding: 1 2; border: round #2563eb; background: #0b1729; }
    #command-grid { height: 17; }
    .command-card { width: 1fr; height: 16; margin: 0 1; padding: 1 2; border: round #1d4ed8; background: #0b1729; }
    #risk-card { border: round #dc2626; }
    #priority-action { height: 8; margin: 1; padding: 1 2; border: round #0e7490; background: #071a2e; }
    """

    def __init__(self, path: Path) -> None:
        self.path = path
        self.analysis = build_dashboard_analysis(path)
        self.active_query = ""
        self.live_enabled = False
        self.live_timer: Timer | None = None
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(id="status-strip")
        with Horizontal(id="summary"):
            yield Static(id="risk", classes="metric")
            yield Static(id="findings", classes="metric")
            yield Static(id="threats", classes="metric")
            yield Static(id="incidents", classes="metric")
        with TabbedContent(initial="command-tab"):
            with TabPane("Command Center", id="command-tab"):
                with Horizontal(id="command-grid"):
                    yield Static(id="risk-card", classes="command-card")
                    yield Static(id="severity-card", classes="command-card")
                    yield Static(id="coverage-card", classes="command-card")
                yield Static(id="priority-action")
            with TabPane("Findings", id="findings-tab"):
                with Vertical():
                    yield Input(placeholder="Search severity, category, finding, or evidence...", id="filter")
                    yield DataTable(id="findings-table", zebra_stripes=True, cursor_type="row")
                    yield Static("Select a finding to inspect its evidence and recommended response.", id="finding-detail", markup=False)
            with TabPane("Incidents", id="incidents-tab"):
                yield DataTable(id="incidents-table", zebra_stripes=True, cursor_type="row")
            with TabPane("Anomalies", id="anomalies-tab"):
                yield DataTable(id="anomalies-table", zebra_stripes=True, cursor_type="row")
            with TabPane("Indicators", id="indicators-tab"):
                yield DataTable(id="indicators-table", zebra_stripes=True, cursor_type="row")
        yield Footer()

    def on_mount(self) -> None:
        self._configure_tables()
        self.live_timer = self.set_interval(3.0, self._live_refresh, pause=True)
        self._render_analysis()

    def _configure_tables(self) -> None:
        self.query_one("#findings-table", DataTable).add_columns("Severity", "Category", "Finding", "Evidence", "Recommended next step")
        self.query_one("#incidents-table", DataTable).add_columns("ID", "Severity", "Category", "Events", "Summary")
        self.query_one("#anomalies-table", DataTable).add_columns("Score", "Event class", "Reason")
        self.query_one("#indicators-table", DataTable).add_columns("Type", "Indicator")

    @staticmethod
    def _risk_level(counts: Counter[str]) -> str:
        if counts["CRITICAL"]:
            return "CRITICAL"
        if counts["HIGH"]:
            return "HIGH"
        if counts["MEDIUM"]:
            return "ELEVATED"
        return "LOW"

    def _render_analysis(self) -> None:
        counts = Counter(item.severity for item in self.analysis.findings)
        risk = self._risk_level(counts)
        threats = counts["CRITICAL"] + counts["HIGH"]
        metrics = {
            "risk": ("RISK POSTURE", risk),
            "findings": ("TOTAL FINDINGS", len(self.analysis.findings)),
            "threats": ("HIGH / CRITICAL", threats),
            "incidents": ("INCIDENTS", len(self.analysis.incidents)),
        }
        for widget_id, (label, value) in metrics.items():
            self.query_one(f"#{widget_id}", Static).update(f"[bold #93c5fd]{label}[/]\n[bold white]{value}[/]")
        mode = "LIVE • 3s refresh" if self.live_enabled else "SNAPSHOT"
        self.query_one("#status-strip", Static).update(
            f"[bold #22d3ee]● ANALYSIS COMPLETE[/]   {mode}   •   {escape(self.analysis.path.name)}   •   {self.analysis.line_count:,} lines   •   {self.analysis.analyzed_at}"
        )
        risk_color = {"CRITICAL": "#ef4444", "HIGH": "#f97316", "ELEVATED": "#eab308", "LOW": "#22c55e"}[risk]
        self.query_one("#risk-card", Static).update(
            f"[bold #93c5fd]SECURITY POSTURE[/]\n\n[bold {risk_color}]{risk}[/]\n\n"
            f"Critical signals  [bold]{counts['CRITICAL']}[/]\nHigh signals      [bold]{counts['HIGH']}[/]\n"
            f"Incidents         [bold]{len(self.analysis.incidents)}[/]"
        )
        maximum = max(counts.values(), default=1)
        bars = []
        for level, color in (("CRITICAL", "#ef4444"), ("HIGH", "#f97316"), ("MEDIUM", "#eab308"), ("LOW", "#22d3ee")):
            width = round((counts[level] / maximum) * 14) if counts[level] else 0
            bars.append(f"[{color}]{level:<8} {'█' * width:<14}[/] {counts[level]}")
        self.query_one("#severity-card", Static).update("[bold #93c5fd]SEVERITY DISTRIBUTION[/]\n\n" + "\n\n".join(bars))
        indicator_count = sum(len(values) for values in self.analysis.indicators.values())
        self.query_one("#coverage-card", Static).update(
            f"[bold #93c5fd]ANALYSIS COVERAGE[/]\n\nSource       [bold]{escape(self.analysis.path.name)}[/]\n"
            f"Lines        [bold]{self.analysis.line_count:,}[/]\nFindings     [bold]{len(self.analysis.findings)}[/]\n"
            f"Anomalies    [bold]{len(self.analysis.anomalies)}[/]\nIndicators   [bold]{indicator_count}[/]"
        )
        recommendation = self.analysis.findings[0].recommendation if self.analysis.findings else "No rule-backed threats were detected. Continue monitoring and validate log coverage."
        self.query_one("#priority-action", Static).update(
            f"[bold #22d3ee]PRIORITY ANALYST ACTION[/]\n\n{recommendation}\n\n"
            "[dim]Validate context before containment or remediation. Findings are investigative signals, not proof of compromise.[/]"
        )
        self._render_findings()
        self._render_incidents()
        self._render_anomalies()
        self._render_indicators()

    def _render_findings(self) -> None:
        table = self.query_one("#findings-table", DataTable)
        table.clear()
        query = self.active_query.casefold().strip()
        for index, item in enumerate(self.analysis.findings):
            searchable = " ".join((item.severity, item.category, item.title, item.evidence)).casefold()
            if query and query not in searchable:
                continue
            severity = Text(item.severity, style=SEVERITY_COLORS.get(item.severity, "white"))
            table.add_row(severity, Text(item.category), Text(item.title), Text(item.evidence), Text(item.recommendation), key=str(index))

    def _render_incidents(self) -> None:
        table = self.query_one("#incidents-table", DataTable)
        table.clear()
        for item in self.analysis.incidents:
            table.add_row(Text(item.id), Text(item.severity, style=SEVERITY_COLORS.get(item.severity, "white")), Text(item.category), str(item.count), Text(item.title))

    def _render_anomalies(self) -> None:
        table = self.query_one("#anomalies-table", DataTable)
        table.clear()
        for item in self.analysis.anomalies:
            table.add_row(f"{item.score:.1f}", Text(item.key), Text(item.reason))

    def _render_indicators(self) -> None:
        table = self.query_one("#indicators-table", DataTable)
        table.clear()
        for kind, values in self.analysis.indicators.items():
            for value in values:
                table.add_row(Text(kind.upper()), Text(value))

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "filter":
            self.active_query = event.value
            self._render_findings()

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.data_table.id != "findings-table":
            return
        try:
            item = self.analysis.findings[int(event.row_key.value)]
        except (TypeError, ValueError, IndexError):
            return
        detail = Text()
        detail.append(f"{item.severity}  ", style=SEVERITY_COLORS.get(item.severity, "white"))
        detail.append(f"{item.title}\n", style="bold white")
        detail.append("Evidence: ", style="bold #93c5fd")
        detail.append(f"{item.evidence}\n")
        detail.append("Recommended response: ", style="bold #22d3ee")
        detail.append(item.recommendation)
        self.query_one("#finding-detail", Static).update(detail)

    def action_clear_filter(self) -> None:
        filter_input = self.query_one("#filter", Input)
        filter_input.value = ""
        self.active_query = ""
        self._render_findings()
        self.query_one("#findings-table", DataTable).focus()

    def action_refresh_analysis(self) -> None:
        self.analysis = build_dashboard_analysis(self.path)
        self._render_analysis()
        self.notify("Analysis refreshed", title="AegisLog AI")

    def _live_refresh(self) -> None:
        if self.live_enabled:
            self.analysis = build_dashboard_analysis(self.path)
            self._render_analysis()

    def action_toggle_live(self) -> None:
        self.live_enabled = not self.live_enabled
        if self.live_timer is not None:
            self.live_timer.resume() if self.live_enabled else self.live_timer.pause()
        self._render_analysis()
        self.notify("Live monitoring enabled" if self.live_enabled else "Live monitoring paused", title="AegisLog AI")

    def action_export_report(self) -> None:
        output = self.path.with_name(f"{self.path.stem}-aegislog-dashboard.json")
        payload = {
            "schema_version": 1,
            "source": str(self.analysis.path),
            "analyzed_at": self.analysis.analyzed_at,
            "line_count": self.analysis.line_count,
            "findings": [asdict(item) for item in self.analysis.findings],
            "incidents": [asdict(item) for item in self.analysis.incidents],
            "anomalies": [asdict(item) for item in self.analysis.anomalies],
            "indicators": self.analysis.indicators,
        }
        output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        self.notify(f"Report exported to {output.name}", title="Export complete")


def run_dashboard(path: Path) -> None:
    AegisDashboard(path).run()
