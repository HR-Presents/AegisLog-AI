from __future__ import annotations

import re
from dataclasses import dataclass

from .database import connect


@dataclass(frozen=True)
class HuntResult:
    id: int
    recorded_at: str
    severity: str
    category: str
    source: str
    title: str


def search_incidents(query: str = "", severity: str = "", category: str = "", source: str = "", limit: int = 100) -> list[HuntResult]:
    clauses: list[str] = []
    params: list[object] = []
    if query:
        clauses.append("(title LIKE ? OR evidence_json LIKE ?)")
        token = f"%{query}%"
        params.extend([token, token])
    if severity:
        clauses.append("severity = ?")
        params.append(severity.upper())
    if category:
        clauses.append("category = ?")
        params.append(category)
    if source:
        clauses.append("source LIKE ?")
        params.append(f"%{source}%")
    sql = "SELECT id, recorded_at, severity, category, source, title FROM incidents"
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY id DESC LIMIT ?"
    params.append(max(1, min(limit, 1000)))
    with connect() as db:
        return [HuntResult(**dict(row)) for row in db.execute(sql, params).fetchall()]


def extract_indicators(text: str) -> dict[str, list[str]]:
    ipv4 = sorted(set(re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", text)))
    domains = sorted(set(re.findall(r"\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b", text)))
    return {"ipv4": ipv4[:200], "domains": domains[:200]}
