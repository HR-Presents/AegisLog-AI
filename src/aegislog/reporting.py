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
  --ink:#E7EDF6; --ink-soft:#BCC7D6; --muted:#718096; --paper:#101722;
  --page:#090D14; --navy:#0C111A; --navy-2:#121A27; --line:#243247;
  --line-soft:#1A2637; --accent:#4C8DFF; --accent-soft:#152748;
  --good:#4FAE86; --good-bg:#10271F; --warn:#D6A85F; --warn-bg:#2B2416;
  --danger:#D96B72; --danger-bg:#2A171C; --critical:#F07178; --mono:#0B111A;
  --surface:#111A27; --surface-2:#0D141F; --steel:#8FA7C7;
}
*{box-sizing:border-box} html{scroll-behavior:smooth;color-scheme:dark}
body{margin:0;background:radial-gradient(circle at top left,#111827 0,#090D14 42%,#070A10 100%);color:var(--ink);font:15px/1.58 "Segoe UI",Inter,Arial,sans-serif}
.report{width:min(1180px,calc(100% - 40px));margin:28px auto;background:linear-gradient(180deg,#0F1622,#0C121C);border:1px solid var(--line);box-shadow:0 24px 72px rgba(0,0,0,.38);border-radius:16px;overflow:hidden}
.masthead{padding:34px 36px 30px;background:linear-gradient(145deg,#0A1019 0%,#101A2A 62%,#0C1420 100%);color:#F4F7FB;border-bottom:1px solid #29405F;position:relative;overflow:hidden}.masthead:after{content:"";position:absolute;inset:auto -90px -130px auto;width:320px;height:320px;border-radius:50%;background:radial-gradient(circle,rgba(76,141,255,.14),rgba(76,141,255,0) 68%);pointer-events:none}
.brandline,.title-grid,.section-head,.decision-head{display:flex;align-items:center;justify-content:space-between;gap:20px}
.brandline{margin-bottom:30px}.brand{display:flex;align-items:center;gap:14px}.brand-mark{width:46px;height:52px;display:grid;place-items:center}.brand-mark svg{display:block;width:46px;height:52px}.brand-name{font-size:24px;line-height:1;font-weight:900;letter-spacing:.14em}.brand-name span{color:var(--accent)}.brand-sub,.classification,.eyebrow,.section-label,.cell-label,.metric span,.case-strip small,.decision-kicker{text-transform:uppercase;font-weight:800;letter-spacing:.12em}.brand-sub{margin-top:6px;color:#8EA0B7;font-size:9px}.classification{color:#7D8CA1;font-size:9px;text-align:right}.title-grid{align-items:end}.eyebrow{color:#7FB0FF;font-size:9px;letter-spacing:.16em}h1{margin:8px 0 10px;font-size:clamp(34px,4.6vw,52px);line-height:1.02;letter-spacing:-.035em}.subtitle{max-width:760px;margin:0;color:#B8C4D3;font-size:14px}.posture{min-width:170px;padding:15px 17px;border:1px solid #2A3A50;background:rgba(16,23,34,.72);text-align:right;border-radius:10px;box-shadow:inset 0 1px rgba(255,255,255,.02)}.posture small{display:block;color:#7F8EA3;font-size:9px;text-transform:uppercase;font-weight:800}.posture strong{display:block;margin-top:3px;font-size:24px;letter-spacing:.02em}.posture.good strong{color:var(--good)}.posture.warning strong{color:var(--warn)}.posture.danger strong{color:var(--critical)}
.case-strip{display:grid;grid-template-columns:1.25fr .8fr .95fr 1fr;background:#0B111A;border-bottom:1px solid var(--line)}.case-strip>div{min-width:0;padding:13px 17px;border-right:1px solid var(--line-soft)}.case-strip>div:last-child{border-right:0}.case-strip small{display:block;color:#66758A;font-size:8px}.case-strip strong{display:block;margin-top:3px;font-size:12px;color:#C8D3E1;overflow-wrap:anywhere}
.toolbar{display:flex;align-items:center;gap:4px;min-height:48px;padding:8px 16px;position:sticky;top:0;z-index:5;background:rgba(9,13,20,.96);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}.toolbar a{padding:7px 9px;color:#8FA0B5;text-decoration:none;border-radius:6px;font-size:11px;font-weight:750}.toolbar a:hover{background:#152033;color:#DDE7F4}.toolbar .spacer{flex:1}.toolbar .local-note{margin-right:10px;color:#66758A;font-size:9px;font-weight:800;letter-spacing:.07em;text-transform:uppercase}.toolbar button{border:1px solid #315A9E;background:#1A3D72;color:#EDF4FF;padding:8px 12px;font:inherit;font-size:11px;font-weight:800;cursor:pointer;border-radius:6px}.toolbar button:hover{background:#224D8E}
.content{padding:28px 30px 38px}.metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin-bottom:30px}.metric{min-width:0;padding:17px 18px;border:1px solid var(--line);border-radius:10px;background:linear-gradient(180deg,#111A27,#0E1622);box-shadow:0 8px 22px rgba(0,0,0,.14)}.metric span{display:block;color:#73839A;font-size:9px}.metric strong{display:block;margin-top:6px;font-size:27px;line-height:1.1;color:#F1F5F9}.metric.good{border-top:2px solid var(--good)}.metric.warning{border-top:2px solid var(--warn)}.metric.danger{border-top:2px solid var(--danger)}
.section{padding:31px 0;border-top:1px solid var(--line-soft)}.section:first-of-type{border-top:0;padding-top:0}.section-head{align-items:flex-end;margin-bottom:18px}.section-label{color:#78A6D8;font-size:9px;letter-spacing:.14em}h2{margin:3px 0 0;font-size:25px;letter-spacing:-.02em;color:#F1F5F9}.section-note{max-width:480px;color:#718096;font-size:11px;text-align:right}
.executive-grid{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(300px,.85fr);gap:16px}.assessment,.priority-box{border:1px solid var(--line);border-radius:12px;background:linear-gradient(180deg,#111A27,#0D141F);min-height:100%}.assessment{padding:21px 22px;border-top:2px solid var(--accent)}.assessment h3,.priority-box h3{margin:0 0 10px;font-size:15px;color:#E7EDF6}.assessment p{margin:0;color:var(--ink-soft)}.assessment .caveat{margin-top:13px;color:#74849A;font-size:11px}
.decision{margin-top:16px;padding:16px 17px;border:1px solid #26374E;border-radius:10px;background:#0B121D}.decision-head{align-items:flex-start}.decision-kicker{color:#6E7D92;font-size:9px}.decision .lead{margin-top:6px;font-size:16px;font-weight:800;color:#F0F4FA}.decision .action{margin-top:7px;color:#AAB7C8;font-size:12px}.decision .meta{margin-top:8px;color:#68788E;font-size:10px}
.priority-box h3{padding:17px 18px 4px}.triage-item{display:grid;grid-template-columns:76px minmax(0,1fr);gap:11px;padding:14px 17px;border-top:1px solid var(--line-soft)}.triage-item strong{display:block;font-size:12px;color:#DCE5F0}.triage-item p{margin:4px 0 0;color:#95A4B8;font-size:11px}
.severity-block{margin-top:16px;border:1px solid var(--line);border-radius:9px;overflow:hidden;background:#0B121B}.severity-row{display:grid;grid-template-columns:86px 42px 1fr;align-items:center;gap:10px;padding:9px 11px;border-bottom:1px solid var(--line-soft)}.severity-row:last-child{border-bottom:0}.severity-row small{color:#718096;font-size:9px;font-weight:800}.track{height:5px;background:#1B2738;overflow:hidden;border-radius:999px}.track i{display:block;height:100%;background:var(--accent)}.severity-row.danger .track i{background:var(--danger)}.severity-row.warning .track i{background:var(--warn)}.severity-row.neutral .track i{background:#547AA8}
.pill{display:inline-block;width:max-content;padding:4px 8px;border-radius:999px;font-size:8px;font-weight:900;letter-spacing:.06em;border:1px solid transparent}.pill.good{color:#7AC7A8;background:var(--good-bg);border-color:#214535}.pill.warning{color:#E1BC78;background:var(--warn-bg);border-color:#4A3D22}.pill.danger{color:#F28A91;background:var(--danger-bg);border-color:#4A272E}.pill.neutral{color:#9EB0C7;background:#172131;border-color:#26344A}
.record-list{display:grid;gap:14px}.record{border:1px solid var(--line);border-radius:12px;background:linear-gradient(180deg,#101925,#0D141F);overflow:hidden;box-shadow:0 7px 20px rgba(0,0,0,.12)}.record-head{display:grid;grid-template-columns:auto minmax(0,1fr) auto;gap:12px;align-items:center;padding:14px 16px;background:#0B121D;border-bottom:1px solid var(--line)}.record-id{color:#78A6D8;font:800 10px "Cascadia Mono",Consolas,monospace}.record-title{min-width:0;font-size:14px;font-weight:800;color:#E7EDF6}.record-meta{color:#718096;font-size:10px;text-align:right}.record-body{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(240px,.65fr)}.record-cell{min-width:0;padding:16px}.record-cell+.record-cell{border-left:1px solid var(--line-soft);background:#0B121B}.cell-label{display:block;margin-bottom:7px;color:#687990;font-size:8px}
code{color:#8EB9F0;font:10.5px "Cascadia Mono",Consolas,monospace}.evidence{display:block;padding:11px 12px;background:var(--mono);border:1px solid #202D3F;border-radius:8px;color:#C1CDDC;white-space:pre-wrap;overflow-wrap:anywhere}.evidence-list{margin:0;padding:0;list-style:none}.evidence-list li+li{margin-top:8px}.action-text{margin:0;color:#AAB7C8;font-size:12px}
.table-wrap{width:100%;overflow-x:auto;border:1px solid var(--line);border-radius:10px;background:#0D141F}table{width:100%;border-collapse:collapse}th,td{padding:12px 13px;border-bottom:1px solid var(--line-soft);text-align:left;vertical-align:top}tr:last-child th,tr:last-child td{border-bottom:0}thead th{background:#0A111A;color:#7F8FA5;font-size:9px;font-weight:900;letter-spacing:.07em;text-transform:uppercase}td{overflow-wrap:anywhere;color:#B7C3D2}.chips{display:flex;flex-wrap:wrap;gap:7px}.chip{border:1px solid #26354A;background:#111A27;border-radius:999px;padding:5px 9px;color:#9DB0C6;font-size:10px}.chip strong{color:#E5ECF5}
.telemetry-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.telemetry-card{border:1px solid var(--line);border-radius:10px;padding:14px 15px;background:#0F1723}.telemetry-card h3{margin:0 0 9px;font-size:12px;color:#DCE5F0}.method-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}.method-card{border:1px solid var(--line);border-radius:10px;padding:16px;background:#0F1723}.method-card h3{margin:0 0 7px;font-size:13px;color:#DCE5F0}.method-card p{margin:0;color:#98A7BA;font-size:11px}.empty{padding:20px 14px;border:1px dashed #314057;border-radius:10px;color:#718096;text-align:center;font-size:11px}.footer{margin-top:24px;padding-top:13px;border-top:1px solid var(--line);color:#65758A;font-size:9px;text-align:center}
@media(max-width:900px){.case-strip{grid-template-columns:1fr 1fr}.case-strip>div:nth-child(2){border-right:0}.case-strip>div:nth-child(-n+2){border-bottom:1px solid var(--line)}.metrics{grid-template-columns:1fr 1fr}.executive-grid,.method-grid,.telemetry-grid{grid-template-columns:1fr}}
@media(max-width:680px){body{background:#090D14}.report{width:100%;margin:0;border:0;border-radius:0;box-shadow:none}.masthead{padding:24px 18px}.brandline,.title-grid,.section-head{align-items:flex-start}.title-grid,.section-head{display:block}.posture{min-width:0;margin-top:16px;text-align:left}.toolbar{overflow-x:auto}.toolbar .local-note{display:none}.content{padding:18px}.metrics{grid-template-columns:1fr 1fr}.record-body{grid-template-columns:1fr}.record-cell+.record-cell{border-left:0;border-top:1px solid var(--line-soft)}.section-note{margin-top:5px;text-align:left}}
@media(max-width:430px){.case-strip,.metrics{grid-template-columns:1fr}.case-strip>div,.metric{border-right:0;border-bottom:1px solid var(--line)}.record-head{grid-template-columns:1fr}.record-meta{text-align:left}.triage-item{grid-template-columns:1fr}}
@media print{@page{margin:11mm}body{background:#fff;color:#111827;font-size:9.5px}.report{width:100%;margin:0;border:0;box-shadow:none;background:#fff}.masthead{padding:16px 18px;background:#111827!important;print-color-adjust:exact;-webkit-print-color-adjust:exact}.brandline{margin-bottom:12px}.toolbar{display:none}.content{padding:12px 0 0;background:#fff}.metrics{grid-template-columns:repeat(4,1fr);gap:6px;margin-bottom:12px}.metric{padding:8px 9px;box-shadow:none}.metric strong{font-size:18px}.section{padding:12px 0}.record,.assessment,.priority-box,.decision,.severity-block,.method-card,.table-wrap,.telemetry-card{break-inside:avoid}.record{box-shadow:none}thead{display:table-header-group}tr{break-inside:avoid}}
"""


def _safe_name(value: str) -> str:
    cleaned = "".join(char if char.isalnum() or char in {"-", "_"} else "-" for char in value)
    return cleaned.strip("-") or "analysis"


def _severity_rank(value: str) -> int:
    return _SEVERITY_RANK.get(value.upper(), 0)


def _risk(data: DashboardData) -> str:
    severities = set(data.severities)
    severities.update(item.severity for item in data.incidents)
    if "CRITICAL" in severities:
        return "CRITICAL"
    if "HIGH" in severities:
        return "HIGH"
    if "MEDIUM" in severities:
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


def _disposition(risk: str) -> str:
    return {
        "CRITICAL": "IMMEDIATE REVIEW",
        "HIGH": "IMMEDIATE REVIEW",
        "REVIEW": "ANALYST REVIEW",
        "CLEAR": "ROUTINE REVIEW",
    }[risk]


def _case_id(data: DashboardData) -> str:
    parts = [data.source, str(data.lines)]
    parts.extend(
        f"F|{i.severity}|{i.category}|{i.title}|{i.evidence}|{i.recommendation}"
        for i in data.findings
    )
    parts.extend(
        f"I|{i.id}|{i.severity}|{i.category}|{i.count}|{i.title}|{'|'.join(i.evidence)}"
        for i in data.incidents
    )
    parts.extend(f"A|{i.score:.6f}|{i.key}|{i.reason}" for i in data.anomalies)
    digest = hashlib.sha256("\x1e".join(parts).encode("utf-8", errors="replace")).hexdigest()[:10].upper()
    return f"AL-{digest}"


def _ordered_findings(data: DashboardData):
    return sorted(data.findings, key=lambda i: (-_severity_rank(i.severity), i.category, i.title))


def _ordered_incidents(data: DashboardData):
    return sorted(
        data.incidents,
        key=lambda i: (-_severity_rank(i.severity), -i.count, i.category, i.title),
    )


def _assessment(data: DashboardData, risk: str) -> str:
    if risk == "CRITICAL":
        return "Critical defensive activity was retained. Prioritize correlated incident evidence and critical findings, then validate them against original telemetry and asset context."
    if risk == "HIGH":
        return "High-severity defensive signals were retained. Immediate analyst review is recommended before normal operational follow-up."
    if risk == "REVIEW":
        return "Medium-severity signals warrant analyst review. Validate source, identity, host, and network context before escalation."
    return "No critical, high, or medium rule-backed findings were retained. This does not prove malicious activity is absent; review coverage and preserve original telemetry as needed."


def _metric(label: str, value: str, modifier: str = "") -> str:
    suffix = f" {modifier}" if modifier else ""
    return f'<article class="metric{suffix}"><span>{escape(label)}</span><strong>{escape(value)}</strong></article>'


def _severity_overview(data: DashboardData) -> str:
    total = max(sum(data.severities.values()), 1)
    rows = []
    for severity in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
        count = data.severities.get(severity, 0)
        percent = min(100.0, (count / total) * 100.0)
        rows.append(
            f'<div class="severity-row {_risk_class(severity)}"><small>{severity}</small><strong>{count}</strong><div class="track"><i style="width:{percent:.1f}%"></i></div></div>'
        )
    return "".join(rows)


def _primary_decision(data: DashboardData) -> str:
    findings = _ordered_findings(data)
    incidents = _ordered_incidents(data)
    top_finding = findings[0] if findings else None
    top_incident = incidents[0] if incidents else None
    if top_incident and (
        top_finding is None
        or _severity_rank(top_incident.severity) >= _severity_rank(top_finding.severity)
    ):
        iid = f"INC-{top_incident.id.upper()[:8]}"
        return f'<div class="decision"><div class="decision-head"><span class="decision-kicker">What needs attention</span><span class="pill {_risk_class(top_incident.severity)}">{escape(top_incident.severity)}</span></div><div class="lead">{escape(iid)} · {escape(top_incident.title)}</div><div class="action">Review the correlated evidence chain and validate the affected source, identity, host, and network context before escalation.</div><div class="meta">{top_incident.count} correlated signal(s) · {escape(top_incident.category)}</div></div>'
    if top_finding:
        return f'<div class="decision"><div class="decision-head"><span class="decision-kicker">What needs attention</span><span class="pill {_risk_class(top_finding.severity)}">{escape(top_finding.severity)}</span></div><div class="lead">{escape(top_finding.title)}</div><div class="action">{escape(top_finding.recommendation)}</div><div class="meta">Rule-backed finding · {escape(top_finding.category)}</div></div>'
    return '<div class="decision"><div class="decision-head"><span class="decision-kicker">What needs attention</span><span class="pill good">CLEAR</span></div><div class="lead">No elevated rule-backed finding requires immediate action</div><div class="action">Review coverage and original telemetry before closing the investigation.</div></div>'


def _triage_actions(data: DashboardData) -> str:
    actions = []
    seen = set()
    for incident in _ordered_incidents(data)[:2]:
        key = f"incident:{incident.id}"
        seen.add(key)
        actions.append(
            f'<div class="triage-item"><span class="pill {_risk_class(incident.severity)}">{escape(incident.severity)}</span><div><strong>INC-{escape(incident.id.upper()[:8])} · {escape(incident.title)}</strong><p>Validate the grouped evidence and surrounding source, identity, host, and network context.</p></div></div>'
        )
    for item in _ordered_findings(data):
        rec = item.recommendation.strip()
        if not rec or rec in seen:
            continue
        seen.add(rec)
        actions.append(
            f'<div class="triage-item"><span class="pill {_risk_class(item.severity)}">{escape(item.severity)}</span><div><strong>{escape(item.title)}</strong><p>{escape(rec)}</p></div></div>'
        )
        if len(actions) == 4:
            break
    return "".join(actions[:4]) if actions else '<div class="empty">No immediate rule-backed remediation items were generated.</div>'


def _incident_records(data: DashboardData) -> str:
    records = []
    for item in _ordered_incidents(data):
        evidence = "".join(
            f'<li><code class="evidence">{escape(v)}</code></li>' for v in item.evidence
        )
        records.append(
            f'<article class="record"><div class="record-head"><span class="record-id">INC-{escape(item.id.upper()[:8])}</span><span class="record-title">{escape(item.title)}</span><span class="record-meta"><span class="pill {_risk_class(item.severity)}">{escape(item.severity)}</span> &nbsp; {escape(item.category)} · {item.count} signal(s)</span></div><div class="record-body"><div class="record-cell"><span class="cell-label">Evidence chain</span><ul class="evidence-list">{evidence}</ul></div><div class="record-cell"><span class="cell-label">Analyst handling</span><p class="action-text">Validate the grouped signals against original telemetry and surrounding host, identity, and network context. Escalate only when the evidence and operational context support that decision.</p></div></div></article>'
        )
    return "".join(records) if records else '<div class="empty">No correlated incidents were recorded.</div>'


def _finding_records(data: DashboardData) -> str:
    records = []
    for index, item in enumerate(_ordered_findings(data), start=1):
        records.append(
            f'<article class="record"><div class="record-head"><span class="record-id">F-{index:03d}</span><span class="record-title">{escape(item.title)}</span><span class="record-meta"><span class="pill {_risk_class(item.severity)}">{escape(item.severity)}</span> &nbsp; {escape(item.category)}</span></div><div class="record-body"><div class="record-cell"><span class="cell-label">Retained evidence</span><code class="evidence">{escape(item.evidence)}</code></div><div class="record-cell"><span class="cell-label">Recommended action</span><p class="action-text">{escape(item.recommendation)}</p></div></div></article>'
        )
    return "".join(records) if records else '<div class="empty">No rule-backed findings were recorded.</div>'


def _anomaly_rows(data: DashboardData) -> str:
    rows = "".join(
        f'<tr><td><strong>{i.score:.1f}</strong></td><td><code>{escape(i.key)}</code></td><td>{escape(i.reason)}</td></tr>'
        for i in data.anomalies
    )
    return rows or '<tr><td colspan="3" class="empty">No rare concerning event classes were recorded.</td></tr>'


def _telemetry_chips(values: dict[str, int]) -> str:
    if not values:
        return '<span class="chip">none</span>'
    return "".join(
        f'<span class="chip">{escape(str(k))} <strong>{v}</strong></span>'
        for k, v in sorted(values.items(), key=lambda p: (-p[1], p[0]))
    )


def build_html_report(data: DashboardData) -> str:
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    source_name = Path(data.source).name
    risk = _risk(data)
    case_id = _case_id(data)
    brand_mark = '''<svg viewBox="0 0 46 52" aria-hidden="true"><path d="M23 2 42 9v14c0 13-7.3 22-19 27C11.3 45 4 36 4 23V9L23 2Z" fill="#0F1A29" stroke="#4C8DFF" stroke-width="2"/><path d="M12 27h7l3-8 4 13 3-6h5" fill="none" stroke="#8FB7FF" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>'''
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="dark"><title>AegisLog Investigation Report - {escape(source_name)}</title><style>{_REPORT_STYLE}</style></head><body><main class="report">
<header class="masthead" id="cover"><div class="brandline"><div class="brand"><div class="brand-mark">{brand_mark}</div><div><div class="brand-name">AEGIS<span>LOG</span></div><div class="brand-sub">Defensive log investigation</div></div></div><div class="classification">Local-first · read-only<br>Investigation record</div></div><div class="title-grid"><div><div class="eyebrow">Case {escape(case_id)}</div><h1>Security Investigation Report</h1><p class="subtitle">Analyst-ready summary and retained evidence for <strong>{escape(source_name)}</strong>.</p></div><div class="posture {_risk_class(risk)}"><small>Current posture</small><strong>{escape(risk)}</strong></div></div></header>
<section class="case-strip"><div><small>Source</small><strong>{escape(source_name)}</strong></div><div><small>Case ID</small><strong>{escape(case_id)}</strong></div><div><small>Generated</small><strong>{generated}</strong></div><div><small>Processing</small><strong>LOCAL / READ-ONLY</strong></div></section>
<nav class="toolbar"><a href="#executive">Summary</a><a href="#incidents">Incidents</a><a href="#findings">Findings</a><a href="#telemetry">Telemetry</a><a href="#anomalies">Anomalies</a><a href="#method">Method</a><span class="spacer"></span><span class="local-note">DETERMINISTIC ANALYSIS</span><button type="button" onclick="window.print()">Print / Save PDF</button></nav>
<div class="content"><section class="metrics">{_metric("Events", f"{data.lines:,}")}{_metric("Findings", str(len(data.findings)))}{_metric("Incidents", str(len(data.incidents)))}{_metric("Disposition", _disposition(risk), _risk_class(risk))}</section>
<section class="section" id="executive"><div class="section-head"><div><div class="section-label">Executive summary</div><h2>What needs attention</h2></div><div class="section-note">Start here. Supporting evidence follows below.</div></div><div class="executive-grid"><div class="assessment"><h3>Assessment</h3><p>{escape(_assessment(data, risk))}</p>{_primary_decision(data)}<p class="caveat">Analyzed <strong>{data.lines:,}</strong> event line(s), retained <strong>{len(data.findings)}</strong> finding(s), <strong>{len(data.incidents)}</strong> incident(s), and <strong>{len(data.anomalies)}</strong> anomaly signal(s). Findings are investigative evidence, not proof of compromise.</p><div class="section-label" style="margin-top:16px;margin-bottom:8px">Severity distribution</div><div class="severity-block">{_severity_overview(data)}</div></div><div class="priority-box"><h3>Recommended triage</h3>{_triage_actions(data)}</div></div></section>
<section class="section" id="incidents"><div class="section-head"><div><div class="section-label">Correlation</div><h2>Incident Queue</h2></div><div class="section-note">Only genuinely correlated evidence should appear here.</div></div><div class="record-list">{_incident_records(data)}</div></section>
<section class="section" id="findings"><div class="section-head"><div><div class="section-label">Detection</div><h2>Findings</h2></div><div class="section-note">Rule-backed detections with retained evidence and next action.</div></div><div class="record-list">{_finding_records(data)}</div></section>
<section class="section" id="telemetry"><div class="section-head"><div><div class="section-label">Telemetry</div><h2>Observed Distribution</h2></div><div class="section-note">A compact view of the parsed source.</div></div><div class="telemetry-grid"><div class="telemetry-card"><h3>Categories</h3><div class="chips">{_telemetry_chips(data.categories)}</div></div><div class="telemetry-card"><h3>Log levels</h3><div class="chips">{_telemetry_chips(data.levels)}</div></div><div class="telemetry-card"><h3>Services</h3><div class="chips">{_telemetry_chips(data.services)}</div></div></section>
<section class="section" id="anomalies"><div class="section-head"><div><div class="section-label">Behavior</div><h2>Anomaly Signals</h2></div><div class="section-note">Supporting signals only; anomaly scores are not verdicts.</div></div><div class="table-wrap"><table><thead><tr><th>Score</th><th>Event class</th><th>Reason</th></tr></thead><tbody>{_anomaly_rows(data)}</tbody></table></div></section>
<section class="section" id="method"><div class="section-head"><div><div class="section-label">Method and scope</div><h2>Analysis Profile</h2></div><div class="section-note">How the report was produced and how to interpret it.</div></div><div class="method-grid"><div class="method-card"><h3>Processing model</h3><p>AegisLog v{escape(__version__)} performed local deterministic detection, incident correlation, and anomaly scoring. The source was handled read-only.</p></div><div class="method-card"><h3>Evidence limitations</h3><p>This report contains retained derived evidence rather than a complete copy of the raw log. Missing detections do not prove malicious activity is absent. Preserve original telemetry when incident-response, retention, or chain-of-custody procedures require it.</p></div></div><div class="table-wrap" style="margin-top:14px"><table><tr><th>Source path</th><td>{escape(data.source)}</td></tr><tr><th>Source file</th><td>{escape(source_name)}</td></tr><tr><th>Event lines</th><td>{data.lines:,}</td></tr><tr><th>AegisLog version</th><td>{escape(__version__)}</td></tr><tr><th>Generated</th><td>{generated}</td></tr><tr><th>Analysis model</th><td>Deterministic local processing</td></tr></table></div></section>
<div class="footer">AEGISLOG v{escape(__version__)} · {escape(case_id)} · Defensive security analysis · Generated locally</div></div></main></body></html>'''


def write_html_report(data: DashboardData, output_dir: Path | None = None) -> Path:
    destination = output_dir or (Path.cwd() / "aegislog-reports")
    destination.mkdir(parents=True, exist_ok=True)
    stem = _safe_name(Path(data.source).stem)
    target = destination / f"{stem}-aegislog-report.html"
    target.write_text(build_html_report(data), encoding="utf-8")
    return target
