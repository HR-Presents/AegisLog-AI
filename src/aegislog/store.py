from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .config import config_dir


def store_path() -> Path:
    path = config_dir() / "incidents.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def save_incidents(source: str, incidents: list) -> Path:
    path = store_path()
    now = datetime.now(timezone.utc).isoformat()
    with path.open("a", encoding="utf-8") as handle:
        for incident in incidents:
            record = {
                "recorded_at": now,
                "source": source,
                "id": incident.id,
                "severity": incident.severity,
                "category": incident.category,
                "title": incident.title,
                "count": incident.count,
                "evidence": list(incident.evidence),
            }
            handle.write(json.dumps(record) + "\n")
    return path


def load_incidents(limit: int = 100) -> list[dict]:
    path = store_path()
    if not path.exists():
        return []
    records: list[dict] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records[-max(1, min(limit, 1000)):]
