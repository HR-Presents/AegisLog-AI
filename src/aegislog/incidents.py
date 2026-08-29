from __future__ import annotations

import hashlib
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


def correlate(findings: list[Finding]) -> list[Incident]:
    groups: dict[str, list[Finding]] = defaultdict(list)
    for finding in findings:
        groups[finding.category].append(finding)
    incidents: list[Incident] = []
    for category, items in groups.items():
        top = max(items, key=lambda item: SEVERITY.get(item.severity, 0))
        digest = hashlib.sha256((category + "\0" + top.title).encode()).hexdigest()[:12]
        incidents.append(Incident(
            id=digest,
            category=category,
            severity=top.severity,
            count=len(items),
            title=top.title,
            evidence=tuple(item.evidence for item in items[:5]),
        ))
    return sorted(incidents, key=lambda i: SEVERITY.get(i.severity, 0), reverse=True)
