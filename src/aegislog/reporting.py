from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timezone
from html import escape
from pathlib import Path

from . import __version__
from .dashboard import DashboardData

_SEVERITY_RANK = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "INFO": 0}

_REPORT_STYLE = """
:root {
  --ink: #172033;
  --muted: #667085;
  --paper: #ffffff;
  --page: #eef2f6;
  --navy: #0c1b2d;
  --navy-2: #13263d;
  --line: #d8e0e8;
  --line-strong: #c5d0dc;
  --accent: #087d92;
  --accent-soft: #e8f6f8;
  --good: #137a50;
  --good-bg: #e8f7ef;
  --warn: #8a5a00;
  --warn-bg: #fff5d8;
  --danger: #b4233a;
  --danger-bg: #fdecef;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  background: var(--page);
  color: var(--ink);
  font: 14px/1.52 "Segoe UI", Arial, sans-serif;
}
a { color: inherit; }
.report {
  max-width: 1180px;
  margin: 24px auto;
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 14px;
  box-shadow: 0 18px 48px rgba(18, 38, 61, .10);
  overflow: hidden;
}
.masthead {
  background: var(--navy);
  color: #f8fbff;
  padding: 28px 34px 24px;
  border-bottom: 4px solid var(--accent);
}
.brand-row {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 26px;
}
.brand-mark {
  width: 44px;
  height: 48px;
  display: grid;
  place-items: center;
  border: 2px solid #7fd8e5;
  border-radius: 10px 10px 16px 16px;
  color: #b9f2fa;
  font-weight: 900;
  letter-spacing: .04em;
}
.brand-name {
  font-size: 23px;
  line-height: 1;
  font-weight: 900;
  letter-spacing: .08em;
}
.brand-sub {
  margin-top: 5px;
  color: #9ec4d1;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: .13em;
  text-transform: uppercase;
}
.title-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 24px;
  align-items: end;
}
.eyebrow {
  color: #83d8e6;
  font-size: 10px;
  font-weight: 900;
  letter-spacing: .14em;
  text-transform: uppercase;
}
h1 {
  margin: 5px 0 8px;
  font-size: clamp(30px, 4vw, 44px);
  line-height: 1.05;
  letter-spacing: -.025em;
}
.subtitle {
  max-width: 760px;
  margin: 0;
  color: #c9d8e3;
  font-size: 15px;
}
.posture {
  min-width: 132px;
  padding: 12px 14px;
  border: 1px solid rgba(255,255,255,.20);
  border-radius: 10px;
  text-align: right;
  background: rgba(255,255,255,.05);
}
.posture small {
  display: block;
  color: #9ec4d1;
  text-transform: uppercase;
  letter-spacing: .09em;
  font-size: 9px;
}
.posture strong { display: block; margin-top: 2px; font-size: 22px; }
.posture.good strong { color: #82e0b4; }
.posture.warning strong { color: #ffd978; }
.posture.danger strong { color: #ff9aaa; }

.meta {
  display: grid;
  grid-template-columns: 1.5fr .7fr 1fr 1fr;
  border-bottom: 1px solid var(--line);
  background: #f8fafc;
}
.meta div {
  min-width: 0;
  padding: 12px 18px;
  border-right: 1px solid var(--line);
}
.meta div:last-child { border-right: 0; }
.meta small {
  display: block;
  color: var(--muted);
  font-size: 9px;
  letter-spacing: .08em;
  text-transform: uppercase;
}
.meta strong {
  display: block;
  margin-top: 2px;
  overflow-wrap: anywhere;
  font-size: 12px;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  padding: 11px 18px;
  border-bottom: 1px solid var(--line);
  background: #fff;
}
.toolbar a {
  color: #344054;
  text-decoration: none;
  padding: 6px 8px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 700;
}
.toolbar a:hover { background: #f2f4f7; }
.toolbar .spacer { flex: 1; }
.toolbar button {
  border: 1px solid #0b7183;
  border-radius: 7px;
  background: var(--accent);
  color: white;
  padding: 7px 10px;
  font: inherit;
  font-size: 11px;
  font-weight: 800;
  cursor: pointer;
}

.content { padding: 22px 26px 34px; }
.metrics {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 10px;
  margin-bottom: 18px;
}
.metric {
  min-width: 0;
  padding: 14px 15px;
  border: 1px solid var(--line);
  border-radius: 9px;
  background: #fff;
}
.metric span {
  display: block;
  color: var(--muted);
  font-size: 9px;
  font-weight: 800;
  letter-spacing: .08em;
  text-transform: uppercase;
}
.metric strong {
  display: block;
  margin-top: 4px;
  font-size: 23px;
  line-height: 1.1;
  overflow-wrap: anywhere;
}
.metric.good strong { color: var(--good); }
.metric.warning strong { color: var(--warn); }
.metric.danger strong { color: var(--danger); }

.section {
  padding: 20px 0;
  border-top: 1px solid var(--line);
}
.section:first-of-type { border-top: 0; }
.section-head {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: baseline;
  margin-bottom: 12px;
}
.section-label {
  color: var(--accent);
  font-size: 9px;
  font-weight: 900;
  letter-spacing: .12em;
  text-transform: uppercase;
}
h2 {
  margin: 2px 0 0;
  font-size: 21px;
  letter-spacing: -.01em;
}
.section-note {
  max-width: 520px;
  color: var(--muted);
  font-size: 11px;
  text-align: right;
}
.summary {
  padding: 14px 16px;
  border-left: 4px solid var(--accent);
  background: #f7fafc;
  color: #344054;
}
.overview {
  display: grid;
  grid-template-columns: 1.1fr .9fr;
  gap: 14px;
  margin-top: 14px;
}
.severity-table,
.triage {
  border: 1px solid var(--line);
  border-radius: 9px;
  overflow: hidden;
}
.severity-row {
  display: grid;
  grid-template-columns: 90px 52px 1fr;
  align-items: center;
  gap: 10px;
  padding: 9px 11px;
  border-bottom: 1px solid var(--line);
}
.severity-row:last-child { border-bottom: 0; }
.severity-row small {
  color: var(--muted);
  font-weight: 800;
}
.track {
  height: 5px;
  background: #edf1f5;
  border-radius: 99px;
  overflow: hidden;
}
.track i {
  display: block;
  height: 100%;
  background: var(--accent);
  border-radius: inherit;
}
.triage-item {
  display: grid;
  grid-template-columns: 76px minmax(0,1fr);
  gap: 10px;
  padding: 10px 11px;
  border-bottom: 1px solid var(--line);
}
.triage-item:last-child { border-bottom: 0; }
.triage-item strong { font-size: 12px; }
.triage-item p { margin: 2px 0 0; color: #475467; font-size: 11px; }

.pill {
  display: inline-block;
  width: max-content;
  padding: 3px 7px;
  border-radius: 999px;
  font-size: 9px;
  font-weight: 900;
  letter-spacing: .04em;
}
.pill.good { color: var(--good); background: var(--good-bg); }
.pill.warning { color: var(--warn); background: var(--warn-bg); }
.pill.danger { color: var(--danger); background: var(--danger-bg); }
.pill.neutral { color: #475467; background: #eef2f6; }

.table-wrap {
  width: 100%;
  overflow-x: auto;
  border: 1px solid var(--line);
  border-radius: 9px;
}
table { width: 100%; border-collapse: collapse; }
th, td {
  padding: 9px 10px;
  border-bottom: 1px solid var(--line);
  text-align: left;
  vertical-align: top;
}
tr:last-child th, tr:last-child td { border-bottom: 0; }
thead th {
  background: #f7f9fb;
  color: #475467;
  font-size: 9px;
  font-weight: 900;
  letter-spacing: .06em;
  text-transform: uppercase;
}
td { overflow-wrap: anywhere; }
code {
  color: #0a6474;
  font-family: "Cascadia Mono", Consolas, monospace;
  font-size: 11px;
}
code.evidence {
  color: #344054;
  white-space: pre-wrap;
}
.evidence-list { margin: 0; padding-left: 17px; }
.evidence-list li + li { margin-top: 3px; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; }
.chip {
  border: 1px solid var(--line);
  border-radius: 999px;
  background: #f8fafc;
  padding: 4px 7px;
  color: #475467;
  font-size: 10px;
}
.empty { color: var(--muted); text-align: center; padding: 18px 8px; }
.note {
  margin: 0;
  color: #475467;
  font-size: 12px;
}
.footer {
  margin-top: 20px;
  padding-top: 12px;
  border-top: 1px solid var(--line);
  color: var(--muted);
  font-size: 10px;
  text-align: center;
}

@media (max-width: 900px) {
  .meta { grid-template-columns: repeat(2, 1fr); }
  .meta div:nth-child(2) { border-right: 0; }
  .meta div:nth-child(-n+2) { border-bottom: 1px solid var(--line); }
  .metrics { grid-template-columns: repeat(3, 1fr); }
  .overview { grid-template-columns: 1fr; }
}
@media (max-width: 620px) {
  body { background: #fff; }
  .report { margin: 0; border: 0; border-radius: 0; box-shadow: none; }
  .masthead { padding: 22px 18px; }
  .title-row { grid-template-columns: 1fr; align-items: start; }
  .posture { text-align: left; min-width: 0; }
  .content { padding: 16px; }
  .metrics, .meta { grid-template-columns: 1fr 1fr; }
  .section-head { display: block; }
  .section-note { margin-top: 5px; text-align: left; }
  .toolbar { overflow-x: auto; flex-wrap: nowrap; }
}
@media (max-width: 420px) {
  .metrics, .meta { grid-template-columns: 1fr; }
  .meta div { border-right: 0; border-bottom: 1px solid var(--line); }
  .severity-row { grid-template-columns: 76px 40px 1fr; }
  .triage-item { grid-template-columns: 1fr; }
}
@media print {
  @page { margin: 11mm; }
  body { background: #fff; color: #111827; font-size: 10px; }
  .report { max-width: none; margin: 0; border: 0; border-radius: 0; box-shadow: none; }
  .masthead {
    background: var(--navy);
    padding: 18px 20px;
    print-color-adjust: exact;
    -webkit-print-color-adjust: exact;
  }
  .brand-row { margin-bottom: 14px; }
  .toolbar { display: none; }
  .content { padding: 14px 0 0; }
  .metrics { grid-template-columns: repeat(5, 1fr); }
  .metric, .severity-table, .triage, .table-wrap { break-inside: avoid; }
  .section { break-inside: auto; padding: 14px 0; }
  thead { display: table-header-group; }
  tr { break-inside: avoid; }
  a { text-decoration: none; }
}
"""


