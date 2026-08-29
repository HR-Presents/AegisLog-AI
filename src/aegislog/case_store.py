from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .database import connect
from .investigation import InvestigationIncident


def ensure_case_schema(db: sqlite3.Connection) -> None:
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS investigation_cases (
            incident_id TEXT PRIMARY KEY,
            first_recorded_at TEXT NOT NULL,
            last_recorded_at TEXT NOT NULL,
            source TEXT NOT NULL,
            severity TEXT NOT NULL,
            confidence INTEGER NOT NULL,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            entities_json TEXT NOT NULL,
            findings_json TEXT NOT NULL,
            timeline_json TEXT NOT NULL,
            observation_count INTEGER NOT NULL DEFAULT 1
        );
        CREATE INDEX IF NOT EXISTS idx_cases_last_seen ON investigation_cases(last_recorded_at);
        CREATE INDEX IF NOT EXISTS idx_cases_severity ON investigation_cases(severity);
        CREATE INDEX IF NOT EXISTS idx_cases_category ON investigation_cases(category);
        """
    )


def save_cases(source: str, incidents: list[InvestigationIncident], path: Path | None = None) -> int:
    now = datetime.now(timezone.utc).isoformat()
    with connect(path) as db:
        ensure_case_schema(db)
        for item in incidents:
            findings = [asdict(finding) for finding in item.findings]
            timeline = [asdict(event) for event in item.timeline]
            db.execute(
                """
                INSERT INTO investigation_cases (
                    incident_id, first_recorded_at, last_recorded_at, source, severity, confidence,
                    category, title, entities_json, findings_json, timeline_json, observation_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                ON CONFLICT(incident_id) DO UPDATE SET
                    last_recorded_at=excluded.last_recorded_at,
                    source=excluded.source,
                    severity=excluded.severity,
                    confidence=excluded.confidence,
                    category=excluded.category,
                    title=excluded.title,
                    entities_json=excluded.entities_json,
                    findings_json=excluded.findings_json,
                    timeline_json=excluded.timeline_json,
                    observation_count=investigation_cases.observation_count + 1
                """,
                (
                    item.id, now, now, source, item.severity, item.confidence, item.category, item.title,
                    json.dumps(list(item.entities)), json.dumps(findings), json.dumps(timeline),
                ),
            )
    return len(incidents)


def list_cases(limit: int = 100, severity: str | None = None, path: Path | None = None) -> list[dict]:
    query = "SELECT * FROM investigation_cases"
    params: list[object] = []
    if severity:
        query += " WHERE severity = ?"
        params.append(severity.upper())
    query += " ORDER BY last_recorded_at DESC LIMIT ?"
    params.append(max(1, min(limit, 1000)))
    with connect(path) as db:
        ensure_case_schema(db)
        return [dict(row) for row in db.execute(query, params).fetchall()]


def get_case(incident_id: str, path: Path | None = None) -> dict | None:
    with connect(path) as db:
        ensure_case_schema(db)
        row = db.execute("SELECT * FROM investigation_cases WHERE incident_id = ?", (incident_id.upper(),)).fetchone()
        if row is None:
            return None
        item = dict(row)
        item["entities"] = json.loads(item.pop("entities_json"))
        item["findings"] = json.loads(item.pop("findings_json"))
        item["timeline"] = json.loads(item.pop("timeline_json"))
        return item
