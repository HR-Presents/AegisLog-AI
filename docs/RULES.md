# Detection rules

V0.2 ships a deliberately small, explainable local rule set covering repeated authentication failures, suspicious sudo/privilege events, selected suspicious web-request patterns, fatal/crash/OOM events, and generic errors/timeouts/denials.

Rules are signals rather than verdicts. A matching string can have a benign explanation, and a real incident may not match any built-in rule. Future rule packs should include an identifier, severity rationale, references, tests, and configurable thresholds where appropriate.

Repeated authentication failures are correlated by source IP. Five or more failures create a possible brute-force finding; twenty or more raise its severity. These defaults are intended for demonstrations and must become configurable before a stable production release.
