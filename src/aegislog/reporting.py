from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from html import escape
from pathlib import Path

from . import __version__
from .dashboard import DashboardData

_SEVERITY_RANK = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "INFO": 0}

_REPORT_STYLE = """
:root {
  --ink:#172033; --ink-soft:#3b4658; --muted:#6b7280; --paper:#ffffff;
  --page:#eef2f6; --navy:#0b1728; --navy-2:#13253b; --line:#d8e0e8;
  --line-soft:#e9eef3; --accent:#0b7285; --accent-soft:#e8f5f7;
  --good:#176b4d; --good-bg:#eaf7f0; --warn:#8a5a00; --warn-bg:#fff4d6;
  --danger:#a92a3e; --danger-bg:#fdecef; --mono:#f6f8fa;
}
*{box-sizing:border-box} html{scroll-behavior:smooth}
body{margin:0;background:var(--page);color:var(--ink);font:15px/1.58 "Segoe UI",Arial,sans-serif}
.report{width:min(1180px,calc(100% - 40px));margin:28px auto;background:var(--paper);border:1px solid var(--line);box-shadow:0 20px 54px rgba(15,23,42,.08)}
.masthead{padding:30px 34px 28px;background:linear-gradient(135deg,var(--navy),var(--navy-2));color:#f8fbff;border-bottom:4px solid var(--accent)}
.brandline,.title-grid,.section-head,.decision-head{display:flex;align-items:center;justify-content:space-between;gap:20px}
.brandline{margin-bottom:26px}.brand{display:flex;align-items:center;gap:12px}.brand-mark{width:42px;height:46px;display:grid;place-items:center;border:1.5px solid #78cbd7;border-radius:10px;color:#b5edf3;font-size:11px;font-weight:900;letter-spacing:.08em}.brand-name{font-size:22px;line-height:1;font-weight:900;letter-spacing:.08em}.brand-sub,.classification,.eyebrow,.section-label,.cell-label,.metric span,.case-strip small,.decision-kicker{text-transform:uppercase;font-weight:800;letter-spacing:.11em}.brand-sub{margin-top:5px;color:#a7bdca;font-size:9px}.classification{color:#a9c1cf;font-size:9px;text-align:right}.title-grid{align-items:end}.eyebrow{color:#86d5df;font-size:9px;letter-spacing:.14em}h1{margin:7px 0 10px;font-size:clamp(32px,4vw,46px);line-height:1.04;letter-spacing:-.03em}.subtitle{max-width:760px;margin:0;color:#ced9e2;font-size:14px}.posture{min-width:165px;padding:14px 16px;border:1px solid rgba(255,255,255,.2);background:rgba(255,255,255,.05);text-align:right;border-radius:10px}.posture small{display:block;color:#a9c1cf;font-size:9px;text-transform:uppercase;font-weight:800}.posture strong{display:block;margin-top:3px;font-size:23px}.posture.good strong{color:#8cdfb7}.posture.warning strong{color:#ffd67f}.posture.danger strong{color:#ff9dae}
.case-strip{display:grid;grid-template-columns:1.25fr .8fr .95fr 1fr;background:#f8fafc;border-bottom:1px solid var(--line)}.case-strip>div{min-width:0;padding:13px 17px;border-right:1px solid var(--line)}.case-strip>div:last-child{border-right:0}.case-strip small{display:block;color:var(--muted);font-size:8px}.case-strip strong{display:block;margin-top:3px;font-size:12px;overflow-wrap:anywhere}
.toolbar{display:flex;align-items:center;gap:4px;min-height:48px;padding:8px 16px;position:sticky;top:0;z-index:5;background:rgba(255,255,255,.98);border-bottom:1px solid var(--line)}.toolbar a{padding:7px 9px;color:#475467;text-decoration:none;border-radius:6px;font-size:11px;font-weight:750}.toolbar a:hover{background:#f2f4f7}.toolbar .spacer{flex:1}.toolbar .local-note{margin-right:10px;color:var(--muted);font-size:9px;font-weight:800;letter-spacing:.06em;text-transform:uppercase}.toolbar button{border:1px solid #0b6878;background:var(--accent);color:#fff;padding:8px 12px;font:inherit;font-size:11px;font-weight:800;cursor:pointer;border-radius:6px}
.content{padding:26px 30px 36px}.metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin-bottom:28px}.metric{min-width:0;padding:16px 17px;border:1px solid var(--line);border-radius:10px;background:#fff;box-shadow:0 4px 14px rgba(15,23,42,.03)}.metric span{display:block;color:var(--muted);font-size:9px}.metric strong{display:block;margin-top:5px;font-size:26px;line-height:1.1}.metric.good{border-top:3px solid var(--good)}.metric.warning{border-top:3px solid #c18411}.metric.danger{border-top:3px solid var(--danger)}
.section{padding:30px 0;border-top:1px solid var(--line)}.section:first-of-type{border-top:0;padding-top:0}.section-head{align-items:flex-end;margin-bottom:18px}.section-label{color:var(--accent);font-size:9px;letter-spacing:.13em}h2{margin:3px 0 0;font-size:24px;letter-spacing:-.02em}.section-note{max-width:480px;color:var(--muted);font-size:11px;text-align:right}
.executive-grid{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(300px,.85fr);gap:16px}.assessment,.priority-box{border:1px solid var(--line);border-radius:12px;background:#fff;min-height:100%}.assessment{padding:20px 21px;border-top:4px solid var(--accent)}.assessment h3,.priority-box h3{margin:0 0 10px;font-size:15px}.assessment p{margin:0;color:var(--ink-soft)}.assessment .caveat{margin-top:13px;color:var(--muted);font-size:11px}
.decision{margin-top:16px;padding:16px 17px;border:1px solid var(--line);border-radius:10px;background:#f8fafc}.decision-head{align-items:flex-start}.decision-kicker{color:var(--muted);font-size:9px}.decision .lead{margin-top:6px;font-size:16px;font-weight:800}.decision .action{margin-top:7px;color:#475467;font-size:12px}.decision .meta{margin-top:8px;color:var(--muted);font-size:10px}
.priority-box h3{padding:17px 18px 4px}.triage-item{display:grid;grid-template-columns:76px minmax(0,1fr);gap:11px;padding:14px 17px;border-top:1px solid var(--line-soft)}.triage-item strong{display:block;font-size:12px}.triage-item p{margin:4px 0 0;color:#475467;font-size:11px}
.severity-block{margin-top:16px;border:1px solid var(--line);border-radius:9px;overflow:hidden}.severity-row{display:grid;grid-template-columns:86px 42px 1fr;align-items:center;gap:10px;padding:9px 11px;border-bottom:1px solid var(--line-soft)}.severity-row:last-child{border-bottom:0}.severity-row small{color:var(--muted);font-size:9px;font-weight:800}.track{height:6px;background:#edf1f5;overflow:hidden;border-radius:999px}.track i{display:block;height:100%;background:var(--accent)}.severity-row.danger .track i{background:var(--danger)}.severity-row.warning .track i{background:#c18411}.severity-row.neutral .track i{background:#7693a0}
.pill{display:inline-block;width:max-content;padding:4px 8px;border-radius:999px;font-size:8px;font-weight:900;letter-spacing:.05em}.pill.good{color:var(--good);background:var(--good-bg)}.pill.warning{color:var(--warn);background:var(--warn-bg)}.pill.danger{color:var(--danger);background:var(--danger-bg)}.pill.neutral{color:#475467;background:#eef2f6}
.record-list{display:grid;gap:14px}.record{border:1px solid var(--line);border-radius:12px;background:#fff;overflow:hidden;box-shadow:0 4px 12px rgba(15,23,42,.025)}.record-head{display:grid;grid-template-columns:auto minmax(0,1fr) auto;gap:12px;align-items:center;padding:14px 16px;background:#f8fafc;border-bottom:1px solid var(--line)}.record-id{color:var(--accent);font:800 10px "Cascadia Mono",Consolas,monospace}.record-title{min-width:0;font-size:14px;font-weight:800}.record-meta{color:var(--muted);font-size:10px;text-align:right}.record-body{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(240px,.65fr)}.record-cell{min-width:0;padding:16px}.record-cell+.record-cell{border-left:1px solid var(--line-soft);background:#fbfcfd}.cell-label{display:block;margin-bottom:7px;color:var(--muted);font-size:8px}
code{color:#0a6474;font:10.5px "Cascadia Mono",Consolas,monospace}.evidence{display:block;padding:11px 12px;background:var(--mono);border:1px solid var(--line-soft);border-radius:8px;color:#344054;white-space:pre-wrap;overflow-wrap:anywhere}.evidence-list{margin:0;padding:0;list-style:none}.evidence-list li+li{margin-top:8px}.action-text{margin:0;color:#344054;font-size:12px}
.table-wrap{width:100%;overflow-x:auto;border:1px solid var(--line);border-radius:10px}table{width:100%;border-collapse:collapse}th,td{padding:12px 13px;border-bottom:1px solid var(--line-soft);text-align:left;vertical-align:top}tr:last-child th,tr:last-child td{border-bottom:0}thead th{background:#f8fafc;color:#475467;font-size:9px;font-weight:900;letter-spacing:.07em;text-transform:uppercase}td{overflow-wrap:anywhere}.chips{display:flex;flex-wrap:wrap;gap:7px}.chip{border:1px solid var(--line);background:#f8fafc;border-radius:999px;padding:5px 9px;color:#475467;font-size:10px}
.telemetry-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.telemetry-card{border:1px solid var(--line);border-radius:10px;padding:14px 15px;background:#fff}.telemetry-card h3{margin:0 0 9px;font-size:12px}.method-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}.method-card{border:1px solid var(--line);border-radius:10px;padding:16px}.method-card h3{margin:0 0 7px;font-size:13px}.method-card p{margin:0;color:#475467;font-size:11px}.empty{padding:20px 14px;border:1px dashed var(--line);border-radius:10px;color:var(--muted);text-align:center;font-size:11px}.footer{margin-top:24px;padding-top:13px;border-top:1px solid var(--line);color:var(--muted);font-size:9px;text-align:center}
@media(max-width:900px){.case-strip{grid-template-columns:1fr 1fr}.case-strip>div:nth-child(2){border-right:0}.case-strip>div:nth-child(-n+2){border-bottom:1px solid var(--line)}.metrics{grid-template-columns:1fr 1fr}.executive-grid,.method-grid,.telemetry-grid{grid-template-columns:1fr}}
@media(max-width:680px){body{background:#fff}.report{width:100%;margin:0;border:0;box-shadow:none}.masthead{padding:24px 18px}.brandline,.title-grid,.section-head{align-items:flex-start}.title-grid,.section-head{display:block}.posture{min-width:0;margin-top:16px;text-align:left}.toolbar{overflow-x:auto}.toolbar .local-note{display:none}.content{padding:18px}.metrics{grid-template-columns:1fr 1fr}.record-body{grid-template-columns:1fr}.record-cell+.record-cell{border-left:0;border-top:1px solid var(--line-soft)}.section-note{margin-top:5px;text-align:left}}
@media(max-width:430px){.case-strip,.metrics{grid-template-columns:1fr}.case-strip>div,.metric{border-right:0;border-bottom:1px solid var(--line)}.record-head{grid-template-columns:1fr}.record-meta{text-align:left}.triage-item{grid-template-columns:1fr}}
@media print{@page{margin:11mm}body{background:#fff;color:#111827;font-size:9.5px}.report{width:100%;margin:0;border:0;box-shadow:none}.masthead{padding:16px 18px;print-color-adjust:exact;-webkit-print-color-adjust:exact}.brandline{margin-bottom:12px}.toolbar{display:none}.content{padding:12px 0 0}.metrics{grid-template-columns:repeat(4,1fr);gap:6px;margin-bottom:12px}.metric{padding:8px 9px;box-shadow:none}.metric strong{font-size:18px}.section{padding:12px 0}.record,.assessment,.priority-box,.decision,.severity-block,.method-card,.table-wrap,.telemetry-card{break-inside:avoid}.record{box-shadow:none}thead{display:table-header-group}tr{break-inside:avoid}}
"""


