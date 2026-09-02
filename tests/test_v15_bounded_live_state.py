from __future__ import annotations

from pathlib import Path

from aegislog.multisource import MultiSourceState
from aegislog.realtime import RealtimeState
from aegislog.trends import TrendTracker


def test_trend_tracker_aggregates_large_batches_without_per_line_history() -> None:
    tracker = TrendTracker(window_seconds=60)
    lines = ["sshd: Failed password for root\n"] * 50_000
    snapshot = tracker.ingest(lines, now=100.0)

    assert len(tracker._events) == 1
    assert snapshot.failed_logins_per_minute == 50_000.0
    assert snapshot.errors_per_minute == 50_000.0


def test_trend_tracker_enforces_hard_bucket_ceiling() -> None:
    tracker = TrendTracker(window_seconds=3600, max_buckets=128)
    for index in range(2_000):
        tracker.ingest(["api: ERROR timeout\n"], now=float(index))

    assert len(tracker._events) <= 128
    assert tracker.snapshot(now=1999.0).errors_per_minute > 0


def test_realtime_rolling_analysis_window_stays_bounded() -> None:
    state = RealtimeState(source="stress.log", window_size=200)
    state.ingest([f"service: INFO event {index}\n" for index in range(10_000)], now=100.0)

    assert state.total_lines == 10_000
    assert state.rolling_count == 200
    assert len(state.lines) == 200
    assert len(state.events) == 200


def test_multisource_rolling_analysis_window_stays_bounded(tmp_path: Path) -> None:
    first = tmp_path / "first.log"
    second = tmp_path / "second.log"
    state = MultiSourceState((first, second), window_size=200)
    state.ingest(first, [f"service: INFO event {index}\n" for index in range(10_000)], now=100.0)

    assert state.total_lines == 10_000
    assert state.rolling_count == 200
    assert len(state.raw_lines) == 200
    assert len(state.events) == 200