def _safe_name(value: str) -> str:
    cleaned = "".join(char if char.isalnum() or char in {"-", "_"} else "-" for char in value)
    return cleaned.strip("-") or "analysis"


def _rows(items: Iterable[tuple[str, str]]) -> str:
    return "".join(
        f"<tr><th>{escape(label)}</th><td>{escape(value)}</td></tr>" for label, value in items
    )


def _risk(data: DashboardData) -> str:
    if data.severities.get("CRITICAL", 0):
        return "CRITICAL"
    if data.severities.get("HIGH", 0):
        return "HIGH"
    if data.severities.get("MEDIUM", 0):
        return "REVIEW"
    return "CLEAR"


def _risk_class(value: str) -> str:
    return {
        "CRITICAL": "danger",
        "HIGH": "danger",
        "REVIEW": "warning",
        "MEDIUM": "warning",
        "CLEAR": "good",
        "LOW": "neutral",
        "INFO": "neutral",
    }.get(value, "neutral")


def _metric(label: str, value: str, modifier: str = "") -> str:
    suffix = f" {modifier}" if modifier else ""
    return (
        f'<article class="metric{suffix}"><span>{escape(label)}</span>'
        f"<strong>{escape(value)}</strong></article>"
    )


def _severity_overview(data: DashboardData) -> str:
    total = max(sum(data.severities.values()), 1)
    rows = []
    for severity in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
        count = data.severities.get(severity, 0)
        percent = min(100.0, (count / total) * 100.0)
        rows.append(
            '<div class="severity-row">'
            f"<small>{severity}</small><strong>{count}</strong>"
            f'<div class="track"><i style="width:{percent:.1f}%"></i></div>'
            "</div>"
        )
    return "".join(rows)


