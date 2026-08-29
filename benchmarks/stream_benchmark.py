from __future__ import annotations

import argparse
import tempfile
import time
from pathlib import Path

from aegislog.streaming import analyze_stream


def main() -> None:
    parser = argparse.ArgumentParser(description="AegisLog bounded-memory streaming benchmark")
    parser.add_argument("--lines", type=int, default=250_000)
    parser.add_argument("--chunk-size", type=int, default=2_000)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "benchmark.log"
        with path.open("w", encoding="utf-8") as handle:
            for index in range(args.lines):
                handle.write("ERROR timeout from service\n" if index % 1000 == 0 else "INFO service healthy\n")
        start = time.perf_counter()
        summary = analyze_stream(path, chunk_size=args.chunk_size)
        elapsed = time.perf_counter() - start
        rate = summary.lines / elapsed if elapsed else 0
        print(f"lines={summary.lines} chunks={summary.chunks} seconds={elapsed:.3f} lines_per_second={rate:.0f}")


if __name__ == "__main__":
    main()
