# AegisLog AI

**Terminal-first defensive log intelligence, live monitoring, and investigation.**

AegisLog AI analyzes authentication, Linux, Windows Event Log, web, Docker, system, and application telemetry using deterministic detections, anomaly scoring, incident correlation, entity intelligence, behavioral baselines, MITRE ATT&CK context, persistent cases, real-time rate/trend analysis, and optional LLM-assisted explanation. Core analysis works locally without an AI service.

## Documentation

- **Complete usage guide:** [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) — Windows setup, command reference, Watch Mode Profiles, live monitoring, native Windows/journald/Docker collection, incidents, investigation, Explain This Incident, MITRE ATT&CK context, case history, checksum verification, recommended workflows, and troubleshooting.
- **v1.3.0 release notes:** [`docs/RELEASE_V1.3.0.md`](docs/RELEASE_V1.3.0.md)
- **AI provider documentation:** [`docs/AI_PROVIDERS.md`](docs/AI_PROVIDERS.md)

For exact syntax supported by the executable you downloaded, use:

```text
AegisLog.exe --help
AegisLog.exe <command> --help
```

## Windows customer quick start

The primary Windows delivery is one file:

```text
AegisLog.exe
```

1. Download `AegisLog.exe` from the v1.3.0 release.
2. Optionally verify it against `AegisLog.exe.sha256`.
3. Double-click `AegisLog.exe`.
4. Choose what you want to analyze from the terminal control center.

No Python installation, virtual environment, requirements file, installer, or support folder is required for the one-file Windows executable.

The binary is a console application. Unless a release explicitly says otherwise, do not assume it is digitally signed; Windows SmartScreen or antivirus reputation warnings can occur with unsigned PyInstaller one-file applications.

## Terminal control center

Running `AegisLog.exe` with no arguments opens the interactive control center. It provides access to file analysis, live dashboards, multi-source monitoring, native telemetry, incident explanation, system checks, and command help.

Useful Windows commands include:

```text
AegisLog.exe dashboard C:\path\to\auth.log
AegisLog.exe live C:\path\to\auth.log --profile security
AegisLog.exe live-multi C:\logs\auth.log C:\logs\web.log --profile authentication
AegisLog.exe native-sources
AegisLog.exe native-analyze windows --channel Security
AegisLog.exe native-live windows --channel Security --profile security
AegisLog.exe incidents C:\path\to\auth.log
AegisLog.exe investigate C:\path\to\auth.log <incident-id>
AegisLog.exe explain C:\path\to\auth.log <incident-id>
AegisLog.exe mitre C:\path\to\auth.log
AegisLog.exe case-history
```

See the [complete user guide](docs/USER_GUIDE.md) for explanations and practical workflows for these commands.

## Watch Mode Profiles

Live monitoring can be focused without changing the underlying read-only ingestion. Available profiles are:

- `all` — full defensive live view
- `security` — broad security-relevant activity
- `authentication` — login failures, account activity, and auth-related rate signals
- `web` — web probes, suspicious requests, and application-facing activity
- `docker` — container/service-oriented telemetry
- `operations` — errors, failures, availability, and operational health signals

Examples:

```text
AegisLog.exe live auth.log --profile authentication
AegisLog.exe live-multi auth.log nginx.log --profile web
AegisLog.exe native-live docker --container api --profile docker
```

## Real-time defensive monitoring

Single-file live monitoring follows a growing log and maintains a bounded rolling analysis window. The dashboard shows event rate, findings, incidents, anomaly context, risk, recent high-signal detections, and adaptive rate/baseline intelligence.

```text
AegisLog.exe live server.log
```

Multi-source monitoring correlates several growing files in one terminal SOC view:

```text
AegisLog.exe live-multi auth.log nginx.log application.log
```

The rate/trend engine tracks failed logins, errors, and firewall blocks per minute, maintains an adaptive local baseline, and marks meaningful short-window deviations as elevated activity or spikes.

