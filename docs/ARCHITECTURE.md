# Architecture

```text
                    +----------------------+
files / streams --->| ingestion + parsers  |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | normalization/event  |
                    +----------+-----------+
                               |
                  +------------+-------------+
                  |                          |
                  v                          v
        +------------------+       +------------------+
        | deterministic    |       | anomaly scoring  |
        | detection rules  |       | (local)          |
        +--------+---------+       +--------+---------+
                 |                          |
                 +------------+-------------+
                              v
                    +----------------------+
                    | incident correlation |
                    +----------+-----------+
                               |
                    +----------+-----------+
                    |                      |
                    v                      v
              terminal/report       investigation AI
                                      abstraction
                                           |
                                      redaction first
```

## Trust boundaries

Raw logs are local input. Deterministic detection, parsing, anomaly scoring, correlation, and the V0.2 `ask` implementation are local. Future remote model integrations must use minimized, redacted context and must be optional. API keys must be read from environment variables or secure platform facilities, never written to project configuration by default.

## Detection philosophy

AegisLog separates observations from conclusions. Rules identify explicit patterns; anomaly scoring highlights unusual event classes; correlation groups related findings. None of these alone proves malicious activity. This distinction should remain visible in every future AI response and report.
