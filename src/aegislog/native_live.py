from __future__ import annotations

import hashlib
from collections import deque
from dataclasses import dataclass, field

from .native_collectors import collect


@dataclass
class NativeLivePoller:
    source: str
    limit: int = 300
    channel: str = "System"
    container: str = ""
    seen_limit: int = 10000
    _seen_order: deque[str] = field(default_factory=deque)
    _seen: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        self.source = self.source.strip().lower()
        self.limit = max(1, min(int(self.limit), 5000))
        self.seen_limit = max(self.limit * 2, int(self.seen_limit))

    @staticmethod
    def _fingerprint(line: str) -> str:
        return hashlib.sha256(line.encode("utf-8", errors="replace")).hexdigest()

    def _remember(self, fingerprint: str) -> None:
        if fingerprint in self._seen:
            return
        self._seen.add(fingerprint)
        self._seen_order.append(fingerprint)
        while len(self._seen_order) > self.seen_limit:
            expired = self._seen_order.popleft()
            self._seen.discard(expired)

    def poll(self) -> list[str]:
        lines = collect(
            self.source,
            limit=self.limit,
            channel=self.channel,
            container=self.container,
        )
        fresh: list[str] = []
        for line in lines:
            fingerprint = self._fingerprint(line)
            if fingerprint not in self._seen:
                fresh.append(line)
            self._remember(fingerprint)
        return fresh

    def prime(self, include_existing: bool = False) -> list[str]:
        lines = collect(
            self.source,
            limit=self.limit,
            channel=self.channel,
            container=self.container,
        )
        for line in lines:
            self._remember(self._fingerprint(line))
        return lines if include_existing else []
