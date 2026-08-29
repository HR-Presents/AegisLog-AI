from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

from .engine import Finding, analyze_lines
from .parsers import parse_line

IP_RE = re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])")
USER_RE = re.compile(r"(?:user(?:name)?[= ]|for (?:invalid user )?)([A-Za-z0-9_.@-]+)", re.IGNORECASE)
TIME_RE = re.compile(r"^(?:[A-Z][a-z]{2}\s+\d{1,2}\s+)?(\d{2}:\d{2}:\d{2})")
SEVERITY = {"INFO": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}


@dataclass(frozen=True)
class TimelineEvent:
    order: int
    timestamp: str
    service: str
    level: str
    summary: str
    entities: tuple[str, ...]


@dataclass(frozen=True)
class EntityProfile:
    kind: str
    value: str
    occurrences: int
    services: tuple[str, ...]
    first_seen: int
    last_seen: int


@dataclass(frozen=True)
class InvestigationIncident:
    id: str
    severity: str
    confidence: int
    category: str
    title: str
    findings: tuple[Finding, ...]
    entities: tuple[str, ...]
    timeline: tuple[TimelineEvent, ...]


def _entities(text: str) -> tuple[str, ...]:
    found: list[str] = []
    for ip in IP_RE.findall(text):
        parts = ip.split(".")
        if all(part.isdigit() and 0 <= int(part) <= 255 for part in parts) and ip not in found:
            found.append(ip)
    for user in USER_RE.findall(text):
        item = f"user:{user}"
        if item not in found:
            found.append(item)
    return tuple(found)


def _confidence(findings: list[Finding], timeline: list[TimelineEvent]) -> int:
    if not findings:
        return 0
    base = {"CRITICAL": 88, "HIGH": 78, "MEDIUM": 64, "LOW": 48, "INFO": 35}.get(
        max(findings, key=lambda item: SEVERITY.get(item.severity, 0)).severity, 50
    )
    evidence_bonus = min(10, max(0, len(findings) - 1) * 3)
    timeline_bonus = min(7, max(0, len(timeline) - 1))
    entity_bonus = 5 if any(event.entities for event in timeline) else 0
    return min(99, base + evidence_bonus + timeline_bonus + entity_bonus)


def build_timeline(lines: list[str]) -> list[TimelineEvent]:
    timeline: list[TimelineEvent] = []
    for order, line in enumerate(lines, start=1):
        event = parse_line(line)
        if not event.message:
            continue
        match = TIME_RE.search(line)
        timestamp = match.group(1) if match else f"line {order}"
        timeline.append(
            TimelineEvent(
                order=order,
                timestamp=timestamp,
                service=event.service or "unknown",
                level=(event.level or "unknown").upper(),
                summary=event.message[:180],
                entities=_entities(line),
            )
        )
    return timeline


def entity_profiles(lines: list[str]) -> list[EntityProfile]:
    services: dict[str, set[str]] = {}
    positions: dict[str, list[int]] = {}
    kinds: dict[str, str] = {}
    for order, line in enumerate(lines, start=1):
        event = parse_line(line)
        for entity in _entities(line):
            kind = "user" if entity.startswith("user:") else "ip"
            value = entity.split(":", 1)[1] if kind == "user" else entity
            key = f"{kind}:{value}"
            kinds[key] = kind
            services.setdefault(key, set()).add(event.service or "unknown")
            positions.setdefault(key, []).append(order)
    profiles = [
        EntityProfile(kinds[key], key.split(":", 1)[1], len(pos), tuple(sorted(services[key])), pos[0], pos[-1])
        for key, pos in positions.items()
    ]
    return sorted(profiles, key=lambda item: (-item.occurrences, item.kind, item.value))


def build_incidents(lines: list[str]) -> list[InvestigationIncident]:
    findings = analyze_lines(lines)
    timeline = build_timeline(lines)
    grouped: dict[str, list[Finding]] = {}
    for finding in findings:
        grouped.setdefault(finding.category, []).append(finding)
    incidents: list[InvestigationIncident] = []
    for category, items in grouped.items():
        top = max(items, key=lambda item: SEVERITY.get(item.severity, 0))
        relevant_entities: list[str] = []
        for item in items:
            for entity in _entities(item.evidence + " " + item.title):
                if entity not in relevant_entities:
                    relevant_entities.append(entity)
        related = [event for event in timeline if any(entity in event.entities for entity in relevant_entities)]
        if not related:
            evidence = " ".join(item.evidence for item in items)
            related = [event for event in timeline if event.service.lower() in evidence.lower()][:12]
        digest = hashlib.sha256((category + "\0" + top.title + "\0" + "|".join(relevant_entities)).encode()).hexdigest()[:8].upper()
        incidents.append(
            InvestigationIncident(
                id=f"INC-{digest}",
                severity=top.severity,
                confidence=_confidence(items, related),
                category=category,
                title=top.title,
                findings=tuple(items),
                entities=tuple(relevant_entities),
                timeline=tuple(related[:20]),
            )
        )
    return sorted(incidents, key=lambda item: (SEVERITY.get(item.severity, 0), item.confidence), reverse=True)


def load_investigation(path: Path) -> tuple[list[str], list[InvestigationIncident], list[EntityProfile]]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
    return lines, build_incidents(lines), entity_profiles(lines)
