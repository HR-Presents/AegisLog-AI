from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime

from .parsers import parse_line


@dataclass(frozen=True)
class BehaviorDelta:
    bucket: str
    key: str
    baseline: float
    current: int
    ratio: float


def _hour(line: str) -> str:
    event = parse_line(line)
    value = getattr(event, "timestamp", None)
    if isinstance(value, datetime): return f"{value.hour:02d}:00"
    text = str(value or "")
    for token in text.split():
        if len(token) >= 5 and token[2] == ":" and token[:2].isdigit(): return f"{token[:2]}:00"
    return "unknown"


def profile(lines: list[str]) -> Counter[tuple[str, str]]:
    counts: Counter[tuple[str, str]] = Counter()
    for line in lines:
        event = parse_line(line)
        level = str(getattr(event, "level", "unknown")); source = str(getattr(event, "source", "unknown"))
        counts[("hour", _hour(line))] += 1; counts[("level", level)] += 1; counts[("source", source)] += 1
    return counts


def compare_windows(baseline_windows: list[list[str]], current: list[str], minimum_current: int = 3) -> list[BehaviorDelta]:
    if not baseline_windows: return []
    profiles = [profile(window) for window in baseline_windows]; now = profile(current); keys = set(now)
    for item in profiles: keys.update(item)
    results: list[BehaviorDelta] = []
    for bucket, key in keys:
        average = sum(item[(bucket, key)] for item in profiles) / len(profiles); value = now[(bucket, key)]
        if value < minimum_current: continue
        ratio = value / max(average, 0.5)
        if ratio >= 2.0: results.append(BehaviorDelta(bucket, key, average, value, ratio))
    return sorted(results, key=lambda item: (-item.ratio, -item.current, item.bucket, item.key))
