# AegisLog AI

**Terminal-first defensive log intelligence and investigation.**

AegisLog AI analyzes Linux, authentication, web, system, Docker and application telemetry using deterministic detections, anomaly scoring, incident correlation, behavioral baselines, persistent investigation state, declarative rule packs, entity correlation, bounded-memory streaming, stateful live analysis, and optional LLM-assisted explanation. Core analysis works without an AI service.

## Customer bundle quick start

AegisLog AI 1.1 includes a self-contained customer distribution bundle. The bundle contains the AegisLog wheel, offline Python dependencies, Windows and Linux/macOS installers, ready-terminal launchers, dashboard launchers, uninstallers, a sample log, and SHA-256 checksums. Customers do not need access to this GitHub repository after receiving the bundle. Python 3.10 or newer is still required on the target machine.

### Windows

1. Extract `AegisLog-AI-v1.1.0-Customer-Bundle.zip`.
2. Open the `AegisLog-AI-Customer` folder.
3. Double-click `INSTALL_WINDOWS.bat`.
4. Double-click `OPEN_AEGISLOG_TERMINAL.bat`.
5. Analyze a log:

```text
aegislog dashboard C:\path\to\auth.log
```

For the shortest path, double-click `RUN_DASHBOARD.bat` after installation and paste the log path when prompted.

### Linux / macOS

```bash
chmod +x INSTALL_LINUX_MACOS.sh OPEN_AEGISLOG_TERMINAL.sh RUN_DASHBOARD.sh UNINSTALL_LINUX_MACOS.sh
./INSTALL_LINUX_MACOS.sh
./OPEN_AEGISLOG_TERMINAL.sh
```

Then run:

```bash
aegislog dashboard /path/to/auth.log
```

The installers create a private `.aegislog-venv` inside the extracted customer folder. They install the bundled wheel and dependencies locally rather than relying on a global Python Scripts directory or GitHub access.

## Developer quick start

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

For an isolated command-line installation, use `pipx install .` from a checked-out release. Upgrade with `pipx upgrade aegislog-ai` after a package release and uninstall with `pipx uninstall aegislog-ai`. AegisLog stores local configuration, rules, and investigation state under `~/.config/aegislog`; uninstalling the package does not delete analyst data.

## Terminal analysis dashboard

```bash
aegislog analyze auth.log
aegislog dashboard auth.log
```

`analyze` opens the terminal dashboard by default. The dashboard shows total lines analyzed, overall risk state, severity counts, categories, parsed log levels, top services, correlated incidents, anomaly scores, detailed findings, evidence, and investigation recommendations. Log-derived values are rendered as untrusted literal text.

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

AegisLog AI 1.1.0 is being prepared on PR #2. CI, security checks, package validation, Linux offline customer installation, Windows customer installer verification, terminal dashboard smoke tests, and customer ZIP generation are automated before merge. No merge, tag, release publication, or repository visibility change is performed by this branch.

## License

MIT
