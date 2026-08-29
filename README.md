# AegisLog AI

**Terminal-first defensive log intelligence and investigation.**

AegisLog AI analyzes Linux, authentication, web, system, Docker and application telemetry using deterministic detections, anomaly scoring, incident correlation, behavioral baselines, persistent investigation state, declarative rule packs, entity correlation, bounded-memory streaming, stateful live analysis, and optional LLM-assisted explanation. Core analysis works without an AI service.

## Quick start

```bash
git clone https://github.com/HR-Presents/AegisLog-AI.git
cd AegisLog-AI

# Windows
powershell -ExecutionPolicy Bypass -File .\install.ps1
.\aegislog.cmd doctor
.\aegislog.cmd analyze examples\auth.log

# Linux / macOS
sh install.sh
./aegislog doctor
./aegislog analyze examples/auth.log
```

The installers create a private `.aegislog-venv` inside the AegisLog folder instead of depending on the user's global Python `Scripts` directory being on `PATH`. Windows also creates `OPEN_AEGISLOG_TERMINAL.bat`, which opens a ready command prompt in the product folder. Linux/macOS creates `OPEN_AEGISLOG_TERMINAL.sh`.

## Terminal dashboard

`analyze` now opens the complete AegisLog terminal dashboard after analysis:

```bash
aegislog analyze auth.log
```

The dashboard shows lines analyzed, risk state, severity counts, finding categories, log levels, top services, correlated incidents, anomaly scores, detected findings and supporting evidence in one terminal view.

The same dashboard can be opened explicitly:

```bash
aegislog dashboard auth.log
```

A spinner is shown while the file is analyzed, then the final investigation dashboard remains in the terminal for review. Log-derived values are rendered as literal text so hostile Rich markup is not interpreted as terminal formatting.

## Persistent entity investigation

```bash
aegislog index-entities auth.log
aegislog entity ip 203.0.113.7
aegislog entity user admin
aegislog entity-top
aegislog entity-top --entity-type ip
```

`index-entities` persists correlated incidents and builds a searchable local entity graph. Analysts can pivot from an IP, user, host, service, or container to historical incidents and rank repeatedly observed entities.

## Scale and behavioral correlation

```bash
aegislog stream huge-server.log --chunk-size 2000
aegislog entities auth.log
aegislog behavior --baseline monday.log --baseline tuesday.log --current today.log
```

`stream` analyzes large files incrementally with bounded retained findings. `entities` performs immediate correlation without persistence. `behavior` compares current telemetry with multiple historical windows.

## SOC-style workflow

```bash
aegislog incidents auth.log --persist
aegislog timeline
aegislog hunt --severity HIGH
aegislog hunt --query "authentication"
aegislog incident 1
aegislog indicators auth.log
aegislog baseline normal.log current.log
```

Persisted investigations use SQLite with versioned schema migrations.

## Extensible detection rules

AegisLog loads declarative JSON rule packs from its `rules.d` configuration directory. `aegislog plugins` displays loaded packs and validation errors. Python files in the rule directory are not imported or executed.

```json
{"rules":[{"id":"custom-01","severity":"HIGH","category":"application","title":"Sensitive service failure","pattern":"payment-worker.*fatal","recommendation":"Review the affected worker and surrounding telemetry."}]}
```

## Live and system telemetry

```bash
aegislog watch /var/log/auth.log --window 200
aegislog collect journal --lines 500 --output journal.log
aegislog collect journal --target ssh.service --output ssh.log
aegislog collect docker --target my-container --output container.log
```

`watch` maintains a bounded rolling correlation window, allowing repeated events to be detected across incoming lines instead of treating every line independently. Collectors remain bounded and read-only.

## Ask AegisLog

```bash
aegislog ask "What are the strongest security signals?" examples/auth.log --local

aegislog config --provider ollama --model llama3.2
aegislog ask "What likely happened?" examples/auth.log
```

Remote compatible providers use environment-based credentials. Provider context is minimized and redacted, telemetry is explicitly untrusted, private-network remote endpoints are rejected, and redirects are disabled. See `docs/AI_PROVIDERS.md`.

## Reports

```bash
aegislog report auth.log --output report.json
aegislog report auth.log --output report.md
aegislog report auth.log --output report.html
```

JSON reports include a schema version, tool version and generation timestamp. HTML report fields escape untrusted log-derived values.

## Performance benchmark

```bash
python benchmarks/stream_benchmark.py --lines 250000 --chunk-size 2000
```

The benchmark is for reproducible regression comparison rather than marketing performance claims.

## Main commands

`analyze`, `dashboard`, `threats`, `anomalies`, `incidents`, `history`, `incident`, `timeline`, `hunt`, `indicators`, `baseline`, `plugins`, `stream`, `entities`, `behavior`, `index-entities`, `entity`, `entity-top`, `watch`, `collect`, `ask`, `report`, `scan`, `config`, and `doctor`.

## Security model

AegisLog is defensive tooling. Findings, indicators, correlations and behavioral deltas are investigative signals, not proof of compromise. Log-derived terminal text is treated as untrusted and escaped/sanitized. The tool does not perform exploitation, automatic remediation, privilege escalation, service changes, firewall changes, or account modifications.

## Development

```bash
pip install -e '.[dev]'
pytest
ruff check .
bandit -q -r src
python -m build
twine check dist/*
```

## Release status

V1.0.0 is the stable public baseline. The `feature/v1.1-terminal-dashboard` branch develops the improved customer installation and terminal-dashboard experience and must pass CI/security/package checks before release.

## License

MIT