def _safe_name(value: str) -> str:
    cleaned = "".join(char if char.isalnum() or char in {"-", "_"} else "-" for char in value)
    return cleaned.strip("-") or "analysis"


def _severity_rank(value: str) -> int:
    return _SEVERITY_RANK.get(value.upper(), 0)


def _risk(data: DashboardData) -> str:
    severities = set(data.severities)
    severities.update(item.severity for item in data.incidents)
    if "CRITICAL" in severities: return "CRITICAL"
    if "HIGH" in severities: return "HIGH"
    if "MEDIUM" in severities: return "REVIEW"
    return "CLEAR"


def _risk_class(value: str) -> str:
    return {"CRITICAL":"danger","HIGH":"danger","REVIEW":"warning","MEDIUM":"warning","CLEAR":"good","LOW":"neutral","INFO":"neutral"}.get(value,"neutral")


def _disposition(risk: str) -> str:
    return {"CRITICAL":"IMMEDIATE REVIEW","HIGH":"IMMEDIATE REVIEW","REVIEW":"ANALYST REVIEW","CLEAR":"ROUTINE REVIEW"}[risk]


def _case_id(data: DashboardData) -> str:
    parts=[data.source,str(data.lines)]
    parts.extend(f"F|{i.severity}|{i.category}|{i.title}|{i.evidence}|{i.recommendation}" for i in data.findings)
    parts.extend(f"I|{i.id}|{i.severity}|{i.category}|{i.count}|{i.title}|{'|'.join(i.evidence)}" for i in data.incidents)
    parts.extend(f"A|{i.score:.6f}|{i.key}|{i.reason}" for i in data.anomalies)
    digest=hashlib.sha256("\x1e".join(parts).encode("utf-8",errors="replace")).hexdigest()[:10].upper()
    return f"AL-{digest}"


