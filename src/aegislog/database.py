from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .config import config_dir


def database_path() -> Path:
    path = config_dir() / "aegislog.db"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def connect(path: Path | None = None) -> sqlite3.Connection:
    db = sqlite3.connect(path or database_path())
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA foreign_keys=ON")
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            external_id TEXT NOT NULL,
            recorded_at TEXT NOT NULL,
            source TEXT NOT NULL,
            severity TEXT NOT NULL,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            event_count INTEGER NOT NULL,
            evidence_json TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_incidents_recorded_at ON incidents(recorded_at);
        CREATE INDEX IF NOT EXISTS idx_incidents_severity ON incidents(severity);
        CREATE INDEX IF NOT EXISTS idx_incidents_category ON incidents(category);
        """
    )
    return db


def add_incidents(source: str, recorded_at: str, incidents: list, path: Path | None = None) -> int:
    with connect(path) as db:
        db.executemany(
            "INSERT INTO incidents (external_id, recorded_at, source, severity, category, title, event_count, evidence_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [(item.id, recorded_at, source, item.severity, item.category, item.title, item.count, json.dumps(list(item.evidence))) for item in incidents],
        )
        return len(incidents)


def list_incidents(limit: int = 100, severity: str | None = None, path: Path | None = None) -> list[dict]:
    query = "SELECT * FROM incidents"
    params: list[object] = []
    if severity:
        query += " WHERE severity = ?"
        params.append(severity.upper())
    query += " ORDER BY id DESC LIMIT ?"
    params.append(max(1, min(limit, 1000)))
    with connect(path) as db:
        return [dict(row) for row in db.execute(query, params).fetchall()]


def get_incident(row_id: int, path: Path | None = None) -> dict | None:
    with connect(path) as db:
        row = db.execute("SELECT * FROM incidents WHERE id = ?", (row_id,)).fetchone()
        if row is None:
            return None
        item = dict(row)
        item["evidence"] = json.loads(item.pop("evidence_json"))
        return item


def timeline(limit: int = 100, path: Path | None = None) -> list[dict]:
    with connect(path) as db:
        return [dict(row) for row in db.execute("SELECT id, recorded_at, source, severity, category, title, event_count FROM incidents ORDER BY recorded_at DESC, id DESC LIMIT ?", (max(1, min(limit, 1000)),)).fetchall()]
