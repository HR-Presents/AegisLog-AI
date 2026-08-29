# Why local-first?

Logs frequently contain sensitive operational details. Keeping parsing, detection, anomaly scoring, correlation, and baseline investigation local reduces unnecessary disclosure and keeps the tool useful in restricted environments.

AI is an enhancement layer rather than a dependency. This also improves reliability: a network outage, provider outage, expired key, or model change should not disable core detection.
