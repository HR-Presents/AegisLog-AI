# Detection pipeline

1. Read permitted log text with replacement for malformed UTF-8.
2. Remove terminal control sequences and redact common secret patterns.
3. Normalize supported structured formats into events.
4. Apply deterministic security/operational rules.
5. Correlate repeated authentication failures by source address.
6. Score rare normalized event classes as anomaly leads.
7. Group findings into investigation incidents.
8. Render bounded terminal output or a JSON report.
9. For question-driven investigation, summarize evidence locally; future external providers receive only explicitly opted-in, minimized, redacted context.

This ordering keeps evidence collection and deterministic detection independent from generative AI.
