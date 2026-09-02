# AegisLog AI

**Open-source, terminal-first defensive security for local log analysis, live monitoring, and incident investigation.**

[![CI](https://github.com/HR-Presents/AegisLog-AI/actions/workflows/ci.yml/badge.svg)](https://github.com/HR-Presents/AegisLog-AI/actions/workflows/ci.yml)
[![Latest release](https://img.shields.io/github/v/release/HR-Presents/AegisLog-AI?display_name=tag)](https://github.com/HR-Presents/AegisLog-AI/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

AegisLog AI helps defenders turn authentication, Linux, Windows Event Log, web, Docker, system, and application telemetry into evidence-led findings and investigations. Its core analysis is deterministic, runs locally, and does not require an AI account or external service. Collection and analysis are read-only: AegisLog does not remediate, reconfigure, or modify the systems it observes.

> **Get started on Windows:** [Download the latest `AegisLog.exe`](https://github.com/HR-Presents/AegisLog-AI/releases/latest) — one console executable with no Python installation required. A matching SHA-256 checksum is included with the release.

## Why AegisLog

- **Local-first by default:** core detection, correlation, investigation, and explanation stay on your machine.
- **Read-only defensive operation:** analyzes files and supported native telemetry without changing accounts, firewalls, services, or host configuration.
- **Terminal-first workflow:** use an interactive control center or focused commands for repeatable investigations.
- **Evidence before certainty:** findings, anomaly scores, and ATT&CK context are investigation leads—not claims of compromise or attribution.
- **Optional AI integration:** compatible remote providers are opt-in; the complete core workflow works without them.
- **MIT licensed:** inspect, adapt, and contribute under the [MIT License](LICENSE).

## Quick start

### Windows (recommended)

1. Open the [latest release](https://github.com/HR-Presents/AegisLog-AI/releases/latest).
2. Download `AegisLog.exe` and, optionally, `AegisLog.exe.sha256` for verification.
3. Run `AegisLog.exe` to open the terminal control center.

### Python 3.10+

```bash
git clone https://github.com/HR-Presents/AegisLog-AI.git
cd AegisLog-AI
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
aegislog doctor
aegislog dashboard examples/auth.log
```

## Documentation

- **Documentation index:** [`docs/README.md`](docs/README.md) — installation, usage, security model, architecture, and project references.
- **Complete usage guide:** [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) — Windows setup, commands, live monitoring, native collection, incidents, investigation, ATT&CK context, cases, checksum verification, and troubleshooting.
- **v1.4.6 release notes:** [`docs/RELEASE_V1.4.6.md`](docs/RELEASE_V1.4.6.md)
- **AI provider documentation:** [`docs/AI_PROVIDERS.md`](docs/AI_PROVIDERS.md)

For exact syntax supported by the executable you downloaded, use:

```text
AegisLog.exe --help
AegisLog.exe <command> --help
```

## Windows release details

The primary Windows delivery is one file:

```text
AegisLog.exe
```

1. Download `AegisLog.exe` from the latest release.
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

## Demo and screenshots

Run the included safe demo against sample data:

```bash
aegislog dashboard examples/auth.log
aegislog incidents examples/auth.log
```

See the [demo walkthrough](docs/DEMO.md) and [screenshot capture guide](docs/SCREENSHOT_SCRIPT.md). Public screenshots are intentionally not embedded until they can be captured from the current stable release with reviewed, synthetic data; no fabricated product UI is used here.

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

For data-handling boundaries and assumptions, read the [threat model](docs/THREAT_MODEL.md), [privacy guide](docs/PRIVACY.md), and [security policy](SECURITY.md). To report a vulnerability, follow the private reporting path in [SECURITY.md](SECURITY.md); do not disclose sensitive details in a public issue.

## Contributing and support

- Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.
- [Report a bug](https://github.com/HR-Presents/AegisLog-AI/issues/new?template=bug_report.md) using sanitized logs and reproducible steps.
- [Request a feature](https://github.com/HR-Presents/AegisLog-AI/issues/new?template=feature_request.md) that fits the defensive, local-first scope.
- For usage questions, check the [FAQ](docs/FAQ.md) and [troubleshooting guide](docs/TROUBLESHOOTING.md) before opening an issue.

## Release engineering

v1.4.6 is published through an explicit manual release workflow. Publication requires an exact confirmation value, must run from `main`, validates package/runtime version metadata, runs quality and security gates, builds and smoke-tests the one-file Windows executable, verifies its SHA-256 checksum, and refuses to reuse or mutate an existing `v1.4.6` tag or GitHub release.

Release notes and customer instructions are in `docs/RELEASE_V1.4.6.md`.

## License

MIT