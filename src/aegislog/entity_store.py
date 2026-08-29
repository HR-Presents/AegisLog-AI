from __future__ import annotations

from pathlib import Path

from .correlation import EntityLink
from .database import connect


def replace_incident_entities(incident_id: int, entities: list[EntityLink], path: Path | None = None) -> int:
    """Replace the entity index for one persisted incident."""
    with connect(path) as db:
        db.execute("DELETE FROM entities WHERE incident_id = ?", (incident_id,))
        db.executemany(
            "INSERT INTO entities (incident_id, entity_type, entity_value, score) VALUES (?, ?, ?, ?)",
            [(incident_id, item.entity_type, item.entity, item.score) for item in entities],
        )
        return len(entities)


def find_entity(entity_type: str, entity_value: str, limit: int = 100, path: Path | None = None) -> list[dict]:
    """Find incidents linked to an exact normalized entity."""
    limit = max(1, min(limit, 1000))
    with connect(path) as db:
        rows = db.execute(
            """
            SELECT e.entity_type, e.entity_value, e.score,
                   i.id AS incident_id, i.recorded_at, i.source, i.severity,
                   i.category, i.title, i.event_count
            FROM entities e
            JOIN incidents i ON i.id = e.incident_id
            WHERE e.entity_type = ? AND e.entity_value = ?
            ORDER BY e.score DESC, i.recorded_at DESC, i.id DESC
            LIMIT ?
            """,
            (entity_type.lower(), entity_value, limit),
        ).fetchall()
        return [dict(row) for row in rows]


def top_entities(entity_type: str | None = None, limit: int = 25, path: Path | None = None) -> list[dict]:
    """Rank entities by linked incident count and accumulated correlation score."""
    limit = max(1, min(limit, 250))
    where = "WHERE entity_type = ?" if entity_type else ""
    params: list[object] = [entity_type.lower()] if entity_type else []
    params.append(limit)
    with connect(path) as db:
        rows = db.execute(
            f"""
            SELECT entity_type, entity_value,
                   COUNT(DISTINCT incident_id) AS incident_count,
                   SUM(score) AS total_score,
                   MAX(score) AS max_score
            FROM entities
            {where}
            GROUP BY entity_type, entity_value
            ORDER BY total_score DESC, incident_count DESC, entity_value
            LIMIT ?
            """,
            params,
        ).fetchall()
        return [dict(row) for row in rows]
