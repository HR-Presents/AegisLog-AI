from __future__ import annotations

import hashlib
import re
from collections import defaultdict
from dataclasses import dataclass

from .engine import Finding


@dataclass(frozen=True)
class Incident:
    id: str
    category: str
    severity: str
    count: int
    title: str
    evidence: tuple[str, ...]


SEVERITY = {"INFO": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
_SERVICE_RE = re.compile(
    r"^(?:\S+\s+)?(?:CRITICAL|ERROR|WARNING|WARN|NOTICE|INFO|DEBUG)\s+(?P<service>[\w.-]+)(?:\[\d+\])?:",
    re.IGNORECASE,
)
_SOURCE_RE = re.compile(
    r"\b(?:from|source(?:_ip)?=|src(?:_ip)?=)(?P<sep>\s*)(?P<ip>[0-9A-Fa-f:.]+)\b",
    re.IGNORECASE,
)


def _service_from_evidence(evidence: str) -> str:
    match = _SERVICE_RE.search(evidence)
    return match.group("service").lower() if match else ""


def _source_from_evidence(evidence: str) -> str:
    match = _SOURCE_RE.search(evidence)
    return match.group("ip").lower() if match else ""


def _correlation_key(finding: Finding) -> tuple[str, str, str, str]:
    """Scope incidents to shared context while preserving generic fallback behavior."""

    category = finding.category.lower()
    service = _service_from_evidence(finding.evidence)
    source = _source_from_evidence(finding.evidence)

    # Structured evidence should not be collapsed merely because two findings share
    # a broad category.  When structured context is absent, retain the historical
    # category-level fallback so older generic inputs remain compatible.
    if service or source:
        return (category, finding.title.lower(), service, source)
    return (category, "", "", "")


def correlate(findings: list[Finding]) -> list[Incident]:
    groups: dict[tuple[str, str, str, str], list[Finding]] = defaultdict(list)
    for finding in findings:
        groups[_correlation_key(finding)].append(finding)

    incidents: list[Incident] = []
    for key, items in groups.items():
        category = key[0]
        top = max(items, key=lambda item: SEVERITY.get(item.severity, 0))

        # Generic operational errors are useful findings, but one isolated structured
        # error is not a correlated incident. Keep it in Findings unless it recurs in
        # the same service/source context. Generic legacy inputs keep prior behavior.
        has_structured_context = bool(key[2] or key[3])
        if category == "error" and has_structured_context and len(items) < 2:
            continue

        digest_seed = "\0".join(key) + "\0" + top.title.lower()
        digest = hashlib.sha256(digest_seed.encode()).hexdigest()[:12]
        incidents.append(
            Incident(
                id=digest,
                category=top.category,
                severity=top.severity,
                count=len(items),
                title=top.title,
                evidence=tuple(item.evidence for item in items[:5]),
            )
        )

    return sorted(
        incidents,
        key=lambda item: (SEVERITY.get(item.severity, 0), item.count),
        reverse=True,
    )