def _ordered_findings(data: DashboardData):
    return sorted(data.findings,key=lambda i:(-_severity_rank(i.severity),i.category,i.title))


def _ordered_incidents(data: DashboardData):
    return sorted(data.incidents,key=lambda i:(-_severity_rank(i.severity),-i.count,i.category,i.title))


def _assessment(data: DashboardData, risk: str) -> str:
    if risk=="CRITICAL": return "Critical defensive activity was retained. Prioritize correlated incident evidence and critical findings, then validate them against original telemetry and asset context."
    if risk=="HIGH": return "High-severity defensive signals were retained. Immediate analyst review is recommended before normal operational follow-up."
    if risk=="REVIEW": return "Medium-severity signals warrant analyst review. Validate source, identity, host, and network context before escalation."
    return "No critical, high, or medium rule-backed findings were retained. This does not prove malicious activity is absent; review coverage and preserve original telemetry as needed."


def _metric(label: str, value: str, modifier: str = "") -> str:
    suffix=f" {modifier}" if modifier else ""
    return f'<article class="metric{suffix}"><span>{escape(label)}</span><strong>{escape(value)}</strong></article>'


def _severity_overview(data: DashboardData) -> str:
    total=max(sum(data.severities.values()),1); rows=[]
    for severity in ("CRITICAL","HIGH","MEDIUM","LOW"):
        count=data.severities.get(severity,0); percent=min(100.0,(count/total)*100.0)
        rows.append(f'<div class="severity-row {_risk_class(severity)}"><small>{severity}</small><strong>{count}</strong><div class="track"><i style="width:{percent:.1f}%"></i></div></div>')
    return "".join(rows)


