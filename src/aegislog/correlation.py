from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass

IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
USER_RE = re.compile(r"(?:user(?:name)?[=: ]+|for (?:invalid user )?)([A-Za-z0-9_.@-]+)", re.I)
HOST_RE = re.compile(r"(?:host(?:name)?[=: ]+)([A-Za-z0-9_.-]+)", re.I)
SERVICE_RE = re.compile(r"\b([A-Za-z0-9_.@-]+)(?:\[\d+\])?:\s")
CONTAINER_RE = re.compile(r"(?:container(?:_name)?[=: ]+)([A-Za-z0-9_.-]+)", re.I)


@dataclass(frozen=True)
class EntityLink:
    entity_type: str
    entity: str
    event_count: int
    categories: tuple[str, ...]
    severities: tuple[str, ...]
    score: int


def correlate_entities(findings: list[object]) -> list[EntityLink]:
    graph: dict[tuple[str, str], dict[str, object]] = defaultdict(lambda: {"count": 0, "categories": set(), "severities": set()})
    extractors = (("ip", IP_RE), ("user", USER_RE), ("host", HOST_RE), ("service", SERVICE_RE), ("container", CONTAINER_RE))
    for finding in findings:
        evidence = str(getattr(finding, "evidence", ""))
        category = str(getattr(finding, "category", "unknown"))
        severity = str(getattr(finding, "severity", "INFO"))
        for entity_type, pattern in extractors:
            for entity in pattern.findall(evidence):
                key = (entity_type, entity)
                graph[key]["count"] = int(graph[key]["count"]) + 1
                graph[key]["categories"].add(category)
                graph[key]["severities"].add(severity)
    weight = {"INFO": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 4, "CRITICAL": 7}
    result: list[EntityLink] = []
    for (entity_type, entity), data in graph.items():
        severities = tuple(sorted(data["severities"]))
        categories = tuple(sorted(data["categories"]))
        score = int(data["count"]) + len(categories) * 2 + max((weight.get(item, 0) for item in severities), default=0)
        result.append(EntityLink(entity_type, entity, int(data["count"]), categories, severities, score))
    return sorted(result, key=lambda item: (-item.score, item.entity_type, item.entity))