def _triage_actions(data: DashboardData) -> str:
    ordered = sorted(
        data.findings,
        key=lambda item: (-_SEVERITY_RANK.get(item.severity, 0), item.category, item.title),
    )
    seen: set[str] = set()
    actions: list[str] = []
    for item in ordered:
        recommendation = item.recommendation.strip()
        if not recommendation or recommendation in seen:
            continue
        seen.add(recommendation)
        actions.append(
            '<div class="triage-item">'
            f'<span class="pill {_risk_class(item.severity)}">{escape(item.severity)}</span>'
            "<div>"
            f"<strong>{escape(item.title)}</strong>"
            f"<p>{escape(recommendation)}</p>"
            "</div></div>"
        )
        if len(actions) == 5:
            break
    if not actions:
        return '<div class="empty">No immediate rule-backed remediation items were generated.</div>'
    return "".join(actions)


def _telemetry_chips(values: dict[str, int]) -> str:
    if not values:
        return '<span class="chip">none</span>'
    return "".join(
        f'<span class="chip">{escape(str(key))} <strong>{count}</strong></span>'
        for key, count in sorted(values.items(), key=lambda pair: (-pair[1], pair[0]))
    )


def build_html_report(data: DashboardData) -> str:
    """Return a self-contained, local HTML report using retained analysis evidence only."""
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    risk = _risk(data)
    source_name = Path(data.source).name

    incidents = "".join(
        "<tr>"
        f"<td><code>INC-{escape(item.id.upper()[:8])}</code></td>"
        f'<td><span class="pill {_risk_class(item.severity)}">{escape(item.severity)}</span></td>'
        f"<td>{escape(item.category)}</td><td>{item.count}</td><td>{escape(item.title)}</td>"
        '<td><ul class="evidence-list">'
        + "".join(f'<li><code class="evidence">{escape(value)}</code></li>' for value in item.evidence)
        + "</ul></td></tr>"
        for item in data.incidents
    ) or '<tr><td colspan="6" class="empty">No correlated incidents were recorded.</td></tr>'

    findings = "".join(
        "<tr>"
        f'<td><span class="pill {_risk_class(item.severity)}">{escape(item.severity)}</span></td>'
        f"<td>{escape(item.category)}</td><td>{escape(item.title)}</td>"
        f'<td><code class="evidence">{escape(item.evidence)}</code></td>'
        f"<td>{escape(item.recommendation)}</td>"
        "</tr>"
        for item in sorted(
            data.findings,
            key=lambda finding: (
                -_SEVERITY_RANK.get(finding.severity, 0),
                finding.category,
                finding.title,
            ),
        )
    ) or '<tr><td colspan="5" class="empty">No rule-backed findings were recorded.</td></tr>'

    anomalies = "".join(
        "<tr>"
        f"<td><strong>{item.score:.1f}</strong></td>"
        f"<td><code>{escape(item.key)}</code></td><td>{escape(item.reason)}</td>"
        "</tr>"
        for item in data.anomalies
    ) or '<tr><td colspan="3" class="empty">No rare concerning event classes were recorded.</td></tr>'

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AegisLog Investigation Report - {escape(source_name)}</title>
<style>{_REPORT_STYLE}</style>
</head>
<body>
<main class="report">
<header class="masthead" id="cover">
  <div class="brand-row">
    <div class="brand-mark" aria-hidden="true">AL</div>
    <div>
      <div class="brand-name">AEGISLOG</div>
      <div class="brand-sub">Security operations / local-first</div>
    </div>
  </div>
  <div class="title-row">
    <div>
      <div class="eyebrow">Defensive investigation</div>
      <h1>Security Investigation Report</h1>
      <p class="subtitle">Analyst-ready summary of retained findings, incident correlation, anomaly signals, and recommended defensive actions for <strong>{escape(source_name)}</strong>.</p>
    </div>
    <div class="posture {_risk_class(risk)}">
      <small>Current posture</small>
      <strong>{escape(risk)}</strong>
    </div>
  </div>
