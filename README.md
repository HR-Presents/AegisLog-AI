# AegisLog AI

**Terminal-first defensive log intelligence and investigation.**

AegisLog AI analyzes Linux, authentication, web, system, Docker and application telemetry using deterministic detections, anomaly scoring, incident correlation, historical baselines, persistent investigation state, local rule plugins, defensive indicator extraction, and optional LLM-assisted explanation. Core analysis works without an AI service.

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

Persisted incidents use a local SQLite database under the AegisLog configuration directory. `hunt` filters by text, severity, category and source.

## Extensible detection rules

AegisLog loads optional local Python rule packs from its `rules.d` configuration directory. Run `aegislog plugins` to inspect loaded packs and errors. A plugin defines a `RULES` list containing dictionaries with `id`, `severity`, `category`, `title`, `pattern`, and `recommendation`. Broken plugins are isolated instead of preventing the core analyzer from running. Only install rule plugins you trust because Python rule files execute locally as code.

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

## Main commands

`analyze`, `threats`, `anomalies`, `incidents`, `history`, `incident`, `timeline`, `hunt`, `indicators`, `baseline`, `plugins`, `watch`, `collect`, `ask`, `report`, `scan`, `config`, and `doctor`.

## Security model

AegisLog is defensive tooling. Findings and extracted indicators are investigative signals, not proof of compromise. Log data is hostile input: terminal control data is sanitized and AI prompts label telemetry as untrusted. The tool does not perform exploitation, automatic remediation, privilege escalation, service changes, firewall changes, or account modifications.

## Development

```bash
pip install -e '.[dev]'
pytest
ruff check .
```

## License

MIT
