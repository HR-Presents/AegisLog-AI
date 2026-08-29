from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from .engine import Finding, analyze_lines


@dataclass
class RollingAnalyzer:
    """Stateful rolling analysis for live telemetry correlation."""

    window_size: int = 200
    _lines: deque[str] = field(default_factory=deque)
    _fingerprints: set[tuple[str, str, str, str]] = field(default_factory=set)

    def __post_init__(self) -> None:
        if self.window_size < 1:
            raise ValueError("window_size must be positive")
        self._lines = deque(self._lines, maxlen=self.window_size)

    def push(self, line: str) -> list[Finding]:
        self._lines.append(line)
        findings = analyze_lines(list(self._lines))
        fresh: list[Finding] = []
        active: set[tuple[str, str, str, str]] = set()
        for item in findings:
            fingerprint = (item.severity, item.category, item.title, item.evidence)
            active.add(fingerprint)
            if fingerprint not in self._fingerprints:
                fresh.append(item)
        self._fingerprints = active
        return fresh

    @property
    def buffered_lines(self) -> int:
        return len(self._lines)
