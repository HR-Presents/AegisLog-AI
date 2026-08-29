from __future__ import annotations

import sqlite3

LATEST_SCHEMA = 2


def migrate(db: sqlite3.Connection) -> int:
    db.execute("CREATE TABLE IF NOT EXISTS schema_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
    row = db.execute("SELECT value FROM schema_meta WHERE key='schema_version'").fetchone()
    current = int(row[0]) if row else 1
    if current > LATEST_SCHEMA:
        raise RuntimeError(f"database schema {current} is newer than supported schema {LATEST_SCHEMA}")
    if current < 2:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_id INTEGER,
                entity_type TEXT NOT NULL,
                entity_value TEXT NOT NULL,
                score INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY(incident_id) REFERENCES incidents(id) ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS idx_entities_type_value ON entities(entity_type, entity_value);
            CREATE INDEX IF NOT EXISTS idx_entities_incident ON entities(incident_id);
            """
        )
        current = 2
    db.execute(
        "INSERT INTO schema_meta(key, value) VALUES('schema_version', ?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (str(current),),
    )
    db.commit()
    return current
