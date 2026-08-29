# Anomaly scoring

V0.2 anomaly scoring is a local frequency heuristic over normalized `service:level` event classes. Rare classes receive a higher score when the input contains enough events.

The score is not a probability of attack. It answers a narrower question: "Is this event class unusual inside this sample?" Historical baselines, seasonality, host-specific behavior, and richer features are roadmap items.
