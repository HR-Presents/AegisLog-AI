# Parsers

The parser layer normalizes input into `Event(raw, source, level, service, message)`.

V0.2 recognizes generic text, a common syslog shape, JSON/journald-style objects, and common HTTP access-log records. Unknown input safely falls back to generic text instead of being rejected.

Future adapters can enrich the same event model with structured metadata while keeping rule, anomaly, correlation, reporting, and AI layers independent of source format.
