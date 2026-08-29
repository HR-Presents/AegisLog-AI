# Incident correlation

`aegislog incidents FILE` groups deterministic findings by category and assigns each group a stable short ID derived from its category and leading finding. The incident severity is the highest severity among grouped findings.

This is deliberately simple in V0.2. Future versions should correlate by time window, host, user, process, source address, service, and causal sequence, then persist incident state between runs.
