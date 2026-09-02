# Performance notes

AegisLog is designed for local, defensive analysis with bounded terminal and live-monitoring state.

Current behavior:

- Static streaming analysis processes large files in chunks where supported instead of retaining full input indefinitely.
- Real-time and multi-source dashboards keep only their configured rolling analysis windows in memory.
- V1.5 aggregates live trend samples per ingest cycle rather than retaining one trend-history record per input line.
- Trend history has a hard bucket ceiling (`4096` by default) to prevent unusually high-frequency callers from growing live telemetry history without bound.
- Recent findings and live alert feeds already use bounded deques for terminal presentation.
- `scan` limits discovery to 100 candidate files, terminal finding output is bounded, and AI prompt construction is bounded by configured event counts.

The trend bucket ceiling is a resilience guard for extreme ingest-call rates. Normal polling intervals stay far below that ceiling. If the ceiling is reached, older adjacent buckets are compacted so aggregate signal counts remain available while memory use stays bounded.

Benchmarks:

```bash
python benchmarks/stream_benchmark.py --lines 250000 --chunk-size 2000
python benchmarks/live_state_benchmark.py --lines 100000 --window 1000 --batch-size 1000
```

Performance work should preserve AegisLog's read-only defensive model and prioritize predictable resource use over unbounded historical retention.
