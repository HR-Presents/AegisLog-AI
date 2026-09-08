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
  --ink: #162033;
  --ink-soft: #344054;
  --muted: #667085;
  --paper: #ffffff;
  --page: #edf1f5;
  --navy: #0b1728;
  --line: #d6dde6;
  --line-soft: #e9edf2;
  --accent: #0c7183;
  --good: #15704a;
  --good-bg: #e8f6ef;
  --warn: #8a5a00;
  --warn-bg: #fff4d6;
  --danger: #ad263c;
  --danger-bg: #fdecef;
  --mono-bg: #f6f8fa;
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
  width: min(1180px, calc(100% - 36px));
  margin: 24px auto;
  background: var(--paper);
  border: 1px solid var(--line);
  box-shadow: 0 18px 46px rgba(15, 23, 42, .08);
}
.masthead {
  background: var(--navy);
  color: #f8fbff;
  padding: 25px 32px 23px;
  border-bottom: 4px solid var(--accent);
}
.brandline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 24px;
}
.brand { display: flex; align-items: center; gap: 12px; }
.brand-mark {
  width: 38px;
  height: 42px;
  display: grid;
  place-items: center;
  border: 1.5px solid #71c8d6;
  border-radius: 7px 7px 12px 12px;
  color: #a7e7ef;
  font-size: 11px;
  font-weight: 900;
  letter-spacing: .06em;
}
.brand-name {
  font-size: 21px;
  line-height: 1;
  font-weight: 900;
  letter-spacing: .08em;
}
.brand-sub,
.classification,
.eyebrow,
.section-label,
.cell-label,
.metric span,
.case-strip small {
  text-transform: uppercase;
  font-weight: 800;
  letter-spacing: .10em;
}
.brand-sub { margin-top: 4px; color: #9cb8c7; font-size: 9px; }
.classification { color: #a9c1cf; font-size: 9px; text-align: right; }
.title-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: end;
  gap: 28px;
}
.eyebrow { color: #7dd2df; font-size: 9px; letter-spacing: .14em; }
h1 {
  margin: 5px 0 8px;
  font-size: clamp(30px, 4vw, 43px);
  line-height: 1.06;
  letter-spacing: -.025em;
}
.subtitle { max-width: 780px; margin: 0; color: #c7d5df; font-size: 14px; }
.posture {
  min-width: 142px;
  padding: 12px 14px;
  border: 1px solid rgba(255,255,255,.18);
  background: rgba(255,255,255,.045);
  text-align: right;
}
.posture small {
  display: block;
  color: #9cb8c7;
  font-size: 8px;
  font-weight: 800;
  letter-spacing: .10em;
  text-transform: uppercase;
}
.posture strong { display: block; margin-top: 2px; font-size: 22px; }
.posture.good strong { color: #83dcb2; }
.posture.warning strong { color: #ffd479; }
.posture.danger strong { color: #ff9bab; }
.case-strip {
  display: grid;
  grid-template-columns: 1.25fr .8fr .95fr 1fr;
  background: #f8fafc;
  border-bottom: 1px solid var(--line);
}
.case-strip > div {
  min-width: 0;
  padding: 11px 16px;
  border-right: 1px solid var(--line);
}
.case-strip > div:last-child { border-right: 0; }
.case-strip small { display: block; color: var(--muted); font-size: 8px; }
.case-strip strong {
  display: block;
  margin-top: 2px;
  font-size: 11px;
  overflow-wrap: anywhere;
}
.toolbar {
  display: flex;
  align-items: center;
  gap: 4px;
  min-height: 44px;
  padding: 8px 14px;
  border-bottom: 1px solid var(--line);
  background: rgba(255,255,255,.96);
  position: sticky;
  top: 0;
  z-index: 5;
}
.toolbar a {
  padding: 6px 8px;
  border-radius: 5px;
  color: #475467;
  text-decoration: none;
  font-size: 10px;
  font-weight: 750;
}
.toolbar a:hover { background: #f2f4f7; }
.toolbar .spacer { flex: 1; }
.toolbar .local-note {
  margin-right: 8px;
  color: var(--muted);
  font-size: 9px;
  font-weight: 800;
  letter-spacing: .06em;
  text-transform: uppercase;
}
.toolbar button {
  border: 1px solid #0b6878;
  background: var(--accent);
  color: #fff;
  padding: 7px 10px;
  font: inherit;
  font-size: 10px;
  font-weight: 800;
  cursor: pointer;
}
.content { padding: 22px 26px 32px; }
.metrics {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  border: 1px solid var(--line);
  margin-bottom: 18px;
}
.metric {
  min-width: 0;
  padding: 12px 14px;
  border-right: 1px solid var(--line);
}
.metric:last-child { border-right: 0; }
.metric span { display: block; color: var(--muted); font-size: 8px; }
.metric strong { display: block; margin-top: 3px; font-size: 22px; line-height: 1.1; }
.metric.good strong { color: var(--good); }
.metric.warning strong { color: var(--warn); }
.metric.danger strong { color: var(--danger); }
.section { padding: 21px 0; border-top: 1px solid var(--line); }
.section:first-of-type { border-top: 0; padding-top: 0; }
.section-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 12px;
}
.section-label { color: var(--accent); font-size: 8px; letter-spacing: .13em; }
h2 { margin: 2px 0 0; font-size: 20px; letter-spacing: -.01em; }
.section-note { max-width: 520px; color: var(--muted); font-size: 10px; text-align: right; }
.executive-grid {
  display: grid;
  grid-template-columns: 1.05fr .95fr;
  gap: 14px;
}
.assessment,
.priority-box { border: 1px solid var(--line); min-height: 100%; }
.assessment { border-left: 4px solid var(--accent); padding: 14px 15px; }
.assessment h3,
.priority-box h3 { margin: 0 0 7px; font-size: 13px; }
.assessment p { margin: 0; color: var(--ink-soft); }
.assessment .caveat { margin-top: 9px; color: var(--muted); font-size: 10px; }
.decision {
  margin-top: 12px;
  padding: 10px 11px;
  background: #f8fafc;
  border: 1px solid var(--line-soft);
}
.decision strong { font-size: 11px; }
.decision p { margin: 3px 0 0; color: #475467; font-size: 10px; }
.priority-box h3 { padding: 11px 12px 0; }
.triage-item {
  display: grid;
  grid-template-columns: 70px minmax(0, 1fr);
  gap: 9px;
  padding: 9px 11px;
  border-top: 1px solid var(--line-soft);
}
.triage-item strong { display: block; font-size: 11px; }
.triage-item p { margin: 2px 0 0; color: #475467; font-size: 10px; }
.severity-block { margin-top: 12px; border: 1px solid var(--line); }
.severity-row {
  display: grid;
  grid-template-columns: 86px 44px 1fr;
  align-items: center;
  gap: 10px;
  padding: 7px 10px;
  border-bottom: 1px solid var(--line-soft);
}
.severity-row:last-child { border-bottom: 0; }
.severity-row small { color: var(--muted); font-size: 9px; font-weight: 800; }
.track { height: 4px; background: #edf1f5; overflow: hidden; }
.track i { display: block; height: 100%; background: var(--accent); }
.severity-row.danger .track i { background: var(--danger); }
.severity-row.warning .track i { background: #c18411; }
.severity-row.neutral .track i { background: #7693a0; }
.pill {
  display: inline-block;
  width: max-content;
  padding: 3px 7px;
  border-radius: 999px;
  font-size: 8px;
  font-weight: 900;
  letter-spacing: .04em;
}
.pill.good { color: var(--good); background: var(--good-bg); }
.pill.warning { color: var(--warn); background: var(--warn-bg); }
.pill.danger { color: var(--danger); background: var(--danger-bg); }
.pill.neutral { color: #475467; background: #eef2f6; }
.record-list { display: grid; gap: 10px; }
.record { border: 1px solid var(--line); background: #fff; }
.record-head {
  display: grid;
  grid-template-columns: auto minmax(0,1fr) auto;
  gap: 10px;
  align-items: center;
  padding: 10px 12px;
  background: #f8fafc;
  border-bottom: 1px solid var(--line);
}
.record-id {
  color: var(--accent);
  font-family: "Cascadia Mono", Consolas, monospace;
  font-size: 10px;
  font-weight: 800;
}
.record-title { min-width: 0; font-size: 12px; font-weight: 800; }
.record-meta { color: var(--muted); font-size: 9px; text-align: right; }
.record-body {
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(220px, .75fr);
}
.record-cell { min-width: 0; padding: 11px 12px; }
.record-cell + .record-cell { border-left: 1px solid var(--line-soft); }
.cell-label { display: block; margin-bottom: 5px; color: var(--muted); font-size: 8px; }
code {
  color: #0a6474;
  font-family: "Cascadia Mono", Consolas, monospace;
  font-size: 10px;
}
.evidence {
  display: block;
  padding: 8px 9px;
  background: var(--mono-bg);
  border: 1px solid var(--line-soft);
  color: #344054;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}
.evidence-list { margin: 0; padding: 0; list-style: none; }
.evidence-list li + li { margin-top: 5px; }
.action-text { margin: 0; color: #344054; font-size: 11px; }
.table-wrap { width: 100%; overflow-x: auto; border: 1px solid var(--line); }
table { width: 100%; border-collapse: collapse; }
th, td {
  padding: 9px 10px;
  border-bottom: 1px solid var(--line-soft);
  text-align: left;
  vertical-align: top;
}
tr:last-child th, tr:last-child td { border-bottom: 0; }
thead th {
  background: #f8fafc;
  color: #475467;
  font-size: 8px;
  font-weight: 900;
  letter-spacing: .07em;
  text-transform: uppercase;
}
td { overflow-wrap: anywhere; }
.chips { display: flex; flex-wrap: wrap; gap: 5px; }
.chip {
  border: 1px solid var(--line);
  background: #f8fafc;
  padding: 4px 7px;
  color: #475467;
  font-size: 9px;
}
.method-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.method-card { border: 1px solid var(--line); padding: 13px 14px; }
.method-card h3 { margin: 0 0 6px; font-size: 12px; }
.method-card p { margin: 0; color: #475467; font-size: 10px; }
.empty {
  padding: 18px 12px;
  border: 1px dashed var(--line);
  color: var(--muted);
  text-align: center;
  font-size: 11px;
}
.footer {
  margin-top: 20px;
  padding-top: 12px;
  border-top: 1px solid var(--line);
  color: var(--muted);
  font-size: 9px;
  text-align: center;
}
@media (max-width: 900px) {
  .case-strip { grid-template-columns: 1fr 1fr; }
  .case-strip > div:nth-child(2) { border-right: 0; }
  .case-strip > div:nth-child(-n+2) { border-bottom: 1px solid var(--line); }
  .metrics { grid-template-columns: repeat(3, 1fr); }
  .metric:nth-child(3) { border-right: 0; }
  .metric:nth-child(-n+3) { border-bottom: 1px solid var(--line); }
  .executive-grid, .method-grid { grid-template-columns: 1fr; }
}
@media (max-width: 680px) {
  body { background: #fff; }
  .report { width: 100%; margin: 0; border: 0; box-shadow: none; }
  .masthead { padding: 22px 18px; }
  .brandline { align-items: flex-start; }
  .title-grid { grid-template-columns: 1fr; align-items: start; }
  .posture { min-width: 0; text-align: left; }
  .toolbar { overflow-x: auto; }
  .toolbar .local-note { display: none; }
  .content { padding: 16px; }
  .metrics { grid-template-columns: 1fr 1fr; }
  .metric, .metric:nth-child(3) {
    border-right: 1px solid var(--line);
    border-bottom: 1px solid var(--line);
  }
  .metric:nth-child(even) { border-right: 0; }
  .record-body { grid-template-columns: 1fr; }
  .record-cell + .record-cell { border-left: 0; border-top: 1px solid var(--line-soft); }
  .section-head { display: block; }
  .section-note { margin-top: 4px; text-align: left; }
}
@media (max-width: 430px) {
  .case-strip, .metrics { grid-template-columns: 1fr; }
  .case-strip > div, .metric { border-right: 0; border-bottom: 1px solid var(--line); }
  .record-head { grid-template-columns: 1fr; }
  .record-meta { text-align: left; }
  .triage-item { grid-template-columns: 1fr; }
  .severity-row { grid-template-columns: 74px 36px 1fr; }
}
@media print {
  @page { margin: 11mm; }
  body { background: #fff; color: #111827; font-size: 9.5px; }
  .report { width: 100%; margin: 0; border: 0; box-shadow: none; }
  .masthead {
    padding: 17px 19px;
    print-color-adjust: exact;
    -webkit-print-color-adjust: exact;
  }
  .brandline { margin-bottom: 14px; }
  .toolbar { display: none; }
  .content { padding: 13px 0 0; }
  .metrics { grid-template-columns: repeat(5, 1fr); margin-bottom: 13px; }
  .metric { padding: 9px 10px; }
  .section { padding: 13px 0; }
  #executive { break-after: page; }
  #incidents { border-top: 0; padding-top: 0; }
  .record, .assessment, .priority-box, .severity-block, .method-card, .table-wrap {
    break-inside: avoid;
  }
  thead { display: table-header-group; }
  tr { break-inside: avoid; }
}
"""


def _safe_name(value: str) -> str:
    cleaned = "".join(char if char.isalnum() or char in {"-", "_"} else "-" for char in value)
    return cleaned.strip("-") or "analysis"


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


def _case_id(data: DashboardData) -> str:
    parts = [data.source, str(data.lines)]
    parts.extend(
        f"F|{item.severity}|{item.category}|{item.title}|{item.evidence}|{item.recommendation}"
        for item in data.findings
    )
    parts.extend(
        f"I|{item.id}|{item.severity}|{item.category}|{item.count}|{item.title}|{'|'.join(item.evidence)}"
        for item in data.incidents
    )
    parts.extend(f"A|{item.score:.6f}|{item.key}|{item.reason}" for item in data.anomalies)
    material = "\x1e".join(parts)
    digest = hashlib.sha256(material.encode("utf-8", errors="replace")).hexdigest()[:10].upper()
    return f"AL-{digest}"


def _assessment(data: DashboardData, risk: str) -> str:
    if risk == "CRITICAL":
        return (
            "Critical rule-backed activity was retained. Prioritize the highest-severity findings and "
            "correlated incident evidence, then validate against original telemetry and asset context."
        )
    if risk == "HIGH":
        return (
            "High-severity defensive signals were retained. Analyst review is recommended before normal "
            "operational follow-up because the evidence may represent material security activity."
        )
    if risk == "REVIEW":
        return (
            "The investigation retained medium-severity findings that warrant review. Validate the "
            "evidence in source, identity, host, and network context before escalation."
        )
    return (
        "No critical, high, or medium rule-backed findings were retained in this analysis. This is not "
        "proof that malicious activity is absent; review coverage and preserve original telemetry as needed."
    )


def _ordered_findings(data: DashboardData):
    return sorted(
        data.findings,
        key=lambda item: (-_SEVERITY_RANK.get(item.severity, 0), item.category, item.title),
    )


def _metric(label: str, value: str, modifier: str = "") -> str:
    suffix = f" {modifier}" if modifier else ""
    return (
        f'<article class="metric{suffix}"><span>{escape(label)}</span>'
        f"<strong>{escape(value)}</strong></article>"
    )


def _severity_overview(data: DashboardData) -> str:
    total = max(sum(data.severities.values()), 1)
    rows: list[str] = []
    for severity in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
        count = data.severities.get(severity, 0)
        percent = min(100.0, (count / total) * 100.0)
        modifier = _risk_class(severity)
        rows.append(
            f'<div class="severity-row {modifier}">'
            f"<small>{severity}</small><strong>{count}</strong>"
            f'<div class="track"><i style="width:{percent:.1f}%"></i></div>'
            "</div>"
        )
    return "".join(rows)


def _primary_decision(data: DashboardData) -> str:
    ordered = _ordered_findings(data)
    if not ordered:
        return (
            '<div class="decision"><strong>Primary analyst decision</strong>'
            "<p>No elevated rule-backed finding requires immediate action. Review coverage, context, "
            "and original telemetry before closing the investigation.</p></div>"
        )
    top = ordered[0]
    return (
        '<div class="decision">'
        f'<span class="pill {_risk_class(top.severity)}">{escape(top.severity)}</span> '
        f"<strong>{escape(top.title)}</strong>"
        f"<p>{escape(top.recommendation)}</p>"
        "</div>"
    )


def _triage_actions(data: DashboardData) -> str:
    seen: set[str] = set()
    actions: list[str] = []
    for item in _ordered_findings(data):
        recommendation = item.recommendation.strip()
        if not recommendation or recommendation in seen:
            continue
        seen.add(recommendation)
        actions.append(
            '<div class="triage-item">'
            f'<span class="pill {_risk_class(item.severity)}">{escape(item.severity)}</span>'
            f"<div><strong>{escape(item.title)}</strong><p>{escape(recommendation)}</p></div>"
            "</div>"
        )
        if len(actions) == 4:
            break
    if not actions:
        return '<div class="empty">No immediate rule-backed remediation items were generated.</div>'
    return "".join(actions)


def _incident_records(data: DashboardData) -> str:
    records: list[str] = []
    for item in data.incidents:
        evidence = "".join(
            f'<li><code class="evidence">{escape(value)}</code></li>' for value in item.evidence
        )
        records.append(
            '<article class="record">'
            '<div class="record-head">'
            f'<span class="record-id">INC-{escape(item.id.upper()[:8])}</span>'
            f'<span class="record-title">{escape(item.title)}</span>'
            f'<span class="record-meta"><span class="pill {_risk_class(item.severity)}">'
            f"{escape(item.severity)}</span> &nbsp; {escape(item.category)} &nbsp; "
            f"{item.count} signal(s)</span>"
            "</div>"
            '<div class="record-body">'
            '<div class="record-cell"><span class="cell-label">Evidence chain</span>'
            f'<ul class="evidence-list">{evidence}</ul></div>'
            '<div class="record-cell"><span class="cell-label">Analyst handling</span>'
            '<p class="action-text">Review the grouped signals together, validate them against the original '
            "telemetry and surrounding host or identity context, then determine whether escalation is "
            "warranted.</p></div></div></article>"
        )
    if not records:
        return '<div class="empty">No correlated incidents were recorded.</div>'
    return "".join(records)


def _finding_records(data: DashboardData) -> str:
    records: list[str] = []
    for index, item in enumerate(_ordered_findings(data), start=1):
        records.append(
            '<article class="record">'
            '<div class="record-head">'
            f'<span class="record-id">F-{index:03d}</span>'
            f'<span class="record-title">{escape(item.title)}</span>'
            f'<span class="record-meta"><span class="pill {_risk_class(item.severity)}">'
            f"{escape(item.severity)}</span> &nbsp; {escape(item.category)}</span>"
            "</div>"
            '<div class="record-body">'
            '<div class="record-cell"><span class="cell-label">Retained evidence</span>'
            f'<code class="evidence">{escape(item.evidence)}</code></div>'
            '<div class="record-cell"><span class="cell-label">Recommended action</span>'
            f'<p class="action-text">{escape(item.recommendation)}</p></div>'
            "</div></article>"
        )
    if not records:
        return '<div class="empty">No rule-backed findings were recorded.</div>'
    return "".join(records)


def _anomaly_rows(data: DashboardData) -> str:
    rows = "".join(
        "<tr>"
        f"<td><strong>{item.score:.1f}</strong></td>"
        f"<td><code>{escape(item.key)}</code></td>"
        f"<td>{escape(item.reason)}</td>"
        "</tr>"
        for item in data.anomalies
    )
    return rows or (
        '<tr><td colspan="3" class="empty">No rare concerning event classes were recorded.</td></tr>'
    )


def _telemetry_chips(values: dict[str, int]) -> str:
    if not values:
        return '<span class="chip">none</span>'
    return "".join(
        f'<span class="chip">{escape(str(key))} <strong>{count}</strong></span>'
        for key, count in sorted(values.items(), key=lambda pair: (-pair[1], pair[0]))
    )


def build_html_report(data: DashboardData) -> str:
    """Return a self-contained, local analyst report using retained evidence only."""
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    source_name = Path(data.source).name
    risk = _risk(data)
    case_id = _case_id(data)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light">
<title>AegisLog Investigation Report - {escape(source_name)}</title>
<style>{_REPORT_STYLE}</style>
</head>
<body>
<main class="report">
<header class="masthead" id="cover">
  <div class="brandline">
    <div class="brand">
      <div class="brand-mark" aria-hidden="true">AL</div>
      <div><div class="brand-name">AEGISLOG</div><div class="brand-sub">Security operations / local-first</div></div>
    </div>
    <div class="classification">Defensive analysis<br>Retained evidence report</div>
  </div>
  <div class="title-grid">
    <div>
      <div class="eyebrow">Investigation record / {escape(case_id)}</div>
      <h1>Security Investigation Report</h1>
      <p class="subtitle">Executive assessment and retained defensive evidence for <strong>{escape(source_name)}</strong>, followed by incident, finding, anomaly, telemetry, and methodology records.</p>
    </div>
    <div class="posture {_risk_class(risk)}"><small>Current posture</small><strong>{escape(risk)}</strong></div>
  </div>
</header>

<section class="case-strip" aria-label="Case metadata">
  <div><small>Source</small><strong>{escape(source_name)}</strong></div>
  <div><small>Case reference</small><strong>{escape(case_id)}</strong></div>
  <div><small>Generated</small><strong>{generated}</strong></div>
  <div><small>Processing</small><strong>LOCAL / READ-ONLY</strong></div>
</section>

<nav class="toolbar" aria-label="Report sections">
  <a href="#executive">Executive</a><a href="#incidents">Incidents</a><a href="#findings">Findings</a>
  <a href="#anomalies">Anomalies</a><a href="#telemetry">Telemetry</a><a href="#method">Method</a>
  <span class="spacer"></span><span class="local-note">REMOTE AI NOT REQUIRED</span>
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
    <div><div class="section-label">Executive brief / page 1</div><h2>Executive Summary</h2></div>
    <div class="section-note">Evidence is investigative and should be validated against original telemetry and operational context.</div>
  </div>
  <div class="executive-grid">
    <div class="assessment">
      <h3>Assessment</h3>
      <p>{escape(_assessment(data, risk))}</p>
      {_primary_decision(data)}
      <p class="caveat">AegisLog analyzed <strong>{data.lines:,}</strong> event line(s), retained <strong>{len(data.findings)}</strong> rule-backed finding(s), <strong>{len(data.incidents)}</strong> correlated incident(s), and <strong>{len(data.anomalies)}</strong> anomaly signal(s). Findings are not proof of compromise.</p>
      <div class="section-label" style="margin-top:12px;margin-bottom:6px">Severity distribution</div>
      <div class="severity-block">{_severity_overview(data)}</div>
    </div>
    <div class="priority-box" id="triage">
      <h3>Recommended Triage</h3>
      {_triage_actions(data)}
    </div>
  </div>
</section>

<section class="section" id="incidents">
  <div class="section-head">
    <div><div class="section-label">Correlation</div><h2>Incident Queue</h2></div>
    <div class="section-note">Signals grouped by the local correlation engine for joint analyst review.</div>
  </div>
  <div class="record-list">{_incident_records(data)}</div>
</section>

<section class="section" id="findings">
  <div class="section-head">
    <div><div class="section-label">Detection</div><h2>Findings and Recommendations</h2></div>
    <div class="section-note">Rule-backed detections ordered by severity with retained evidence and handling guidance.</div>
  </div>
  <div class="record-list">{_finding_records(data)}</div>
</section>

<section class="section" id="anomalies">
  <div class="section-head">
    <div><div class="section-label">Behavior</div><h2>Anomaly Signals</h2></div>
    <div class="section-note">Rare concerning event classes surfaced for review; anomaly scores are not standalone verdicts.</div>
  </div>
  <div class="table-wrap"><table>
    <thead><tr><th>Score</th><th>Event class</th><th>Reason</th></tr></thead>
    <tbody>{_anomaly_rows(data)}</tbody>
  </table></div>
</section>

<section class="section" id="telemetry">
  <div class="section-head">
    <div><div class="section-label">Telemetry</div><h2>Observed Distribution</h2></div>
    <div class="section-note">High-level distribution of parsed telemetry retained by the analysis snapshot.</div>
  </div>
  <div class="table-wrap"><table>
    <tr><th>Categories</th><td><div class="chips">{_telemetry_chips(data.categories)}</div></td></tr>
    <tr><th>Log levels</th><td><div class="chips">{_telemetry_chips(data.levels)}</div></td></tr>
    <tr><th>Services</th><td><div class="chips">{_telemetry_chips(data.services)}</div></td></tr>
  </table></div>
</section>

<section class="section" id="method">
  <div class="section-head">
    <div><div class="section-label">Method and scope</div><h2>Analysis Profile</h2></div>
    <div class="section-note">How this report was produced and how its evidence should be interpreted.</div>
  </div>
  <div class="method-grid">
    <div class="method-card"><h3>Processing model</h3><p>AegisLog v{escape(__version__)} performed local deterministic detection, incident correlation, and anomaly scoring. The source was handled read-only and remote AI was not required for this report.</p></div>
    <div class="method-card"><h3>Evidence limitations</h3><p>The report contains retained derived evidence rather than a complete copy of the raw log. Missing detections do not prove malicious activity is absent. Preserve original telemetry separately when incident-response, retention, or chain-of-custody procedures require it.</p></div>
  </div>
  <div class="table-wrap" style="margin-top:12px"><table>
    <tr><th>Source path</th><td>{escape(data.source)}</td></tr>
    <tr><th>Source file</th><td>{escape(source_name)}</td></tr>
    <tr><th>Event lines</th><td>{data.lines:,}</td></tr>
    <tr><th>AegisLog version</th><td>{escape(__version__)}</td></tr>
    <tr><th>Generated</th><td>{generated}</td></tr>
    <tr><th>Remote AI</th><td>Not required for this report</td></tr>
  </table></div>
</section>

<div class="footer">AEGISLOG v{escape(__version__)} / {escape(case_id)} / Defensive security analysis / Generated locally</div>
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