# Next engineering milestone

V0.3 should prioritize real provider/collector adapters rather than adding more presentation layers:

1. streaming/chunked analyzer for large logs
2. journald collector with bounded queries
3. Docker log collector
4. persisted incident store and timelines
5. configurable thresholds/allowlists
6. opt-in provider-neutral LLM execution with explicit remote-data consent
7. local-model adapter
8. parser/rule plugin contract
9. benchmark and false-positive corpus

This sequence keeps the terminal product useful while preserving its evidence and privacy boundaries.
