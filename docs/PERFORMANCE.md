# Performance notes

V0.2 prioritizes clarity over large-scale throughput. `analyze` currently reads a file into memory, `scan` limits discovery to 100 candidate files, terminal finding output is bounded, and AI prompt construction is bounded by configured event counts.

Before V1.0, file analysis should move to streaming/chunked processing, correlation should preserve bounded state, and benchmarks should cover large files, malformed lines, and high-cardinality sources.
