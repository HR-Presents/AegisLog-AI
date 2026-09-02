from __future__ import annotations

import argparse
import time

from aegislog.realtime import RealtimeState


def main() -> None:
    parser = argparse.ArgumentParser(description="AegisLog bounded live-state benchmark")
    parser.add_argument("--lines", type=int, default=100_000)
    parser.add_argument("--window", type=int, default=1_000)
    parser.add_argument("--batch-size", type=int, default=1_000)
    args = parser.parse_args()

    if args.lines < 1 or args.window < 20 or args.batch_size < 1:
        raise SystemExit("lines and batch-size must be positive; window must be at least 20")

    state = RealtimeState(source="benchmark.log", window_size=args.window)
    template = "api: ERROR timeout from service\n"
    remaining = args.lines
    start = time.perf_counter()
    while remaining:
        size = min(args.batch_size, remaining)
        state.ingest([template] * size)
        remaining -= size
    elapsed = time.perf_counter() - start
    rate = state.total_lines / elapsed if elapsed else 0.0
    print(
        f"lines={state.total_lines} window={state.rolling_count}/{state.window_size} "
        f"trend_buckets={len(state.trend_tracker._events)} seconds={elapsed:.3f} "
        f"lines_per_second={rate:.0f}"
    )


if __name__ == "__main__":
    main()
