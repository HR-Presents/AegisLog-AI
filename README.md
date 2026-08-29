# AegisLog AI

**Terminal-first defensive log intelligence and investigation.**

AegisLog AI analyzes Linux, authentication, web, system, Docker and application telemetry using deterministic detections, anomaly scoring, incident correlation, historical baselines, persistent investigation state, declarative local rule packs, defensive indicator extraction, entity correlation, bounded-memory streaming analysis, and optional LLM-assisted explanation. Core analysis works without an AI service.

## Quick start

```bash
git clone https://github.com/HR-Presents/AegisLog-AI.git
cd AegisLog-AI
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .

aegislog doctor
aegislog analyze examples/auth.log
aegislog incidents examples/auth.log --persist
aegislog timeline
```

## Scale and correlation

```bash
aegislog stream huge-server.log --chunk-size 2000
aegislog entities auth.log
aegislog behavior --baseline monday.log --baseline tuesday.log --current today.log
```

`stream` analyzes large files incrementally and retains only a bounded number of findings in memory while still counting all detected severities. `entities` ranks correlated IP, user, host, service, and container identities found in rule-backed evidence. `behavior` compares the current sample against multiple historical windows and surfaces large source, level, and time-profile changes.

## SOC-style investigation workflow

```bash
aegislog incidents auth.log --persist
aegislog timeline
aegislog hunt --severity HIGH
aegislog hunt --query "authentication"
aegislog incident 1
aegislog indicators auth.log
aegislog baseline normal.log current.log
```

Persisted incidents use a local SQLite database under the AegisLog configuration directory. The database now uses versioned schema migrations so future releases can evolve local investigation state without replacing the database.

## Extensible detection rules

AegisLog loads optional declarative JSON rule packs from its `rules.d` configuration directory. Run `aegislog plugins` to inspect loaded packs and errors. A pack contains a `rules` list; each rule provides `id`, `severity`, `category`, `title`, `pattern`, and `recommendation`. Broken packs are isolated instead of preventing the core analyzer from running. Python files in `rules.d` are not imported or executed.

```json
{"rules":[{"id":"custom-01","severity":"HIGH","category":"application","title":"Sensitive service failure","pattern":"payment-worker.*fatal","recommendation":"Review the affected worker and surrounding telemetry."}]}
```

## Live and system telemetry

```bash
aegislog watch /var/log/auth.log
aegislog collect journal --lines 500 --output journal.log
aegislog collect journal --target ssh.service --output ssh.log
aegislog collect docker --target my-container --output container.log
```

Collectors are bounded and read-only. AegisLog never automatically elevates privileges, changes services, or modifies containers.

## Ask AegisLog

```bash
aegislog ask "What are the strongest security signals?" examples/auth.log --local

aegislog config --provider ollama --model llama3.2
aegislog ask "What likely happened?" examples/auth.log
```

For a remote compatible service, set `AEGISLOG_API_KEY`, configure `openai-compatible`, and select a model. Keys are not saved in configuration. Provider context is minimized and redacted, telemetry is marked as untrusted, private-network remote endpoints are rejected, and redirects are disabled. See `docs/AI_PROVIDERS.md`.

## Reports

```bash
aegislog report auth.log --output report.json
aegislog report auth.log --output report.md
aegislog report auth.log --output report.html
```

HTML report fields escape untrusted log-derived values.

## Performance benchmark

A reproducible streaming benchmark is included:

```bash
python benchmarks/stream_benchmark.py --lines 250000 --chunk-size 2000
```

The benchmark generates synthetic telemetry locally and reports elapsed time and lines processed per second. It is intended for regression comparison rather than marketing claims.

## Main commands

`analyze`, `threats`, `anomalies`, `incidents`, `history`, `incident`, `timeline`, `hunt`, `indicators`, `baseline`, `plugins`, `stream`, `entities`, `behavior`, `watch`, `collect`, `ask`, `report`, `scan`, `config`, and `doctor`.

## Security model

AegisLog is defensive tooling. Findings, indicators, correlations, and behavioral deltas are investigative signals, not proof of compromise. Log data is hostile input: terminal control data is sanitized and AI prompts label telemetry as untrusted. The tool does not perform exploitation, automatic remediation, privilege escalation, service changes, firewall changes, or account modifications.

## Development

```bash
pip install -e '.[dev]'
pytest
ruff check .
```

## License

MIT
