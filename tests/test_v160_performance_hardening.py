from __future__ import annotations

from pathlib import Path

from aegislog.multisource import MultiSourceState


def test_multisource_aggregates_arrivals_per_ingest_batch(tmp_path: Path) -> None:
    source = tmp_path / "events.log"
    state = MultiSourceState((source, tmp_path / "other.log"), window_size=100)

    state.ingest(source, [f"service: INFO event {index}\n" for index in range(50_000)], now=100.0)

    assert state.total_lines == 50_000
    assert len(state._arrivals) == 1
    assert state._arrivals[0] == (100.0, 50_000)


def test_multisource_arrival_history_has_hard_bucket_ceiling(tmp_path: Path) -> None:
    source = tmp_path / "events.log"
    state = MultiSourceState(
        (source, tmp_path / "other.log"),
        window_size=100,
        trend_seconds=3600,
        max_arrival_buckets=64,
    )

    for index in range(2_000):
        state._record_arrivals(float(index), 1)

    assert len(state._arrivals) <= 64
    assert sum(count for _, count in state._arrivals) == 2_000


def test_multisource_seen_fingerprints_have_hard_ceiling(tmp_path: Path) -> None:
    source = tmp_path / "events.log"
    state = MultiSourceState(
        (source, tmp_path / "other.log"),
        window_size=100,
        max_seen_fingerprints=32,
    )

    for index in range(200):
        state._seen[("LOW", "test", f"finding-{index}", f"evidence-{index}")] = float(index)
    state._bound_seen()

    assert len(state._seen) == 32
    assert min(state._seen.values()) == 168.0


def test_multisource_bounds_are_config_validated(tmp_path: Path) -> None:
    source = tmp_path / "events.log"
    try:
        MultiSourceState((source,), max_arrival_buckets=1)
    except ValueError as exc:
        assert "max_arrival_buckets" in str(exc)
    else:
        raise AssertionError("expected invalid arrival bucket ceiling to be rejected")