def _primary_decision(data: DashboardData) -> str:
    findings=_ordered_findings(data); incidents=_ordered_incidents(data)
    top_finding=findings[0] if findings else None; top_incident=incidents[0] if incidents else None
    if top_incident and (top_finding is None or _severity_rank(top_incident.severity)>=_severity_rank(top_finding.severity)):
        iid=f"INC-{top_incident.id.upper()[:8]}"
        return f'<div class="decision"><div class="decision-head"><span class="decision-kicker">What needs attention</span><span class="pill {_risk_class(top_incident.severity)}">{escape(top_incident.severity)}</span></div><div class="lead">{escape(iid)} · {escape(top_incident.title)}</div><div class="action">Review the correlated evidence chain and validate the affected source, identity, host, and network context before escalation.</div><div class="meta">{top_incident.count} correlated signal(s) · {escape(top_incident.category)}</div></div>'
    if top_finding:
        return f'<div class="decision"><div class="decision-head"><span class="decision-kicker">What needs attention</span><span class="pill {_risk_class(top_finding.severity)}">{escape(top_finding.severity)}</span></div><div class="lead">{escape(top_finding.title)}</div><div class="action">{escape(top_finding.recommendation)}</div><div class="meta">Rule-backed finding · {escape(top_finding.category)}</div></div>'
    return '<div class="decision"><div class="decision-head"><span class="decision-kicker">What needs attention</span><span class="pill good">CLEAR</span></div><div class="lead">No elevated rule-backed finding requires immediate action</div><div class="action">Review coverage and original telemetry before closing the investigation.</div></div>'


