# Current limitations

AegisLog AI V0.2 is an early foundation, not a SIEM replacement. It does not currently persist baselines across runs, inspect packet contents, automatically collect privileged logs, perform malware scanning, execute remediation, or prove that a security incident occurred.

The anomaly scorer uses event-class rarity inside the supplied sample rather than a historical machine-learning baseline. `ask` is local and deterministic in V0.2; remote and local LLM provider adapters remain roadmap work. Parsers cover common formats but are not yet exhaustive.

These limitations are intentional so the project can keep a clear evidence model while functionality expands.