</header>

<section class="meta" aria-label="Report metadata">
  <div><small>Source</small><strong>{escape(source_name)}</strong></div>
  <div><small>Version</small><strong>{escape(__version__)}</strong></div>
  <div><small>Generated</small><strong>{generated}</strong></div>
  <div><small>Processing</small><strong>LOCAL / READ-ONLY</strong></div>
</section>

<nav class="toolbar" aria-label="Report sections">
  <a href="#executive">Executive</a>
  <a href="#triage">Triage</a>
  <a href="#incidents">Incidents</a>
  <a href="#findings">Findings</a>
  <a href="#anomalies">Anomalies</a>
  <a href="#telemetry">Telemetry</a>
  <span class="spacer"></span>
  <span class="brand-sub">REMOTE AI NOT REQUIRED</span>
  <button type="button" onclick="window.print()">Print / Save PDF</button>
</nav>

<div class="content">
<section class="metrics" aria-label="Investigation metrics">
  {_metric("Events", f"{data.lines:,}")}
  {_metric("Findings", str(len(data.findings)))}
  {_metric("Incidents", str(len(data.incidents)))}
  {_metric("Anomalies", str(len(data.anomalies)))}
  {_metric("Posture", risk, _risk_class(risk))}
</section>

<section class="section" id="executive">
  <div class="section-head">
    <div><div class="section-label">Executive view</div><h2>Executive Summary</h2></div>
    <div class="section-note">Findings are investigative evidence and should be validated in operational context.</div>
  </div>
  <div class="summary">AegisLog analyzed <strong>{data.lines:,}</strong> event line(s) and retained <strong>{len(data.findings)}</strong> rule-backed finding(s), <strong>{len(data.incidents)}</strong> correlated incident(s), and <strong>{len(data.anomalies)}</strong> anomaly signal(s). Current defensive posture: <strong>{escape(risk)}</strong>.</div>
  <div class="overview">
    <div>
      <div class="section-label" style="margin-bottom:7px">Severity distribution</div>
      <div class="severity-table">{_severity_overview(data)}</div>
    </div>
    <div id="triage">
      <div class="section-label" style="margin-bottom:7px">Recommended Triage</div>
      <div class="triage">{_triage_actions(data)}</div>
    </div>
  </div>
