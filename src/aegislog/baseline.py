from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from .parsers import parse_line


@dataclass(frozen=True)
class BaselineDelta:
    key: str
    baseline: int
    current: int
    ratio: float


def _counts(lines: list[str]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for line in lines:
        event = parse_line(line)
        key = f"{event.source}:{event.level}"
        counts[key] += 1
    return counts


def compare(baseline_lines: list[str], current_lines: list[str]) -> list[BaselineDelta]:
    before = _counts(baseline_lines)
    after = _counts(current_lines)
    results: list[BaselineDelta] = []
    for key in sorted(set(before) | set(after)):
        old = before[key]
        new = after[key]
        ratio = new / max(old, 1)
        if new != old:
            results.append(BaselineDelta(key, old, new, ratio))
    return sorted(results, key=lambda item: (item.ratio, item.current - item.baseline), reverse=True)