def _triage_actions(data: DashboardData) -> str:
    actions=[]; seen=set()
    for incident in _ordered_incidents(data)[:2]:
        key=f"incident:{incident.id}"; seen.add(key)
        actions.append(f'<div class="triage-item"><span class="pill {_risk_class(incident.severity)}">{escape(incident.severity)}</span><div><strong>INC-{escape(incident.id.upper()[:8])} · {escape(incident.title)}</strong><p>Validate the grouped evidence and surrounding source, identity, host, and network context.</p></div></div>')
    for item in _ordered_findings(data):
        rec=item.recommendation.strip()
        if not rec or rec in seen: continue
        seen.add(rec); actions.append(f'<div class="triage-item"><span class="pill {_risk_class(item.severity)}">{escape(item.severity)}</span><div><strong>{escape(item.title)}</strong><p>{escape(rec)}</p></div></div>')
        if len(actions)==4: break
    return "".join(actions[:4]) if actions else '<div class="empty">No immediate rule-backed remediation items were generated.</div>'


def _incident_records(data: DashboardData) -> str:
    records=[]
    for item in _ordered_incidents(data):
        evidence="".join(f'<li><code class="evidence">{escape(v)}</code></li>' for v in item.evidence)
        records.append(f'<article class="record"><div class="record-head"><span class="record-id">INC-{escape(item.id.upper()[:8])}</span><span class="record-title">{escape(item.title)}</span><span class="record-meta"><span class="pill {_risk_class(item.severity)}">{escape(item.severity)}</span> &nbsp; {escape(item.category)} · {item.count} signal(s)</span></div><div class="record-body"><div class="record-cell"><span class="cell-label">Evidence chain</span><ul class="evidence-list">{evidence}</ul></div><div class="record-cell"><span class="cell-label">Analyst handling</span><p class="action-text">Validate the grouped signals against original telemetry and surrounding host, identity, and network context. Escalate only when the evidence and operational context support that decision.</p></div></div></article>')
    return "".join(records) if records else '<div class="empty">No correlated incidents were recorded.</div>'


