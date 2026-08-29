from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass

from .parsers import Event


@dataclass(frozen=True)
class Anomaly:
    score: float
    key: str
    reason: str


def score_events(events: list[Event]) -> list[Anomaly]:
    """Lightweight local frequency anomaly scoring; no external model required."""
    if not events:
        return []
    keys = [f"{e.service or 'unknown'}:{(e.level or 'unknown').lower()}" for e in events if e.message]
    counts = Counter(keys)
    total = max(len(keys), 1)
    anomalies: list[Anomaly] = []
    for key, count in counts.items():
        ratio = count / total
        rarity = -math.log10(max(ratio, 1e-9))
        score = min(100.0, 20.0 + rarity * 30.0)
        if count <= 3 and total >= 10 and score >= 45:
            anomalies.append(Anomaly(round(score, 1), key, f"Rare event class: {count}/{total} events"))
    return sorted(anomalies, key=lambda a: a.score, reverse=True)
