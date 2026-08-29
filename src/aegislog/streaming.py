from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from .engine import Finding, analyze_lines


@dataclass(frozen=True)
class StreamSummary:
    lines: int
    chunks: int
    findings: tuple[Finding, ...]
    severities: dict[str, int]


def analyze_stream(path: Path, chunk_size: int = 2000, max_findings: int = 5000) -> StreamSummary:
    """Analyze a file incrementally so large inputs do not require a full read into memory."""
    if chunk_size < 1: raise ValueError("chunk_size must be positive")
    total = 0; chunks = 0; findings: list[Finding] = []; counts: Counter[str] = Counter(); batch: list[str] = []
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            total += 1; batch.append(line)
            if len(batch) >= chunk_size:
                chunks += 1
                current = analyze_lines(batch); counts.update(item.severity for item in current)
                if len(findings) < max_findings: findings.extend(current[: max_findings - len(findings)])
                batch.clear()
        if batch:
            chunks += 1
            current = analyze_lines(batch); counts.update(item.severity for item in current)
            if len(findings) < max_findings: findings.extend(current[: max_findings - len(findings)])
    return StreamSummary(total, chunks, tuple(findings), dict(counts))
