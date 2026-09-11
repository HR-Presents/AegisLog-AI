from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from html import escape
from pathlib import Path

from . import __version__
from .dashboard import DashboardData

_SEVERITY_RANK = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "INFO": 0}


def _safe_name(value: str) -> str:
    cleaned = "".join(char if char.isalnum() or char in {"-", "_"} else "-" for char in value)
    return cleaned.strip("-") or "analysis"


def _source_name(source: str) -> str:
    normalized = source.replace("\\", "/").rstrip("/")
    return normalized.rsplit("/", 1)[-1] if normalized else source


def _risk(data: DashboardData) -> tuple[str, str]:
    severities = {item.severity for item in data.findings}
    severities.update(item.severity for item in data.incidents)
    if "CRITICAL" in severities:
        return "Critical Risk", "danger"
    if "HIGH" in severities:
        return "High Risk", "danger"
    if "MEDIUM" in severities:
        return "Review Required", "warning"
    return "Low Risk", "good"


def _pct(value: int, total: int) -> float:
    return 0.0 if total <= 0 else round((value / total) * 100.0, 1)


def _finding_rows(data: DashboardData) -> str:
    ordered = sorted(data.findings, key=lambda item: (-_SEVERITY_RANK.get(item.severity, 0), item.category, item.title))
    if not ordered:
        return '<div class="empty">No rule-backed findings were retained for this input.</div>'
    blocks: list[str] = []
    for index, item in enumerate(ordered, start=1):
        css = "danger" if item.severity in {"CRITICAL", "HIGH"} else "warning" if item.severity == "MEDIUM" else "good"
        blocks.append(f'''<article class="finding-card">
<div class="finding-head"><span class="finding-id">F-{index:03d}</span><strong>{escape(item.title)}</strong><span class="pill {css}">{escape(item.severity)}</span></div>
<div class="finding-grid"><div><small>Category</small><b>{escape(item.category)}</b></div><div><small>Evidence</small><code>{escape(item.evidence)}</code></div><div><small>Recommendation</small><p>{escape(item.recommendation)}</p></div></div>
</article>''')
    return "".join(blocks)


def _incident_rows(data: DashboardData) -> str:
    if not data.incidents:
        return '<tr><td colspan="6"><div class="empty">No correlated incidents were retained.</div></td></tr>'
    rows: list[str] = []
    for item in data.incidents:
        css = "danger" if item.severity in {"CRITICAL", "HIGH"} else "warning" if item.severity == "MEDIUM" else "good"
        evidence = "<br>".join(f"<code>{escape(line)}</code>" for line in item.evidence)
        rows.append(f"<tr><td><b>INC-{escape(item.id.upper()[:8])}</b></td><td><span class='pill {css}'>{escape(item.severity)}</span></td><td>{escape(item.category)}</td><td>{escape(item.title)}</td><td>{item.count}</td><td>{evidence}</td></tr>")
    return "".join(rows)


def _anomaly_rows(data: DashboardData) -> str:
    if not data.anomalies:
        return '<tr><td colspan="3"><div class="empty">No anomaly classes met the retained scoring threshold.</div></td></tr>'
    return "".join(f"<tr><td><b>{escape(item.key)}</b></td><td>{item.score:.1f}</td><td>{escape(item.reason)}</td></tr>" for item in data.anomalies)


def _bar_rows(values: dict[str, int], *, semantic: bool = False, limit: int = 8) -> str:
    ordered = sorted(values.items(), key=lambda pair: (-pair[1], pair[0]))[:limit]
    if not ordered:
        return '<div class="empty">No data available.</div>'
    maximum = max(value for _, value in ordered) or 1
    palette = ["teal", "violet", "sky", "amber", "coral", "mint"]
    rows: list[str] = []
    for index, (label, value) in enumerate(ordered):
        if semantic:
            key = label.upper()
            tone = "coral" if key in {"CRITICAL", "HIGH"} else "amber" if key == "MEDIUM" else "sky" if key == "LOW" else "mint"
        else:
            tone = palette[index % len(palette)]
        width = max(3.0, (value / maximum) * 100.0)
        rows.append(f'<div class="bar-row"><span>{escape(str(label).upper())}</span><div class="bar-track"><i class="{tone}" style="width:{width:.1f}%"></i></div><b>{value}</b></div>')
    return "".join(rows)


