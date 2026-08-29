from __future__ import annotations

from dataclasses import dataclass

from .engine import Finding, redact


@dataclass(frozen=True)
class InvestigationContext:
    question: str
    findings: list[Finding]
    log_excerpt: list[str]


def build_safe_prompt(context: InvestigationContext, limit: int = 80) -> str:
    findings = "\n".join(
        f"- {f.severity} | {f.title} | {redact(f.evidence)}" for f in context.findings[:30]
    )
    excerpt = "\n".join(redact(line.strip()) for line in context.log_excerpt[:limit])
    return (
        "You are a defensive log-analysis assistant. Do not claim compromise without evidence. "
        "Separate observed evidence from hypotheses and give safe investigation/remediation steps.\n\n"
        f"Question: {context.question}\n\nFindings:\n{findings or 'None'}\n\n"
        f"Redacted log context:\n{excerpt}\n"
    )


def local_answer(context: InvestigationContext) -> str:
    if not context.findings:
        return "No rule-backed finding answers this conclusively. Review the surrounding events and collect more context."
    top = context.findings[:5]
    lines = ["Local investigation summary:"]
    for finding in top:
        lines.append(f"- [{finding.severity}] {finding.title}: {finding.recommendation}")
    lines.append("These are investigative signals, not proof of compromise.")
    return "\n".join(lines)
