from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timezone
from html import escape
from pathlib import Path

from . import __version__
from .dashboard import DashboardData


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
        "CLEAR": "good",
    }.get(value, "neutral")


def _metric(label: str, value: str, modifier: str = "") -> str:
    suffix = f" {modifier}" if modifier else ""
    return (
        f'<article class="metric{suffix}"><span>{escape(label)}</span>'
        f'<strong>{escape(value)}</strong></article>'
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
        f"<td>{'<br>'.join(escape(value) for value in item.evidence) or '-'}</td>"
        "</tr>"
        for item in data.incidents
    ) or '<tr><td colspan="6" class="empty">No correlated incidents.</td></tr>'

    findings = "".join(
        "<tr>"
        f'<td><span class="pill {_risk_class(item.severity)}">{escape(item.severity)}</span></td>'
        f"<td>{escape(item.category)}</td><td>{escape(item.title)}</td>"
        f"<td>{escape(item.evidence)}</td><td>{escape(item.recommendation)}</td>"
        "</tr>"
        for item in data.findings
    ) or '<tr><td colspan="5" class="empty">No rule-backed findings were recorded.</td></tr>'

    anomalies = "".join(
        "<tr>"
        f"<td>{item.score:.1f}</td><td>{escape(item.key)}</td><td>{escape(item.reason)}</td>"
        "</tr>"
        for item in data.anomalies
    ) or '<tr><td colspan="3" class="empty">No rare concerning event classes were recorded.</td></tr>'

    telemetry = "".join(
        f"<tr><th>{escape(group)}</th><td>{escape(', '.join(f'{key}: {count}' for key, count in sorted(values.items(), key=lambda pair: (-pair[1], pair[0])))) or 'none'}</td></tr>"
        for group, values in (
            ("Categories", data.categories),
            ("Log levels", data.levels),
            ("Services", data.services),
        )
    )

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AegisLog Analysis Report - {escape(source_name)}</title>
<style>
:root{{--bg:#071018;--surface:#0d1824;--surface2:#101f2e;--line:#24445f;--text:#e7f6ff;--muted:#8faabd;--cyan:#35e7ff;--blue:#4d8dff;--magenta:#e15cff;--green:#4bf59f;--yellow:#ffd35a;--red:#ff5d76}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;background:radial-gradient(circle at top right,#13263b 0,#071018 40%);color:var(--text);font:15px/1.55 "Segoe UI",Arial,sans-serif}}
.report{{max-width:1280px;margin:0 auto;padding:28px 28px 48px}}.cover{{min-height:640px;border:1px solid #1f6680;background:linear-gradient(145deg,#07131d 0%,#102b3d 58%,#271449 100%);border-radius:24px;padding:46px;display:flex;flex-direction:column;justify-content:space-between;box-shadow:0 30px 80px #0008}}
.brand{{display:flex;align-items:center;gap:18px}}.mark{{width:78px;height:86px;filter:drop-shadow(0 0 18px #35e7ff66)}}.brand-name{{font-size:33px;font-weight:900;letter-spacing:.08em}}.brand-sub{{color:var(--cyan);font-size:11px;letter-spacing:.2em;font-weight:800}}h1{{font-size:54px;line-height:1.05;margin:14px 0}}.lede{{max-width:780px;color:#c5dce8;font-size:19px}}.meta{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:30px}}.meta div{{padding:14px;border:1px solid #ffffff22;background:#ffffff08;border-radius:12px}}.meta small{{display:block;color:#9fc0d2;margin-bottom:4px}}
.actions{{display:flex;justify-content:flex-end;margin:18px 0;gap:10px}}button{{border:1px solid #2b5c78;background:#102336;color:var(--text);border-radius:9px;padding:10px 15px;font-weight:800;cursor:pointer}}button.primary{{background:linear-gradient(90deg,var(--cyan),var(--blue));color:#031019;border:0}}.grid{{display:grid;grid-template-columns:repeat(6,1fr);gap:12px;margin:18px 0}}.metric,.card{{border:1px solid var(--line);background:linear-gradient(180deg,var(--surface2),var(--surface));border-radius:16px}}.metric{{padding:18px}}.metric span{{display:block;color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.08em}}.metric strong{{font-size:27px}}.metric.good strong{{color:var(--green)}}.metric.warning strong{{color:var(--yellow)}}.metric.danger strong{{color:var(--red)}}.card{{padding:24px;margin-top:16px}}.kicker{{color:var(--cyan);text-transform:uppercase;letter-spacing:.16em;font-size:11px;font-weight:900}}h2{{margin:4px 0 18px;font-size:24px}}table{{width:100%;border-collapse:collapse}}th,td{{padding:11px 10px;border-bottom:1px solid #1b3548;text-align:left;vertical-align:top}}th{{color:#9fbacc;font-size:12px}}code{{color:var(--cyan)}}.pill{{display:inline-block;padding:4px 9px;border-radius:999px;font-size:11px;font-weight:900}}.pill.good{{color:#0d5c37;background:#b7ffd8}}.pill.warning{{color:#6a4b00;background:#ffeaa1}}.pill.danger{{color:#7b0a1e;background:#ffc1cb}}.pill.neutral{{color:#12364c;background:#c7e7f5}}.summary{{padding:18px;border-left:4px solid var(--cyan);background:#0a2230;border-radius:10px}}.empty{{color:var(--muted);text-align:center}}.footer{{margin-top:24px;text-align:center;color:var(--muted);font-size:12px}}
@media(max-width:950px){{.grid{{grid-template-columns:repeat(3,1fr)}}.meta{{grid-template-columns:repeat(2,1fr)}}}}@media(max-width:620px){{.report{{padding:12px}}.cover{{padding:26px;min-height:auto}}h1{{font-size:38px}}.grid,.meta{{grid-template-columns:1fr}}.card{{overflow:auto}}}}
@media print{{body{{background:#fff;color:#111}}.report{{max-width:none;padding:0}}.cover{{min-height:250mm;border-radius:0;box-shadow:none;color:#fff}}.actions{{display:none}}.card,.metric{{background:#fff;color:#111;box-shadow:none}}th{{color:#555}}}}
</style></head><body><main class="report">
<section class="cover"><div class="brand"><svg class="mark" viewBox="0 0 100 112" xmlns="http://www.w3.org/2000/svg" aria-label="AegisLog shield"><defs><linearGradient id="a" x1="0" x2="1"><stop stop-color="#35e7ff"/><stop offset="1" stop-color="#e15cff"/></linearGradient></defs><path d="M50 4 91 19v32c0 28-17 47-41 57C26 98 9 79 9 51V19L50 4Z" fill="none" stroke="url(#a)" stroke-width="6"/><path d="M50 24 70 74H58l-4-11H36l-4 11H20l22-50h8Zm0 18-9 13h18L50 42Z" fill="#e7f6ff"/></svg><div><div class="brand-name">AEGISLOG</div><div class="brand-sub">SECURITY OPERATIONS / LOCAL-FIRST</div></div></div><div><div class="kicker">Defensive analysis report</div><h1>Investigation Report</h1><p class="lede">Complete retained analysis evidence for <strong>{escape(source_name)}</strong>, including findings, correlated incidents, anomaly signals, telemetry summaries, and remediation guidance.</p><div class="meta"><div><small>Source</small><strong>{escape(source_name)}</strong></div><div><small>Version</small><strong>{escape(__version__)}</strong></div><div><small>Generated</small><strong>{generated}</strong></div><div><small>Posture</small><strong>{escape(risk)}</strong></div></div></div><div class="brand-sub">READ-ONLY ANALYSIS / REMOTE AI NOT REQUIRED</div></section>
<div class="actions"><button onclick="window.scrollTo({{top:0,behavior:'smooth'}})">Cover</button><button class="primary" onclick="window.print()">Print / Save PDF</button></div>
<section class="grid">{_metric('Events', f'{data.lines:,}')}{_metric('Findings', str(len(data.findings)))}{_metric('Incidents', str(len(data.incidents)))}{_metric('Anomalies', str(len(data.anomalies)))}{_metric('Critical / High', f"{data.severities.get('CRITICAL',0)} / {data.severities.get('HIGH',0)}", _risk_class(risk))}{_metric('Posture', risk, _risk_class(risk))}</section>
<section class="card"><div class="kicker">Executive view</div><h2>Executive Summary</h2><div class="summary">AegisLog analyzed {data.lines:,} event line(s) and retained {len(data.findings)} rule-backed finding(s), {len(data.incidents)} correlated incident(s), and {len(data.anomalies)} anomaly signal(s). The current defensive posture is <strong>{escape(risk)}</strong>. Findings are investigative evidence and should be validated in operational context; they are not proof of compromise.</div></section>
<section class="card"><div class="kicker">Scope</div><h2>Analysis Profile</h2><table>{_rows((("Source path", data.source),("Source file", source_name),("Event lines", f"{data.lines:,}"),("AegisLog version", __version__),("Generated", generated),("Analysis model", "Local deterministic detection, correlation, anomaly scoring")))}</table></section>
<section class="card"><div class="kicker">Correlation</div><h2>Incidents</h2><table><thead><tr><th>ID</th><th>Severity</th><th>Category</th><th>Signals</th><th>Title</th><th>Evidence</th></tr></thead><tbody>{incidents}</tbody></table></section>
<section class="card"><div class="kicker">Detection</div><h2>Findings and Recommendations</h2><table><thead><tr><th>Severity</th><th>Category</th><th>Detection</th><th>Evidence</th><th>Recommended action</th></tr></thead><tbody>{findings}</tbody></table></section>
<section class="card"><div class="kicker">Behavior</div><h2>Anomaly Signals</h2><table><thead><tr><th>Score</th><th>Event class</th><th>Reason</th></tr></thead><tbody>{anomalies}</tbody></table></section>
<section class="card"><div class="kicker">Telemetry</div><h2>Observed Distribution</h2><table>{telemetry}</table></section>
<section class="card"><div class="kicker">Interpretation</div><h2>Analyst Notes</h2><p>This report contains the same retained, derived evidence used by the terminal dashboard. It intentionally does not reproduce the full raw source log. Missing detections do not prove that malicious activity is absent. Validate important findings against source telemetry, asset context, identity context, and other defensive evidence before escalation.</p></section>
<div class="footer">AEGISLOG v{escape(__version__)} / Defensive security analysis / Generated locally</div>
</main></body></html>"""


def write_html_report(data: DashboardData, output_dir: Path | None = None) -> Path:
    """Write a self-contained report and return its path."""
    destination = output_dir or (Path.cwd() / "aegislog-reports")
    destination.mkdir(parents=True, exist_ok=True)
    stem = _safe_name(Path(data.source).stem)
    target = destination / f"{stem}-aegislog-report.html"
    target.write_text(build_html_report(data), encoding="utf-8")
    return target