</section>

<section class="section" id="incidents">
  <div class="section-head">
    <div><div class="section-label">Correlation</div><h2>Incident Queue</h2></div>
    <div class="section-note">Grouped signals that should be reviewed together.</div>
  </div>
  <div class="table-wrap"><table>
    <thead><tr><th>ID</th><th>Severity</th><th>Category</th><th>Signals</th><th>Summary</th><th>Evidence chain</th></tr></thead>
    <tbody>{incidents}</tbody>
  </table></div>
</section>

<section class="section" id="findings">
  <div class="section-head">
    <div><div class="section-label">Detection</div><h2>Findings and Recommendations</h2></div>
    <div class="section-note">Rule-backed detections ordered by severity.</div>
  </div>
  <div class="table-wrap"><table>
    <thead><tr><th>Severity</th><th>Category</th><th>Detection</th><th>Evidence</th><th>Recommended action</th></tr></thead>
    <tbody>{findings}</tbody>
  </table></div>
</section>

<section class="section" id="anomalies">
  <div class="section-head">
    <div><div class="section-label">Behavior</div><h2>Anomaly Signals</h2></div>
    <div class="section-note">Rare concerning event classes surfaced for analyst review.</div>
  </div>
  <div class="table-wrap"><table>
    <thead><tr><th>Score</th><th>Event class</th><th>Reason</th></tr></thead>
    <tbody>{anomalies}</tbody>
  </table></div>
</section>

<section class="section" id="telemetry">
  <div class="section-head">
    <div><div class="section-label">Telemetry</div><h2>Observed Distribution</h2></div>
    <div class="section-note">High-level distribution of parsed telemetry retained by the analysis.</div>
  </div>
  <div class="table-wrap"><table>
    <tr><th>Categories</th><td><div class="chips">{_telemetry_chips(data.categories)}</div></td></tr>
    <tr><th>Log levels</th><td><div class="chips">{_telemetry_chips(data.levels)}</div></td></tr>
    <tr><th>Services</th><td><div class="chips">{_telemetry_chips(data.services)}</div></td></tr>
  </table></div>
</section>

<section class="section">
  <div class="section-head">
    <div><div class="section-label">Scope</div><h2>Analysis Profile</h2></div>
    <div class="section-note">This report is generated locally from retained, derived evidence.</div>
  </div>
  <div class="table-wrap"><table>{_rows((
      ("Source path", data.source),
      ("Source file", source_name),
      ("Event lines", f"{data.lines:,}"),
      ("AegisLog version", __version__),
      ("Generated", generated),
      ("Processing", "Local deterministic detection, correlation, and anomaly scoring"),
      ("Source handling", "Read-only; source content is not modified"),
      ("Remote AI", "Not required for this report"),
  ))}</table></div>
  <p class="note" style="margin-top:12px">The report intentionally does not reproduce the complete raw source log. Missing detections do not prove malicious activity is absent. Preserve original telemetry separately when evidence retention, chain-of-custody, or incident-response procedures require it.</p>
</section>

<div class="footer">AEGISLOG v{escape(__version__)} / Defensive security analysis / Generated locally</div>
</div>
</main>
</body>
</html>"""


def write_html_report(data: DashboardData, output_dir: Path | None = None) -> Path:
    """Write a self-contained report and return its path."""
    destination = output_dir or (Path.cwd() / "aegislog-reports")
    destination.mkdir(parents=True, exist_ok=True)
    stem = _safe_name(Path(data.source).stem)
    target = destination / f"{stem}-aegislog-report.html"
    target.write_text(build_html_report(data), encoding="utf-8")
    return target
