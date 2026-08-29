from __future__ import annotations

from pathlib import Path

from aegislog.multisource import MultiSourceState
from aegislog.realtime import RealtimeState
from aegislog.trends import TrendTracker


def test_tracks_failed_logins_errors_and_firewall_blocks_per_minute() -> None:
    tracker = TrendTracker(window_seconds=60)
    snapshot = tracker.ingest(
        [
            "sshd: Failed password for root from 203.0.113.4\n",
            "api: ERROR database timeout\n",
            "kernel: UFW BLOCK SRC=203.0.113.8\n",
        ],
        now=100.0,
    )
    assert snapshot.failed_logins_per_minute == 1.0
    assert snapshot.errors_per_minute == 2.0
    assert snapshot.firewall_blocks_per_minute == 1.0


def test_detects_short_window_spike_against_prior_baseline() -> None:
    tracker = TrendTracker(window_seconds=60)
    tracker.ingest(["sshd: Failed password for root\n"] * 2, now=100.0)
    snapshot = tracker.ingest(["sshd: Failed password for root\n"] * 4, now=110.0)
    failed = next(item for item in snapshot.metrics if item.name == "Failed logins")
    assert failed.current_per_minute == 6.0
    assert failed.baseline_per_minute == 2.0
    assert failed.deviation_ratio == 3.0
    assert failed.state == "SPIKE"
    assert snapshot.spike_count >= 1


def test_old_activity_expires_from_rate_window() -> None:
    tracker = TrendTracker(window_seconds=60)
    tracker.ingest(["kernel: UFW BLOCK SRC=203.0.113.8\n"] * 5, now=100.0)
    snapshot = tracker.snapshot(now=161.0)
    assert snapshot.firewall_blocks_per_minute == 0.0


def test_realtime_state_feeds_rate_tracker() -> None:
    state = RealtimeState(source="test.log")
    state.ingest(["sshd: Failed password for root\n"] * 3)
    snapshot = state.trend_tracker.snapshot()
    assert snapshot.failed_logins_per_minute == 3.0


def test_multisource_state_combines_rate_signals_across_sources() -> None:
    state = MultiSourceState(sources=(Path("auth.log"), Path("firewall.log")))
    state.ingest(Path("auth.log"), ["sshd: Failed password for root\n"] * 2)
    state.ingest(Path("firewall.log"), ["kernel: UFW BLOCK SRC=203.0.113.8\n"] * 3)
    snapshot = state.trend_tracker.snapshot()
    assert snapshot.failed_logins_per_minute == 2.0
    assert snapshot.firewall_blocks_per_minute == 3.0