def _finding_records(data: DashboardData) -> str:
    records=[]
    for index,item in enumerate(_ordered_findings(data),start=1):
        records.append(f'<article class="record"><div class="record-head"><span class="record-id">F-{index:03d}</span><span class="record-title">{escape(item.title)}</span><span class="record-meta"><span class="pill {_risk_class(item.severity)}">{escape(item.severity)}</span> &nbsp; {escape(item.category)}</span></div><div class="record-body"><div class="record-cell"><span class="cell-label">Retained evidence</span><code class="evidence">{escape(item.evidence)}</code></div><div class="record-cell"><span class="cell-label">Recommended action</span><p class="action-text">{escape(item.recommendation)}</p></div></div></article>')
    return "".join(records) if records else '<div class="empty">No rule-backed findings were recorded.</div>'


def _anomaly_rows(data: DashboardData) -> str:
    rows="".join(f'<tr><td><strong>{i.score:.1f}</strong></td><td><code>{escape(i.key)}</code></td><td>{escape(i.reason)}</td></tr>' for i in data.anomalies)
    return rows or '<tr><td colspan="3" class="empty">No rare concerning event classes were recorded.</td></tr>'


def _telemetry_chips(values: dict[str,int]) -> str:
    if not values: return '<span class="chip">none</span>'
    return "".join(f'<span class="chip">{escape(str(k))} <strong>{v}</strong></span>' for k,v in sorted(values.items(),key=lambda p:(-p[1],p[0])))


