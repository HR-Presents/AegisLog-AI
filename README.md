# AegisLog AI

**Terminal-first defensive log intelligence with optional AI investigation.**

AegisLog AI analyzes Linux, authentication, web, system, Docker and application telemetry using local deterministic detections, anomaly scoring, incident correlation, safe collection, and optional LLM-assisted explanation. Local analysis remains available without any AI service.

## Quick start

```bash
git clone https://github.com/HR-Presents/AegisLog-AI.git
cd AegisLog-AI
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .

aegislog doctor
aegislog analyze examples/auth.log
aegislog threats examples/auth.log
aegislog anomalies examples/auth.log
aegislog incidents examples/auth.log --persist
aegislog history
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

Local investigation requires no model:

```bash
aegislog ask "What are the strongest security signals?" examples/auth.log --local
```

For a local Ollama model:

```bash
aegislog config --provider ollama --model llama3.2
aegislog ask "What likely happened?" examples/auth.log
```

For an OpenAI-compatible endpoint:

```bash
export AEGISLOG_API_KEY='your-key'
aegislog config --provider openai-compatible --model YOUR_MODEL
aegislog ask "Explain the likely root cause" examples/auth.log
```

AegisLog does not save API keys in configuration. Before provider calls it minimizes context, redacts recognized secrets, and explicitly marks log content as untrusted telemetry rather than model instructions. Remote OpenAI-compatible endpoints are restricted from resolving to local/private network addresses; the Ollama adapter is the explicit local-model path. See `docs/AI_PROVIDERS.md`.

## Main commands

- `analyze` — local rule-backed analysis
- `threats` — high/critical security findings
- `anomalies` — lightweight rarity/frequency anomalies
- `incidents` — correlate and optionally persist related findings
- `history` — view persisted incident records
- `watch` — analyze appended log events live
- `collect` — bounded journald or Docker collection
- `ask` — local or configured AI-assisted investigation
- `report` — JSON findings/anomaly/incident report
- `scan` — scan candidate logs in a directory
- `config` — set non-secret provider preferences
- `doctor` — inspect runtime configuration

## Security model

AegisLog is defensive tooling. Findings are investigative signals, not proof of compromise. Log data is considered hostile input: terminal control data is sanitized and AI prompts label telemetry as untrusted. The tool does not perform exploitation, automatic remediation, privilege escalation, service changes, firewall changes, or account modifications.

## Development

```bash
pip install -e '.[dev]'
pytest
ruff check .
```

The repository includes CI, packaging checks, dependency auditing, synthetic fixtures, installation helpers, architecture notes, privacy documentation, a threat model and operational guidance under `docs/`.

## License

MIT
