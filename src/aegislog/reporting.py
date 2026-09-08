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
  --bg: #061019;
  --surface: #0b1722;
  --surface-2: #102231;
  --surface-3: #132b3d;
  --line: #23465d;
  --line-soft: #183247;
  --text: #e9f7ff;
  --muted: #91adbe;
  --cyan: #38e8ff;
  --blue: #5a8fff;
  --violet: #ba68ff;
  --green: #54f5a7;
  --yellow: #ffd65c;
  --red: #ff627b;
  --shadow: 0 22px 70px rgba(0, 0, 0, .34);
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  background:
    radial-gradient(circle at 86% -10%, rgba(90, 143, 255, .22), transparent 33rem),
    radial-gradient(circle at -5% 18%, rgba(56, 232, 255, .12), transparent 26rem),
    var(--bg);
  color: var(--text);
  font: 15px/1.58 "Segoe UI", Inter, Arial, sans-serif;
}
a { color: inherit; }
.report { max-width: 1380px; margin: 0 auto; padding: 24px 28px 54px; }
.cover {
  min-height: 560px;
  border: 1px solid #23627f;
  background:
    linear-gradient(140deg, rgba(56, 232, 255, .08), transparent 36%),
    linear-gradient(318deg, rgba(186, 104, 255, .16), transparent 34%),
    linear-gradient(145deg, #07131d 0%, #0b2130 60%, #121b32 100%);
  border-radius: 26px;
  padding: 44px;
  display: grid;
  grid-template-rows: auto 1fr auto;
  gap: 34px;
  box-shadow: var(--shadow);
}
.brand { display: flex; align-items: center; gap: 18px; }
.mark { width: 76px; height: 86px; filter: drop-shadow(0 0 18px rgba(56, 232, 255, .35)); }
.brand-name { font-size: 34px; line-height: 1; font-weight: 900; letter-spacing: .09em; }
.brand-sub, .eyebrow {
  color: var(--cyan);
  font-size: 11px;
  letter-spacing: .17em;
  font-weight: 900;
  text-transform: uppercase;
}
.cover-main { align-self: center; max-width: 980px; }
.cover h1 { font-size: clamp(40px, 6vw, 68px); line-height: 1.02; margin: 12px 0 18px; letter-spacing: -.035em; }
.lede { max-width: 880px; color: #c9deea; font-size: 19px; margin: 0; }
.risk-line { display: flex; flex-wrap: wrap; align-items: center; gap: 12px; margin-top: 24px; }
.risk-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border-radius: 999px;
  padding: 8px 13px;
  font-size: 12px;
  font-weight: 900;
  letter-spacing: .08em;
}
.risk-badge::before { content: ""; width: 8px; height: 8px; border-radius: 50%; background: currentColor; box-shadow: 0 0 14px currentColor; }
.risk-badge.good { color: var(--green); background: rgba(84, 245, 167, .10); border: 1px solid rgba(84, 245, 167, .35); }
.risk-badge.warning { color: var(--yellow); background: rgba(255, 214, 92, .10); border: 1px solid rgba(255, 214, 92, .35); }
.risk-badge.danger { color: var(--red); background: rgba(255, 98, 123, .10); border: 1px solid rgba(255, 98, 123, .35); }
.cover-note { color: var(--muted); font-size: 13px; }
.meta { display: grid; grid-template-columns: 1.45fr .65fr 1fr .75fr; gap: 12px; }
.meta div {
  min-width: 0;
  padding: 14px 15px;
  border: 1px solid rgba(255, 255, 255, .11);
  background: rgba(255, 255, 255, .045);
  border-radius: 13px;
}
.meta small { display: block; color: #9eb9c9; margin-bottom: 4px; text-transform: uppercase; letter-spacing: .07em; font-size: 10px; }
.meta strong { display: block; overflow-wrap: anywhere; }
.toolbar {
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 18px 0;
  padding: 10px;
  border: 1px solid var(--line-soft);
  border-radius: 14px;
  background: rgba(6, 16, 25, .91);
  backdrop-filter: blur(14px);
}
.toolbar .spacer { flex: 1; }
.toolbar a, .toolbar button {
  border: 1px solid #2a5770;
  background: #0f2231;
  color: var(--text);
  text-decoration: none;
  border-radius: 9px;
  padding: 9px 12px;
  font: inherit;
  font-size: 12px;
  font-weight: 800;
  cursor: pointer;
}
.toolbar .primary { background: linear-gradient(90deg, var(--cyan), var(--blue)); color: #031019; border: 0; }
.metrics { display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; margin: 18px 0; }
.metric, .card {
  border: 1px solid var(--line);
  background: linear-gradient(180deg, var(--surface-2), var(--surface));
  border-radius: 16px;
}
.metric { padding: 17px 18px; min-width: 0; }
.metric span { display: block; color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: .09em; }
.metric strong { display: block; margin-top: 3px; font-size: 27px; overflow-wrap: anywhere; }
.metric.good strong { color: var(--green); }
.metric.warning strong { color: var(--yellow); }
.metric.danger strong { color: var(--red); }
.card { padding: 24px; margin-top: 16px; box-shadow: 0 12px 34px rgba(0, 0, 0, .13); }
.kicker { color: var(--cyan); text-transform: uppercase; letter-spacing: .16em; font-size: 10px; font-weight: 900; }
h2 { margin: 4px 0 18px; font-size: 25px; letter-spacing: -.015em; }
.summary {
  padding: 18px 20px;
  border-left: 4px solid var(--cyan);
  background: linear-gradient(90deg, rgba(56, 232, 255, .09), rgba(90, 143, 255, .04));
  border-radius: 10px;
}
.severity-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 18px; }
.severity-item { padding: 13px; border: 1px solid var(--line-soft); border-radius: 11px; background: #091720; }
.severity-item small { display: block; color: var(--muted); text-transform: uppercase; letter-spacing: .08em; }
.severity-item strong { font-size: 22px; }
.bar { height: 5px; margin-top: 9px; background: #061019; border-radius: 999px; overflow: hidden; }
.bar i { display: block; height: 100%; border-radius: inherit; background: linear-gradient(90deg, var(--cyan), var(--blue)); }
.triage { display: grid; gap: 10px; }
.triage-item {
  display: grid;
  grid-template-columns: 92px minmax(0, 1fr);
  gap: 14px;
  padding: 14px;
  border: 1px solid var(--line-soft);
  background: #091720;
  border-radius: 12px;
}
.triage-item p { margin: 3px 0 0; color: #c6dbe6; }
.pill {
  display: inline-block;
  width: max-content;
  padding: 4px 9px;
  border-radius: 999px;
  font-size: 10px;
  font-weight: 900;
  letter-spacing: .05em;
}
.pill.good { color: #0c5a35; background: #b9ffda; }
.pill.warning { color: #654900; background: #ffeba7; }
.pill.danger { color: #790b20; background: #ffc2cc; }
.pill.neutral { color: #10394f; background: #c7eaf8; }
.table-wrap { width: 100%; overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 11px 10px; border-bottom: 1px solid #1a3548; text-align: left; vertical-align: top; }
thead th { position: sticky; top: 51px; z-index: 2; background: #102231; }
th { color: #a0bdcd; font-size: 11px; text-transform: uppercase; letter-spacing: .055em; }
td { overflow-wrap: anywhere; }
code { color: var(--cyan); font-family: "Cascadia Mono", Consolas, monospace; }
code.evidence { color: #cfe7f2; white-space: pre-wrap; }
.evidence-list { margin: 0; padding-left: 18px; }
.evidence-list li + li { margin-top: 4px; }
.chips { display: flex; flex-wrap: wrap; gap: 8px; }
.chip { border: 1px solid #274b62; background: #0a1b27; border-radius: 999px; padding: 6px 9px; color: #c8dee9; font-size: 12px; }
.empty { color: var(--muted); text-align: center; padding: 24px 10px; }
.note { color: #c3d9e4; }
.footer { margin-top: 26px; text-align: center; color: var(--muted); font-size: 11px; letter-spacing: .04em; }
@media (max-width: 1050px) {
  .metrics { grid-template-columns: repeat(3, 1fr); }
  .meta { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 720px) {
  .report { padding: 12px; }
  .cover { padding: 26px; min-height: auto; border-radius: 18px; }
  .brand-name { font-size: 28px; }
  .mark { width: 58px; height: 66px; }
  .metrics, .meta, .severity-grid { grid-template-columns: 1fr 1fr; }
  .toolbar { overflow-x: auto; }
  .triage-item { grid-template-columns: 1fr; }
  .card { padding: 18px; }
}
@media (max-width: 480px) {
  .metrics, .meta, .severity-grid { grid-template-columns: 1fr; }
}
@media print {
  @page { margin: 12mm; }
  body { background: #fff; color: #111; font-size: 11px; }
  .report { max-width: none; padding: 0; }
  .cover {
    min-height: 250mm;
    border-radius: 0;
    box-shadow: none;
    break-after: page;
    print-color-adjust: exact;
    -webkit-print-color-adjust: exact;
  }
  .toolbar { display: none; }
  .metrics { grid-template-columns: repeat(3, 1fr); }
  .metric, .card, .severity-item, .triage-item { background: #fff; color: #111; box-shadow: none; break-inside: avoid; }
  .summary { color: #111; background: #f2f8fb; }
  .note, .triage-item p, code.evidence { color: #222; }
  thead th { position: static; background: #f4f7f9; color: #444; }
  th { color: #555; }
  .table-wrap { overflow: visible; }
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
    blocks = []
    for severity in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
        count = data.severities.get(severity, 0)
        percent = min(100.0, (count / total) * 100.0)
        blocks.append(
            '<div class="severity-item">'
            f"<small>{severity}</small><strong>{count}</strong>"
            f'<div class="bar"><i style="width:{percent:.1f}%"></i></div>'
            "</div>"
        )
    return "".join(blocks)


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
        if len(actions) == 6:
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
<meta name="color-scheme" content="dark">
<title>AegisLog Investigation Report - {escape(source_name)}</title>
<style>{_REPORT_STYLE}</style>
</head>
<body>
<main class="report">
<section class="cover" id="cover">
  <div class="brand">
    <svg class="mark" viewBox="0 0 100 112" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="AegisLog shield">
      <defs><linearGradient id="a" x1="0" x2="1"><stop stop-color="#38e8ff"/><stop offset="1" stop-color="#ba68ff"/></linearGradient></defs>
      <path d="M50 4 91 19v32c0 28-17 47-41 57C26 98 9 79 9 51V19L50 4Z" fill="none" stroke="url(#a)" stroke-width="6"/>
      <path d="M50 24 70 74H58l-4-11H36l-4 11H20l22-50h8Zm0 18-9 13h18L50 42Z" fill="#e9f7ff"/>
    </svg>
    <div><div class="brand-name">AEGISLOG</div><div class="brand-sub">Security operations / local-first</div></div>
  </div>
  <div class="cover-main">
    <div class="eyebrow">Defensive investigation report</div>
    <h1>Security Investigation Report</h1>
    <p class="lede">A structured analyst view of retained evidence for <strong>{escape(source_name)}</strong>, covering rule-backed findings, incident correlation, anomaly signals, telemetry distribution, and remediation priorities.</p>
    <div class="risk-line">
      <span class="risk-badge {_risk_class(risk)}">POSTURE {escape(risk)}</span>
      <span class="cover-note">Findings are investigative evidence, not proof of compromise.</span>
    </div>
  </div>
  <div>
    <div class="meta">
      <div><small>Source</small><strong>{escape(source_name)}</strong></div>
      <div><small>Version</small><strong>{escape(__version__)}</strong></div>
      <div><small>Generated</small><strong>{generated}</strong></div>
      <div><small>Processing</small><strong>LOCAL / READ-ONLY</strong></div>
    </div>
    <div class="brand-sub" style="margin-top:16px">REMOTE AI NOT REQUIRED / SELF-CONTAINED REPORT</div>
  </div>
</section>

<nav class="toolbar" aria-label="Report sections">
  <a href="#executive">Executive</a>
  <a href="#triage">Triage</a>
  <a href="#incidents">Incidents</a>
  <a href="#findings">Findings</a>
  <a href="#anomalies">Anomalies</a>
  <a href="#telemetry">Telemetry</a>
  <span class="spacer"></span>
  <a href="#cover">Cover</a>
  <button class="primary" type="button" onclick="window.print()">Print / Save PDF</button>
</nav>

<section class="metrics" aria-label="Investigation metrics">
  {_metric("Events", f"{data.lines:,}")}
  {_metric("Findings", str(len(data.findings)))}
  {_metric("Incidents", str(len(data.incidents)))}
  {_metric("Anomalies", str(len(data.anomalies)))}
  {_metric("Critical / High", f"{data.severities.get('CRITICAL', 0)} / {data.severities.get('HIGH', 0)}", _risk_class(risk))}
  {_metric("Posture", risk, _risk_class(risk))}
</section>

<section class="card" id="executive">
  <div class="kicker">Executive view</div>
  <h2>Executive Summary</h2>
  <div class="summary">AegisLog analyzed <strong>{data.lines:,}</strong> event line(s) and retained <strong>{len(data.findings)}</strong> rule-backed finding(s), <strong>{len(data.incidents)}</strong> correlated incident(s), and <strong>{len(data.anomalies)}</strong> anomaly signal(s). The current defensive posture is <strong>{escape(risk)}</strong>. Validate important findings against source telemetry, asset context, identity context, and other defensive evidence before escalation.</div>
  <div class="severity-grid">{_severity_overview(data)}</div>
</section>

<section class="card" id="triage">
  <div class="kicker">Priorities</div>
  <h2>Recommended Triage</h2>
  <div class="triage">{_triage_actions(data)}</div>
</section>

<section class="card">
  <div class="kicker">Scope</div>
  <h2>Analysis Profile</h2>
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
</section>

<section class="card" id="incidents">
  <div class="kicker">Correlation</div>
  <h2>Incident Queue</h2>
  <div class="table-wrap"><table>
    <thead><tr><th>ID</th><th>Severity</th><th>Category</th><th>Signals</th><th>Summary</th><th>Evidence chain</th></tr></thead>
    <tbody>{incidents}</tbody>
  </table></div>
</section>

<section class="card" id="findings">
  <div class="kicker">Detection</div>
  <h2>Findings and Recommendations</h2>
  <div class="table-wrap"><table>
    <thead><tr><th>Severity</th><th>Category</th><th>Detection</th><th>Evidence</th><th>Recommended action</th></tr></thead>
    <tbody>{findings}</tbody>
  </table></div>
</section>

<section class="card" id="anomalies">
  <div class="kicker">Behavior</div>
  <h2>Anomaly Signals</h2>
  <div class="table-wrap"><table>
    <thead><tr><th>Score</th><th>Event class</th><th>Reason</th></tr></thead>
    <tbody>{anomalies}</tbody>
  </table></div>
</section>

<section class="card" id="telemetry">
  <div class="kicker">Telemetry</div>
  <h2>Observed Distribution</h2>
  <table>
    <tr><th>Categories</th><td><div class="chips">{_telemetry_chips(data.categories)}</div></td></tr>
    <tr><th>Log levels</th><td><div class="chips">{_telemetry_chips(data.levels)}</div></td></tr>
    <tr><th>Services</th><td><div class="chips">{_telemetry_chips(data.services)}</div></td></tr>
  </table>
</section>

<section class="card">
  <div class="kicker">Interpretation</div>
  <h2>Analyst Notes</h2>
  <p class="note">This report contains the retained, derived evidence used by the terminal investigation dashboard. It intentionally does not reproduce the full raw source log. Missing detections do not prove that malicious activity is absent. Preserve original telemetry separately when evidence retention, chain-of-custody, or incident-response procedures require it.</p>
</section>

<div class="footer">AEGISLOG v{escape(__version__)} / Defensive security analysis / Generated locally / Remote AI not required</div>
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
