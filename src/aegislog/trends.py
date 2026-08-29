from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field


@dataclass(frozen=True)
class TrendMetric:
    name: str
    current_per_minute: float
    baseline_per_minute: float
    deviation_ratio: float
    state: str


@dataclass(frozen=True)
class TrendSnapshot:
    window_seconds: int
    failed_logins_per_minute: float
    errors_per_minute: float
    firewall_blocks_per_minute: float
    metrics: tuple[TrendMetric, ...]

    @property
    def spike_count(self) -> int:
        return sum(1 for item in self.metrics if item.state == "SPIKE")


@dataclass
class TrendTracker:
    window_seconds: int = 60
    alpha: float = 0.20
    _events: deque[tuple[float, bool, bool, bool]] = field(default_factory=deque)
    _baseline: dict[str, float] = field(default_factory=dict)
    _latest: TrendSnapshot | None = None

    def __post_init__(self) -> None:
        if self.window_seconds < 10:
            raise ValueError("window_seconds must be at least 10")
        if not 0.0 < self.alpha <= 1.0:
            raise ValueError("alpha must be within (0, 1]")

    @staticmethod
    def _classify(line: str) -> tuple[bool, bool, bool]:
        text = line.lower()
        failed_login = any(
            marker in text
            for marker in (
                "failed password",
                "authentication failure",
                "login failed",
                "invalid user",
                "failed login",
            )
        )
        error = any(marker in text for marker in (" error ", "error:", "failed", "failure", "exception", "timeout"))
        firewall = any(
            marker in text
            for marker in (
                "ufw block",
                "firewall block",
                "blocked connection",
                "action=block",
                "action=deny",
                " denied ",
            )
        )
        return failed_login, error, firewall

    def _trim(self, now: float) -> None:
        cutoff = now - self.window_seconds
        while self._events and self._events[0][0] < cutoff:
            self._events.popleft()

    def ingest(self, lines: list[str], now: float | None = None) -> TrendSnapshot:
        stamp = time.monotonic() if now is None else now
        self._trim(stamp)
        for line in lines:
            auth, error, firewall = self._classify(line)
            self._events.append((stamp, auth, error, firewall))
        self._trim(stamp)
        current = self._rates()
        metrics: list[TrendMetric] = []
        minimums = {"Failed logins": 5.0, "Errors": 6.0, "Firewall blocks": 5.0}
        for name, value in current.items():
            baseline = self._baseline.get(name, value)
            ratio = value / baseline if baseline > 0 else (999.0 if value > 0 else 1.0)
            spike = value >= minimums[name] and baseline > 0 and ratio >= 2.0 and value - baseline >= 3.0
            state = "SPIKE" if spike else ("ELEVATED" if value >= minimums[name] else "NORMAL")
            metrics.append(TrendMetric(name, value, baseline, ratio, state))
            self._baseline[name] = value if name not in self._baseline else (self.alpha * value + (1.0 - self.alpha) * baseline)
        self._latest = TrendSnapshot(
            self.window_seconds,
            current["Failed logins"],
            current["Errors"],
            current["Firewall blocks"],
            tuple(metrics),
        )
        return self._latest

    def _rates(self) -> dict[str, float]:
        scale = 60.0 / float(self.window_seconds)
        failed = sum(1 for _, auth, _, _ in self._events if auth) * scale
        errors = sum(1 for _, _, error, _ in self._events if error) * scale
        firewall = sum(1 for _, _, _, blocked in self._events if blocked) * scale
        return {
            "Failed logins": failed,
            "Errors": errors,
            "Firewall blocks": firewall,
        }

    def snapshot(self, now: float | None = None) -> TrendSnapshot:
        stamp = time.monotonic() if now is None else now
        self._trim(stamp)
        current = self._rates()
        metrics: list[TrendMetric] = []
        for name, value in current.items():
            baseline = self._baseline.get(name, value)
            ratio = value / baseline if baseline > 0 else (999.0 if value > 0 else 1.0)
            minimum = 5.0 if name != "Errors" else 6.0
            state = "SPIKE" if value >= minimum and baseline > 0 and ratio >= 2.0 and value - baseline >= 3.0 else ("ELEVATED" if value >= minimum else "NORMAL")
            metrics.append(TrendMetric(name, value, baseline, ratio, state))
        return TrendSnapshot(
            self.window_seconds,
            current["Failed logins"],
            current["Errors"],
            current["Firewall blocks"],
            tuple(metrics),
        )
