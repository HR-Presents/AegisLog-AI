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


INTERESTING_LEVELS = {"warning", "error", "critical"}


def score_events(events: list[Event]) -> list[Anomaly]:
    """Lightweight local anomaly scoring focused on rare concerning event classes."""
    relevant = [e for e in events if e.message and (e.level or "").lower() in INTERESTING_LEVELS]
    if not relevant:
        return []

    keys = [f"{e.service or 'unknown'}:{(e.level or 'unknown').lower()}" for e in relevant]
    counts = Counter(keys)
    total_events = max(sum(1 for e in events if e.message), 1)
    anomalies: list[Anomaly] = []

    for key, count in counts.items():
        ratio = count / total_events
        rarity = -math.log10(max(ratio, 1e-9))
        score = min(100.0, 30.0 + rarity * 32.0)
        if count <= 3 and total_events >= 10 and score >= 50:
            anomalies.append(
                Anomaly(
                    round(score, 1),
                    key,
                    f"Rare concerning event class: {count}/{total_events} total events",
                )
            )

    return sorted(anomalies, key=lambda a: a.score, reverse=True)
