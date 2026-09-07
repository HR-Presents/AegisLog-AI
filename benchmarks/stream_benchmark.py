from __future__ import annotations

import argparse
import os
import platform
import resource
import tempfile
import time
import tracemalloc
from pathlib import Path

from aegislog.streaming import analyze_stream


def _cpu_model() -> str:
    cpuinfo = Path("/proc/cpuinfo")
    if cpuinfo.exists():
        for line in cpuinfo.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.lower().startswith("model name") and ":" in line:
                return line.split(":", 1)[1].strip()
    return platform.processor() or "unknown"


def main() -> None:
    parser = argparse.ArgumentParser(description="AegisLog bounded-memory streaming benchmark")
    parser.add_argument("--lines", type=int, default=250_000)
    parser.add_argument("--chunk-size", type=int, default=2_000)
    args = parser.parse_args()
    if args.lines < 1 or args.chunk_size < 1:
        raise SystemExit("--lines and --chunk-size must be positive")

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "benchmark.log"
        with path.open("w", encoding="utf-8") as handle:
            for index in range(args.lines):
                handle.write("ERROR timeout from service\n" if index % 1000 == 0 else "INFO service healthy\n")
        dataset_bytes = path.stat().st_size

        tracemalloc.start()
        rss_before = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        start = time.perf_counter()
        summary = analyze_stream(path, chunk_size=args.chunk_size)
        elapsed = time.perf_counter() - start
        _, peak_python_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        rss_after = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        rate = summary.lines / elapsed if elapsed else 0

        print(
            "method=synthetic-line-stream "
            f"python={platform.python_version()} platform={platform.platform()} "
            f"cpu_count={os.cpu_count()} cpu_model={_cpu_model()!r}"
        )
        print(
            f"lines={summary.lines} dataset_bytes={dataset_bytes} chunks={summary.chunks} "
            f"chunk_size={args.chunk_size} seconds={elapsed:.3f} lines_per_second={rate:.0f}"
        )
        print(
            f"peak_python_bytes={peak_python_bytes} max_rss_before_kib={rss_before} "
            f"max_rss_after_kib={rss_after} truncated_lines={summary.truncated_lines} "
            f"dropped_findings={summary.dropped_findings} dropped_auth_events={summary.dropped_auth_events}"
        )
        print(
            "limitations=synthetic homogeneous data; hosted-runner measurements vary and do not represent "
            "production log mixes, storage latency, or sustained live ingestion"
        )


if __name__ == "__main__":
    main()