def build_html_report(data: DashboardData) -> str:
    generated = datetime.now(timezone.utc).strftime("%d %B %Y, %H:%M UTC")
    source_name = _source_name(data.source)
    risk_label, risk_css = _risk(data)
    severity_counts = Counter(item.severity for item in data.findings)
    total_findings = len(data.findings)
    elevated = sum(count for severity, count in severity_counts.items() if _SEVERITY_RANK.get(severity, 0) >= 2)
    elevated_share = _pct(elevated, total_findings)
    correlated_findings = sum(item.count for item in data.incidents)
    correlated_share = _pct(correlated_findings, total_findings)
    top_service, top_service_count = max(data.services.items(), key=lambda pair: pair[1], default=("none", 0))
    top_incident = data.incidents[0] if data.incidents else None
    top_finding = sorted(data.findings, key=lambda item: -_SEVERITY_RANK.get(item.severity, 0))[0] if data.findings else None
    primary = top_incident.title if top_incident else top_finding.title if top_finding else "No elevated investigation target"
    recommendation = top_finding.recommendation if top_finding else "Preserve telemetry and review coverage if operational context requires it."
    severity_html = _bar_rows(dict(severity_counts), semantic=True)
    service_html = _bar_rows(data.services)
    category_html = _bar_rows(data.categories)
    level_html = _bar_rows(data.levels)
    raw_preview = "\n".join(data.raw_lines[:120]) if data.raw_lines else "No raw preview retained."

    style = r'''
:root{--primary:#16a6a1;--primary-dark:#0d7377;--violet:#7c6fd0;--sky:#3b82c4;--amber:#d99932;--coral:#d85f68;--mint:#3f9e79;--soft:#eaf7f6;--violet-soft:#f0edff;--sky-soft:#eaf4ff;--dark:#132233;--muted:#6b7888;--border:#dbe4ea;--surface:#fff;--background:#f4f7f9}
*{box-sizing:border-box}body{margin:0;font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif;background:var(--background);color:var(--dark);line-height:1.6}a{color:var(--primary-dark);text-decoration:none}.report{max-width:1120px;margin:32px auto;padding:0 24px 40px}.cover{min-height:690px;display:flex;flex-direction:column;justify-content:space-between;background:linear-gradient(145deg,#142d39 0%,#176f73 45%,#596bb3 72%,#7964b6 100%);color:#fff;border-radius:22px;padding:46px;box-shadow:0 20px 56px rgba(19,34,51,.22)}.brand{font-size:30px;font-weight:850;letter-spacing:.04em}.brand small{display:block;font-size:10px;letter-spacing:.18em;opacity:.8;margin-top:3px}.cover h1{margin:0 0 12px;font-size:48px;line-height:1.08}.cover-subtitle{font-size:20px;opacity:.9;max-width:720px}.cover-meta{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;margin-top:30px}.cover-meta div{padding:16px;border:1px solid rgba(255,255,255,.22);border-radius:13px;background:rgba(255,255,255,.09)}.cover-meta small{display:block;opacity:.72;margin-bottom:3px}.confidential{font-size:12px;opacity:.75}.actions{display:flex;justify-content:flex-end;gap:10px;margin:18px 0}.button{border:0;border-radius:10px;padding:11px 18px;font-weight:700;cursor:pointer}.button-primary{background:var(--primary);color:#fff}.button-secondary{background:#fff;color:var(--dark);border:1px solid var(--border)}.grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px;margin:22px 0}.metric,.card{background:var(--surface);border:1px solid var(--border);border-radius:16px;box-shadow:0 8px 24px rgba(15,23,42,.05)}.metric{padding:20px;border-top:4px solid var(--primary)}.metric.violet{border-top-color:var(--violet)}.metric.amber{border-top-color:var(--amber)}.metric.coral{border-top-color:var(--coral)}.metric-label{color:var(--muted);font-size:13px;margin-bottom:8px}.metric-value{font-size:27px;font-weight:800}.card{padding:26px;margin-top:18px}.card h2{margin:0 0 18px;font-size:22px}.card h3{margin:22px 0 10px;font-size:17px}.section-kicker{color:var(--primary-dark);font-size:12px;font-weight:800;letter-spacing:.12em;text-transform:uppercase}.table{width:100%;border-collapse:collapse}.table th,.table td{padding:12px 10px;border-bottom:1px solid var(--border);text-align:left;vertical-align:top}.table th{color:var(--muted);font-size:13px;font-weight:600}.risk,.pill{display:inline-flex;padding:6px 11px;border-radius:999px;font-size:12px;font-weight:800}.danger{color:#991b1b;background:#fee2e2}.warning{color:#92400e;background:#fef3c7}.good{color:#166534;background:#dcfce7}.summary{background:linear-gradient(90deg,var(--soft),var(--violet-soft));border-left:4px solid var(--primary);padding:18px;border-radius:10px}.health-panel{display:flex;justify-content:space-between;gap:20px;align-items:center;padding:18px;border-radius:12px;background:#f8fafc;border:1px solid var(--border)}.toc{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px 28px;padding:0;list-style:none}.toc li{border-bottom:1px dashed var(--border);padding:8px 0}.chart-grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}.chart-card{padding:18px;border:1px solid var(--border);border-radius:14px;background:#fbfcfd}.bar-row{display:grid;grid-template-columns:120px 1fr 46px;gap:10px;align-items:center;margin:11px 0;font-size:12px}.bar-track{height:10px;border-radius:999px;background:#edf1f4;overflow:hidden}.bar-track i{height:100%;display:block;border-radius:999px}.bar-track .teal{background:var(--primary)}.bar-track .violet{background:var(--violet)}.bar-track .sky{background:var(--sky)}.bar-track .amber{background:var(--amber)}.bar-track .coral{background:var(--coral)}.bar-track .mint{background:var(--mint)}.finding-card{border:1px solid var(--border);border-radius:14px;overflow:hidden;margin:14px 0}.finding-head{display:grid;grid-template-columns:auto 1fr auto;gap:12px;align-items:center;padding:14px 16px;background:#f8fafc;border-bottom:1px solid var(--border)}.finding-id{font:700 11px Consolas,monospace;color:var(--violet)}.finding-grid{display:grid;grid-template-columns:.6fr 1.5fr 1.2fr}.finding-grid>div{padding:16px;border-right:1px solid var(--border)}.finding-grid>div:last-child{border-right:0}.finding-grid small{display:block;color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.08em;margin-bottom:7px}.finding-grid code{font:12px/1.55 Consolas,monospace;color:#243447;white-space:pre-wrap;word-break:break-word}.finding-grid p{margin:0}.output{margin:0;padding:18px;border-radius:12px;background:#14202c;color:#dce8f4;white-space:pre-wrap;word-break:break-word;max-height:520px;overflow:auto;font:12px/1.65 Consolas,monospace}.empty{padding:18px;border:1px dashed var(--border);border-radius:12px;color:var(--muted);background:#fbfcfd}.footer{color:var(--muted);font-size:12px;text-align:center;margin-top:26px}.page-break{break-before:page;page-break-before:always}.mini-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}.mini-card{padding:16px;border-radius:14px;background:linear-gradient(145deg,var(--soft),#fff);border:1px solid var(--border)}.mini-card:nth-child(2){background:linear-gradient(145deg,var(--violet-soft),#fff)}.mini-card:nth-child(3){background:linear-gradient(145deg,var(--sky-soft),#fff)}.mini-card strong{font-size:26px;display:block}.mini-card span{font-size:12px;color:var(--muted)}
@media(max-width:820px){.grid,.chart-grid,.finding-grid,.mini-grid{grid-template-columns:1fr 1fr}.cover{min-height:auto}.cover-meta,.toc{grid-template-columns:1fr}.health-panel{align-items:flex-start;flex-direction:column}.finding-grid>div{border-right:0;border-bottom:1px solid var(--border)}}@media(max-width:520px){.report{padding:0 12px 24px;margin-top:12px}.cover{padding:28px}.cover h1{font-size:34px}.grid,.chart-grid,.mini-grid,.finding-grid{grid-template-columns:1fr}.table th,.table td{display:block;width:100%}}@media print{@page{size:A4;margin:14mm}body{background:#fff;print-color-adjust:exact;-webkit-print-color-adjust:exact}.report{max-width:none;margin:0;padding:0}.cover{min-height:252mm;border-radius:0;box-shadow:none}.actions{display:none}.metric,.card{box-shadow:none}.output{max-height:none;overflow:visible;color:#111827;background:#f8fafc;border:1px solid var(--border)}}
'''

    return f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AegisLog Investigation Report - {escape(source_name)}</title><style>{style}</style></head><body><main class="report">