## Native telemetry

AegisLog can collect supported native sources without first exporting them to a file:

```text
AegisLog.exe native-sources
AegisLog.exe native-analyze windows --channel Security
AegisLog.exe native-analyze journald
AegisLog.exe native-analyze docker --container <name>
AegisLog.exe native-live windows --channel Security
AegisLog.exe native-live journald
AegisLog.exe native-live docker --container <name>
```

Native collection is bounded and read-only. Supported sources depend on the operating system and installed tooling.

## Incident investigation

AegisLog can build evidence-led incidents with confidence, timelines, entities, persistent case history, and MITRE ATT&CK context.

```text
AegisLog.exe incidents auth.log
AegisLog.exe investigate auth.log <incident-id>
AegisLog.exe intel-entities auth.log
AegisLog.exe save-investigation auth.log <incident-id>
AegisLog.exe case-history
AegisLog.exe case-show <incident-id>
AegisLog.exe mitre auth.log
AegisLog.exe explain auth.log <incident-id>
```

`explain` produces a deterministic local analyst explanation with a summary, why the activity matters, evidence, evidence-consistent ATT&CK context, safe next investigation steps, and an explicit uncertainty caveat. It does not require sending log content to an external AI service.

## Terminal analysis dashboard

```text
AegisLog.exe analyze auth.log
AegisLog.exe dashboard auth.log
```

The dashboard shows total lines analyzed, overall risk state, severity counts, categories, parsed levels, top services, correlated incidents, anomaly scores, detailed findings, evidence, and investigation recommendations. Log-derived values are rendered as untrusted literal text.

## Developer quick start

```bash
git clone https://github.com/HR-Presents/AegisLog-AI.git
cd AegisLog-AI
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e '.[dev]'

aegislog doctor
aegislog dashboard examples/auth.log
pytest
ruff check .
bandit -q -r src
```

AegisLog requires Python 3.10+ when run from source or installed as a Python package. The standalone Windows release executable bundles its own runtime.

## Declarative detection rules

AegisLog loads declarative JSON rule packs from its `rules.d` configuration directory. Python files in the rule directory are not imported or executed.

```json
{"rules":[{"id":"custom-01","severity":"HIGH","category":"application","title":"Sensitive service failure","pattern":"payment-worker.*fatal","recommendation":"Review the affected worker and surrounding telemetry."}]}
```

## Optional AI providers

Core analysis is deterministic and local. Optional compatible AI providers can be configured for assisted analysis where supported. Remote provider context is minimized and redacted, telemetry is treated as untrusted, private-network remote endpoints are rejected, and redirects are disabled. See `docs/AI_PROVIDERS.md`.

## Reports and scale

AegisLog also supports report generation, bounded-memory streaming, historical baselines, behavior comparison, hunting, entity indexing, and indicator extraction.

```bash
aegislog report auth.log --output report.json
aegislog stream huge-server.log --chunk-size 2000
aegislog baseline normal.log current.log
aegislog behavior --baseline monday.log --baseline tuesday.log --current today.log
aegislog hunt --severity HIGH
```

## Security model

AegisLog is defensive tooling. Findings, anomaly scores, confidence values, correlations, ATT&CK mappings, and behavioral deltas are investigative signals, not proof of compromise or attacker attribution. Log-derived terminal text is treated as untrusted and sanitized. The tool does not perform exploitation, automatic remediation, privilege escalation, service changes, firewall changes, or account modifications.

## Release engineering

v1.3.0 is published through an explicit manual release workflow. Publication requires an exact confirmation value, must run from `main`, validates package/runtime version metadata, runs quality and security gates, builds and smoke-tests the one-file Windows executable, verifies its SHA-256 checksum, and refuses to reuse or mutate an existing `v1.3.0` tag or GitHub release.

Release notes and customer instructions are in `docs/RELEASE_V1.3.0.md`.

## License

MIT
