from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field

from rich import box
from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .theme import ACCENT, ACCENT_SOFT, INFO, MUTED, NEUTRAL, SECONDARY, SUCCESS, WARNING


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
    max_buckets: int = 4096
    _events: deque[tuple[float, int, int, int]] = field(default_factory=deque)
    _baseline: dict[str, float] = field(default_factory=dict)
    _latest: TrendSnapshot | None = None

    def __post_init__(self) -> None:
        if self.window_seconds < 10: raise ValueError("window_seconds must be at least 10")
        if not 0.0 < self.alpha <= 1.0: raise ValueError("alpha must be within (0, 1]")
        if self.max_buckets < 64: raise ValueError("max_buckets must be at least 64")

    @staticmethod
    def _classify(line: str) -> tuple[bool, bool, bool]:
        text = line.lower(); failed_login = any(marker in text for marker in ("failed password", "authentication failure", "login failed", "invalid user", "failed login")); error = any(marker in text for marker in (" error ", "error:", "failed", "failure", "exception", "timeout")); firewall = any(marker in text for marker in ("ufw block", "firewall block", "blocked connection", "action=block", "action=deny", " denied ")); return failed_login, error, firewall

    def _trim(self, now: float) -> None:
        cutoff = now - self.window_seconds
        while self._events and self._events[0][0] < cutoff: self._events.popleft()

    def _append_bucket(self, stamp: float, failed: int, errors: int, firewall: int) -> None:
        if not (failed or errors or firewall): return
        if self._events and self._events[-1][0] == stamp:
            previous = self._events.pop(); self._events.append((stamp, previous[1] + failed, previous[2] + errors, previous[3] + firewall))
        else: self._events.append((stamp, failed, errors, firewall))
        while len(self._events) > self.max_buckets:
            oldest = self._events.popleft()
            if not self._events: self._events.append(oldest); break
            next_bucket = self._events.popleft(); self._events.appendleft((next_bucket[0], oldest[1] + next_bucket[1], oldest[2] + next_bucket[2], oldest[3] + next_bucket[3]))

    def ingest(self, lines: list[str], now: float | None = None) -> TrendSnapshot:
        stamp = time.monotonic() if now is None else now; self._trim(stamp); failed = errors = firewall = 0
        for line in lines:
            auth, error, blocked = self._classify(line); failed += int(auth); errors += int(error); firewall += int(blocked)
        self._append_bucket(stamp, failed, errors, firewall); self._trim(stamp); current = self._rates(); metrics: list[TrendMetric] = []; minimums = {"Failed logins": 5.0, "Errors": 6.0, "Firewall blocks": 5.0}
        for name, value in current.items():
            baseline = self._baseline.get(name, value); ratio = value / baseline if baseline > 0 else (999.0 if value > 0 else 1.0); spike = value >= minimums[name] and baseline > 0 and ratio >= 2.0 and value - baseline >= 3.0; state = "SPIKE" if spike else ("ELEVATED" if value >= minimums[name] else "NORMAL"); metrics.append(TrendMetric(name, value, baseline, ratio, state)); self._baseline[name] = value if name not in self._baseline else (self.alpha * value + (1.0 - self.alpha) * baseline)
        self._latest = TrendSnapshot(self.window_seconds, current["Failed logins"], current["Errors"], current["Firewall blocks"], tuple(metrics)); return self._latest

    def _rates(self) -> dict[str, float]:
        scale = 60.0 / float(self.window_seconds); return {"Failed logins": sum(a for _, a, _, _ in self._events) * scale, "Errors": sum(e for _, _, e, _ in self._events) * scale, "Firewall blocks": sum(b for _, _, _, b in self._events) * scale}

    def snapshot(self, now: float | None = None) -> TrendSnapshot:
        stamp = time.monotonic() if now is None else now; self._trim(stamp); current = self._rates(); metrics: list[TrendMetric] = []
        for name, value in current.items():
            baseline = self._baseline.get(name, value); ratio = value / baseline if baseline > 0 else (999.0 if value > 0 else 1.0); minimum = 5.0 if name != "Errors" else 6.0; state = "SPIKE" if value >= minimum and baseline > 0 and ratio >= 2.0 and value - baseline >= 3.0 else ("ELEVATED" if value >= minimum else "NORMAL"); metrics.append(TrendMetric(name, value, baseline, ratio, state))
        return TrendSnapshot(self.window_seconds, current["Failed logins"], current["Errors"], current["Firewall blocks"], tuple(metrics))


def _state_style(state: str) -> str:
    if state == "SPIKE": return "bold bright_red"
    if state == "ELEVATED": return WARNING
    return SUCCESS


def _spark(current: float, baseline: float, width: int = 12) -> Text:
    maximum = max(current, baseline, 1.0); current_n = min(width, round((current / maximum) * width)); base_n = min(width, round((baseline / maximum) * width)); text = Text()
    for index in range(1, width + 1):
        if index <= current_n: text.append("=", style=ACCENT if index <= base_n else WARNING)
        elif index <= base_n: text.append("-", style=SECONDARY)
        else: text.append(" ")
    return text


def render_trends(snapshot: TrendSnapshot, metric_names: tuple[str, ...] | None = None) -> Panel:
    allowed = set(metric_names or ()); metrics = [m for m in snapshot.metrics if not allowed or m.name in allowed]; table = Table(expand=True, box=None, padding=(0, 1)); table.add_column("SIGNAL", ratio=2, style=NEUTRAL); table.add_column("ACTIVITY", width=14); table.add_column("CURRENT", width=9, justify="right"); table.add_column("BASE", width=9, justify="right", style=SECONDARY); table.add_column("DELTA", width=7, justify="right"); table.add_column("STATE", width=9)
    for metric in metrics:
        ratio = f"{metric.deviation_ratio:.1f}x" if metric.deviation_ratio < 100 else ">99x"; style = _state_style(metric.state); table.add_row(metric.name, _spark(metric.current_per_minute, metric.baseline_per_minute), Text(f"{metric.current_per_minute:.1f}/m", style=style if metric.state != "NORMAL" else INFO), Text(f"{metric.baseline_per_minute:.1f}/m", style=SECONDARY), Text(ratio, style=style if metric.state != "NORMAL" else MUTED), Text(metric.state, style=style))
    if not metrics: table.add_row("No profile metrics", Text("-" * 12, style=SECONDARY), "0.0/m", Text("0.0/m", style=SECONDARY), "1.0x", Text("NORMAL", style=SUCCESS))
    legend = Text("= current/overlap", style=ACCENT); legend.append("   - baseline", style=SECONDARY)
    return Panel(Group(table, Text(""), legend), title=Text(f" RATE & BASELINE  |  {snapshot.window_seconds}s WINDOW ", style=f"bold {SECONDARY}"), title_align="left", box=box.ROUNDED, border_style=ACCENT_SOFT, padding=(0, 1))