<section class="cover"><div class="brand">AEGISLOG<small>PRESENTED BY HR-PRESENTS</small></div><div><div class="section-kicker" style="color:#cfeeed">Defensive log investigation</div><h1>Investigation Report</h1><p class="cover-subtitle">Deterministic findings, correlated incidents, anomaly signals, and retained evidence for {escape(source_name)}.</p><div class="cover-meta"><div><small>Source</small><strong>{escape(source_name)}</strong></div><div><small>Posture</small><strong>{escape(risk_label)}</strong></div><div><small>Analysis mode</small><strong>Local / Read-only</strong></div><div><small>Generated</small><strong>{generated}</strong></div></div></div><div class="confidential">Local analysis output | Source unchanged | Deterministic investigation evidence</div></section>
<div class="actions"><button class="button button-secondary" onclick="window.scrollTo({{top:0,behavior:'smooth'}})">Back to cover</button><button class="button button-primary" onclick="window.print()">Print / Save as PDF</button></div>
<section class="card page-break"><div class="section-kicker">Document navigation</div><h2>Contents</h2><ol class="toc"><li><a href="#executive-summary">Executive Summary</a></li><li><a href="#score-overview">Investigation Overview</a></li><li><a href="#source-profile">Source Profile</a></li><li><a href="#visuals">Visual Analytics</a></li><li><a href="#incidents">Incidents</a></li><li><a href="#findings">Findings</a></li><li><a href="#anomalies">Anomalies</a></li><li><a href="#appendix">Appendix</a></li></ol></section>
<section class="card" id="executive-summary"><div class="section-kicker">Assessment</div><h2>Executive Summary</h2><div class="health-panel"><div><strong>Investigation Posture</strong><p style="margin:6px 0 0;color:var(--muted)">Evidence is prioritized by deterministic severity, correlation, and anomaly scoring.</p></div><span class="risk {risk_css}">{escape(risk_label)}</span></div><h3>Analysis summary</h3><div class="summary">AegisLog processed <strong>{data.lines:,}</strong> events and retained <strong>{len(data.findings)}</strong> findings, <strong>{len(data.incidents)}</strong> correlated incidents, and <strong>{len(data.anomalies)}</strong> anomaly signals. Primary investigation focus: <strong>{escape(primary)}</strong>.</div><h3>Recommended next step</h3><p>{escape(recommendation)}</p></section>
<section class="grid" id="score-overview"><article class="metric"><div class="metric-label">Events</div><div class="metric-value">{data.lines:,}</div></article><article class="metric violet"><div class="metric-label">Findings</div><div class="metric-value">{len(data.findings)}</div></article><article class="metric amber"><div class="metric-label">Incidents</div><div class="metric-value">{len(data.incidents)}</div></article><article class="metric coral"><div class="metric-label">Anomalies</div><div class="metric-value">{len(data.anomalies)}</div></article></section>
<section class="card" id="source-profile"><div class="section-kicker">Scope</div><h2>Source Profile</h2><table class="table"><tr><th>Source file</th><td>{escape(source_name)}</td></tr><tr><th>Source path</th><td>{escape(data.source)}</td></tr><tr><th>Events processed</th><td>{data.lines:,}</td></tr><tr><th>AegisLog version</th><td>{escape(__version__)}</td></tr><tr><th>Processing model</th><td>Deterministic local analysis</td></tr><tr><th>Source handling</th><td>Read-only; source unchanged</td></tr><tr><th>Generated</th><td>{generated}</td></tr></table></section>
<section class="card" id="visuals"><div class="section-kicker">Visual analytics</div><h2>Investigation Visuals</h2><div class="mini-grid"><div class="mini-card"><strong>{elevated_share:.1f}%</strong><span>Medium+ share of retained findings</span></div><div class="mini-card"><strong>{correlated_share:.1f}%</strong><span>Findings represented in incident groups</span></div><div class="mini-card"><strong>{top_service_count}</strong><span>Events from top service: {escape(str(top_service))}</span></div></div><div class="chart-grid" style="margin-top:18px"><div class="chart-card"><h3>Severity Distribution</h3>{severity_html}</div><div class="chart-card"><h3>Service Activity</h3>{service_html}</div><div class="chart-card"><h3>Finding Categories</h3>{category_html}</div><div class="chart-card"><h3>Log Level Mix</h3>{level_html}</div></div></section>
<section class="card" id="incidents"><div class="section-kicker">Correlation</div><h2>Incidents</h2><div style="overflow-x:auto"><table class="table"><thead><tr><th>ID</th><th>Severity</th><th>Category</th><th>Title</th><th>Count</th><th>Evidence</th></tr></thead><tbody>{_incident_rows(data)}</tbody></table></div></section>
<section class="card" id="findings"><div class="section-kicker">Deterministic detection</div><h2>Findings</h2>{_finding_rows(data)}</section>
<section class="card" id="anomalies"><div class="section-kicker">Behavioral signal</div><h2>Anomalies</h2><div style="overflow-x:auto"><table class="table"><thead><tr><th>Key</th><th>Score</th><th>Reason</th></tr></thead><tbody>{_anomaly_rows(data)}</tbody></table></div></section>
<section class="card" id="appendix"><div class="section-kicker">Appendix</div><h2>Retained Raw Preview</h2><pre class="output">{escape(raw_preview)}</pre><h3>Interpretation</h3><p>Findings are deterministic investigative signals, not proof of compromise. Correlated incidents group related retained findings; anomaly scores identify rare concerning event classes. Missing detections are not evidence that malicious activity is absent. Preserve original telemetry where incident-response, retention, or chain-of-custody procedures require it.</p></section>
<div class="footer">AEGISLOG v{escape(__version__)} | Presented by HR-Presents | Generated locally</div></main></body></html>'''


def write_html_report(data: DashboardData, output_dir: Path | None = None) -> Path:
    destination = output_dir or (Path.cwd() / "aegislog-reports")
    destination.mkdir(parents=True, exist_ok=True)
    stem = _safe_name(Path(_source_name(data.source)).stem)
    target = destination / f"{stem}-aegislog-report.html"
    target.write_text(build_html_report(data), encoding="utf-8")
    return target