def build_html_report(data: DashboardData) -> str:
    generated=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    source_name=Path(data.source).name; risk=_risk(data); case_id=_case_id(data)
    elevated=sum(c for s,c in data.severities.items() if _severity_rank(s)>=_severity_rank("MEDIUM"))
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><title>AegisLog Investigation Report - {escape(source_name)}</title><style>{_REPORT_STYLE}</style></head><body><main class="report">
<header class="masthead" id="cover"><div class="brandline"><div class="brand"><div class="brand-mark">AL</div><div><div class="brand-name">AEGISLOG</div><div class="brand-sub">Security operations · local-first</div></div></div><div class="classification">Defensive analysis<br>Investigation record</div></div><div class="title-grid"><div><div class="eyebrow">Case {escape(case_id)}</div><h1>Security Investigation Report</h1><p class="subtitle">Analyst-ready summary and retained evidence for <strong>{escape(source_name)}</strong>.</p></div><div class="posture {_risk_class(risk)}"><small>Current posture</small><strong>{escape(risk)}</strong></div></div></header>
<section class="case-strip"><div><small>Source</small><strong>{escape(source_name)}</strong></div><div><small>Case ID</small><strong>{escape(case_id)}</strong></div><div><small>Generated</small><strong>{generated}</strong></div><div><small>Processing</small><strong>LOCAL / READ-ONLY</strong></div></section>
<nav class="toolbar"><a href="#executive">Summary</a><a href="#incidents">Incidents</a><a href="#findings">Findings</a><a href="#telemetry">Telemetry</a><a href="#anomalies">Anomalies</a><a href="#method">Method</a><span class="spacer"></span><span class="local-note">REMOTE AI NOT REQUIRED</span><button type="button" onclick="window.print()">Print / Save PDF</button></nav>
<div class="content"><section class="metrics">{_metric("Events",f"{data.lines:,}")}{_metric("Findings",str(len(data.findings)))}{_metric("Incidents",str(len(data.incidents)))}{_metric("Disposition",_disposition(risk),_risk_class(risk))}</section>
<section class="section" id="executive"><div class="section-head"><div><div class="section-label">Executive summary</div><h2>What needs attention</h2></div><div class="section-note">Start here. Supporting evidence follows below.</div></div><div class="executive-grid"><div class="assessment"><h3>Assessment</h3><p>{escape(_assessment(data,risk))}</p>{_primary_decision(data)}<p class="caveat">Analyzed <strong>{data.lines:,}</strong> event line(s), retained <strong>{len(data.findings)}</strong> finding(s), <strong>{len(data.incidents)}</strong> incident(s), and <strong>{len(data.anomalies)}</strong> anomaly signal(s). Findings are investigative evidence, not proof of compromise.</p><div class="section-label" style="margin-top:16px;margin-bottom:8px">Severity distribution</div><div class="severity-block">{_severity_overview(data)}</div></div><div class="priority-box"><h3>Recommended triage</h3>{_triage_actions(data)}</div></div></section>
<section class="section" id="incidents"><div class="section-head"><div><div class="section-label">Correlation</div><h2>Incident Queue</h2></div><div class="section-note">Only genuinely correlated evidence should appear here.</div></div><div class="record-list">{_incident_records(data)}</div></section>
<section class="section" id="findings"><div class="section-head"><div><div class="section-label">Detection</div><h2>Findings</h2></div><div class="section-note">Rule-backed detections with retained evidence and next action.</div></div><div class="record-list">{_finding_records(data)}</div></section>
<section class="section" id="telemetry"><div class="section-head"><div><div class="section-label">Telemetry</div><h2>Observed Distribution</h2></div><div class="section-note">A compact view of the parsed source.</div></div><div class="telemetry-grid"><div class="telemetry-card"><h3>Categories</h3><div class="chips">{_telemetry_chips(data.categories)}</div></div><div class="telemetry-card"><h3>Log levels</h3><div class="chips">{_telemetry_chips(data.levels)}</div></div><div class="telemetry-card"><h3>Services</h3><div class="chips">{_telemetry_chips(data.services)}</div></div></div></section>
<section class="section" id="anomalies"><div class="section-head"><div><div class="section-label">Behavior</div><h2>Anomaly Signals</h2></div><div class="section-note">Supporting signals only; anomaly scores are not verdicts.</div></div><div class="table-wrap"><table><thead><tr><th>Score</th><th>Event class</th><th>Reason</th></tr></thead><tbody>{_anomaly_rows(data)}</tbody></table></div></section>
<section class="section" id="method"><div class="section-head"><div><div class="section-label">Method and scope</div><h2>Analysis Profile</h2></div><div class="section-note">How the report was produced and how to interpret it.</div></div><div class="method-grid"><div class="method-card"><h3>Processing model</h3><p>AegisLog v{escape(__version__)} performed local deterministic detection, incident correlation, and anomaly scoring. The source was handled read-only and remote AI was not required.</p></div><div class="method-card"><h3>Evidence limitations</h3><p>This report contains retained derived evidence rather than a complete copy of the raw log. Missing detections do not prove malicious activity is absent. Preserve original telemetry when incident-response, retention, or chain-of-custody procedures require it.</p></div></div><div class="table-wrap" style="margin-top:14px"><table><tr><th>Source path</th><td>{escape(data.source)}</td></tr><tr><th>Source file</th><td>{escape(source_name)}</td></tr><tr><th>Event lines</th><td>{data.lines:,}</td></tr><tr><th>AegisLog version</th><td>{escape(__version__)}</td></tr><tr><th>Generated</th><td>{generated}</td></tr><tr><th>Remote AI</th><td>Not required for this report</td></tr></table></div></section>
<div class="footer">AEGISLOG v{escape(__version__)} · {escape(case_id)} · Defensive security analysis · Generated locally</div></div></main></body></html>'''


def write_html_report(data: DashboardData, output_dir: Path | None = None) -> Path:
    destination=output_dir or (Path.cwd()/"aegislog-reports")
    destination.mkdir(parents=True,exist_ok=True)
    stem=_safe_name(Path(data.source).stem)
    target=destination/f"{stem}-aegislog-report.html"
    target.write_text(build_html_report(data),encoding="utf-8")
    return target
