from __future__ import annotations

import html
from datetime import datetime, timezone
from pathlib import Path


def markdown_report(source: str, total: int, findings: list, incidents: list) -> str:
    lines = ["# AegisLog AI Security Report", "", f"Generated: {datetime.now(timezone.utc).isoformat()}", f"Source: `{source}`", f"Lines analyzed: {total}", "", "## Findings", ""]
    if not findings:
        lines.append("No rule-backed findings were detected.")
    for finding in findings:
        lines.extend([f"### [{finding.severity}] {finding.title}", f"- Category: `{finding.category}`", f"- Evidence: `{finding.evidence}`", f"- Recommendation: {finding.recommendation}", ""])
    lines.extend(["## Correlated incidents", ""])
    for incident in incidents:
        lines.append(f"- **{incident.severity}** `{incident.id}` — {incident.title} ({incident.count} events)")
    lines.extend(["", "> Findings are investigative signals and should be validated with surrounding telemetry before response actions."])
    return "\n".join(lines) + "\n"


def html_report(source: str, total: int, findings: list, incidents: list) -> str:
    rows = "".join(f"<tr><td>{html.escape(f.severity)}</td><td>{html.escape(f.title)}</td><td>{html.escape(f.category)}</td><td><code>{html.escape(f.evidence)}</code></td><td>{html.escape(f.recommendation)}</td></tr>" for f in findings)
    incident_rows = "".join(f"<tr><td>{html.escape(i.severity)}</td><td>{html.escape(i.id)}</td><td>{html.escape(i.title)}</td><td>{i.count}</td></tr>" for i in incidents)
    return f"""<!doctype html><html><head><meta charset=\"utf-8\"><title>AegisLog AI Security Report</title><style>body{{font-family:system-ui,sans-serif;max-width:1200px;margin:40px auto;padding:0 20px}}table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #ccc;padding:8px;text-align:left;vertical-align:top}}code{{white-space:pre-wrap}}.note{{padding:12px;background:#f4f4f4}}</style></head><body><h1>AegisLog AI Security Report</h1><p><strong>Source:</strong> {html.escape(source)}<br><strong>Lines analyzed:</strong> {total}</p><h2>Findings</h2><table><thead><tr><th>Severity</th><th>Finding</th><th>Category</th><th>Evidence</th><th>Recommendation</th></tr></thead><tbody>{rows}</tbody></table><h2>Correlated incidents</h2><table><thead><tr><th>Severity</th><th>ID</th><th>Summary</th><th>Events</th></tr></thead><tbody>{incident_rows}</tbody></table><p class=\"note\">Findings are investigative signals and should be validated with surrounding telemetry before response actions.</p></body></html>"""


def write_report(output: Path, source: str, total: int, findings: list, incidents: list) -> None:
    suffix = output.suffix.lower()
    if suffix in {".md", ".markdown"}:
        content = markdown_report(source, total, findings, incidents)
    elif suffix in {".html", ".htm"}:
        content = html_report(source, total, findings, incidents)
    else:
        raise ValueError("report output must end in .md or .html")
    output.write_text(content, encoding="utf-8")
