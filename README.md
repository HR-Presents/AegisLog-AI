<div align="center">

# AegisLog AI

### Terminal-first defensive security for local log analysis, live monitoring, and incident investigation

[![CI](https://github.com/HR-Presents/AegisLog-AI/actions/workflows/ci.yml/badge.svg)](https://github.com/HR-Presents/AegisLog-AI/actions/workflows/ci.yml)
[![Security](https://github.com/HR-Presents/AegisLog-AI/actions/workflows/security.yml/badge.svg)](https://github.com/HR-Presents/AegisLog-AI/actions/workflows/security.yml)
[![Latest release](https://img.shields.io/github/v/release/HR-Presents/AegisLog-AI?display_name=tag&style=flat-square)](https://github.com/HR-Presents/AegisLog-AI/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)

**Stable release: v1.6.0**

[Download AegisLog.exe](https://github.com/HR-Presents/AegisLog-AI/releases/tag/v1.6.0) · [Documentation](docs/README.md) · [User Guide](docs/USER_GUIDE.md) · [Release Notes](docs/RELEASE_V1.6.0.md)

</div>

---

## What AegisLog AI is

AegisLog AI is an **open-source, local-first defensive security platform** built for analysts who want practical terminal workflows without sending their core telemetry to an external service.

It turns authentication, Linux, Windows Event Log, web, Docker, system, and application telemetry into structured findings, correlated incidents, investigation timelines, analyst triage, entity context, anomaly signals, MITRE ATT&CK context, and evidence-led explanations.

The core workflow is deterministic and read-only. AegisLog does not automatically remediate hosts, change firewall rules, modify accounts or services, deploy persistence, evade controls, or perform exploitation.

> **Windows users:** the recommended distribution is a standalone `AegisLog.exe`. Normal use does not require Python, a virtual environment, a requirements file, an installer, or a support folder.

---

## Why use it

- **Local-first analysis** — core detection, correlation, investigation, triage, and explanation run locally.
- **Read-only operation** — AegisLog observes and analyzes telemetry without changing the monitored system.
- **Terminal-first UX** — interactive control center, dashboards, focused commands, live monitoring, and investigation workflows.
- **Evidence-led results** — findings, confidence values, anomaly scores, incident priorities, and ATT&CK mappings are investigation signals, not proof of compromise or attribution.
- **Native telemetry support** — Windows Event Log, journald, Docker, and file-based sources where supported.
- **Bounded runtime behavior** — rolling windows and bounded long-running state are used to avoid unbounded growth during sustained monitoring.
- **Optional AI only** — compatible external providers are opt-in and secondary; the complete core workflow works without them.
- **Open source** — MIT licensed and designed for inspection, extension, and defensive use.

---

## v1.6.0 highlights

AegisLog AI v1.6.0 focuses on analyst workflow quality and operational reliability rather than broadening into offensive capability.

- **Analyst triage summary** during investigations, using existing severity and confidence evidence to help prioritize review.
- **Improved native diagnostics** for Windows Event Log, journald, and Docker, including clearer unsupported-versus-unavailable states.
- **Safer live-source resilience** when watched files temporarily disappear or recover, while keeping the current dashboard visible.
- **Bounded multi-source runtime state** for arrival history and alert fingerprints during long-running monitoring.
- **Focused regression coverage** for triage, native diagnostics, source loss/recovery, high-volume ingestion, and runtime ceilings.
- **Guarded release engineering** with quality/security gates, one-file Windows builds, smoke tests, checksums, and immutable-style release checks.

AegisLog remains **defensive, local-first, read-only, and non-attributive**. A severity score, confidence value, anomaly, triage priority, or ATT&CK mapping is not treated as proof of compromise or attacker identity.

---

## Quick start

### Windows — recommended

1. Open the [v1.6.0 release](https://github.com/HR-Presents/AegisLog-AI/releases/tag/v1.6.0).
2. Download `AegisLog.exe`.
3. Download `AegisLog.exe.sha256` if you want to verify the binary.
4. Run `AegisLog.exe` to open the terminal control center.

The executable is currently unsigned, so Windows SmartScreen or endpoint-security reputation warnings can appear even when the published checksum matches.

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

---

## Terminal control center

Running AegisLog with no command opens the interactive terminal control center.

```text
AegisLog.exe
```

From there you can move into file analysis, live dashboards, multi-source monitoring, native telemetry, incident investigation, case history, explanations, and diagnostics.

Useful Windows commands:

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
AegisLog.exe intel-entities C:\path\to\auth.log
AegisLog.exe mitre C:\path\to\auth.log
AegisLog.exe case-history
```

For exact syntax supported by your build:

```text
AegisLog.exe --help
AegisLog.exe <command> --help
```

---

## Core workflows

### File analysis and dashboard

```text
AegisLog.exe analyze auth.log
AegisLog.exe dashboard auth.log
```

The terminal dashboard can show total lines analyzed, risk state, severity counts, categories, parsed levels, top services, incidents, anomaly context, detailed findings, evidence, and recommended investigation steps.

Log-derived text is treated as untrusted and rendered safely in the terminal.

### Live monitoring

Single-file monitoring follows a growing source using a bounded rolling analysis window:

```text
AegisLog.exe live server.log
```

Multi-source monitoring correlates several growing files in one terminal SOC-style view:

```text
AegisLog.exe live-multi auth.log nginx.log application.log
```

If a watched file becomes temporarily unavailable, v1.6.0 reports the source state, keeps the current dashboard visible, retries using read-only polling, and recognizes recovery when the source returns.

Live monitoring supports focused profiles:

- `all`
- `security`
- `authentication`
- `web`
- `docker`
- `operations`

Examples:

```text
AegisLog.exe live auth.log --profile authentication
AegisLog.exe live-multi auth.log nginx.log --profile web
AegisLog.exe native-live docker --container api --profile docker
```

### Native telemetry

AegisLog can collect supported native sources without requiring a prior manual export:

```text
AegisLog.exe native-sources
AegisLog.exe native-analyze windows --channel Security
AegisLog.exe native-analyze journald
AegisLog.exe native-analyze docker --container <name>
AegisLog.exe native-live windows --channel Security
AegisLog.exe native-live journald
AegisLog.exe native-live docker --container <name>
```

Native collection is bounded and read-only. Support depends on the operating system and installed tooling. v1.6.0 provides clearer operator diagnostics for unsupported and temporarily unavailable sources without changing host security policy.

### Incident investigation

```text
AegisLog.exe incidents auth.log
AegisLog.exe investigate auth.log <incident-id>
AegisLog.exe explain auth.log <incident-id>
AegisLog.exe intel-entities auth.log
AegisLog.exe mitre auth.log
AegisLog.exe save-investigation auth.log <incident-id>
AegisLog.exe case-history
AegisLog.exe case-show <incident-id>
```

Investigations can include severity, confidence, triage priority, timeline events, evidence, entity context, ATT&CK context, and safe next actions.

The v1.6 triage summary is intentionally conservative. It helps analysts decide what deserves attention first, but explicitly does **not** claim compromise, attacker intent, or attribution.

`explain` produces a deterministic local analyst explanation with evidence, context, safe next investigation steps, and uncertainty language. It does not require sending log content to an external AI service.

---

## Reports, baselines, and scale

AegisLog also supports structured reporting, streaming analysis, baselines, behavior comparison, hunting, entity indexing, and indicator extraction.

```bash
aegislog report auth.log --output report.json
aegislog stream huge-server.log --chunk-size 2000
aegislog baseline normal.log current.log
aegislog behavior --baseline monday.log --baseline tuesday.log --current today.log
aegislog hunt --severity HIGH
```

Long-running state is designed around bounded structures. v1.6.0 adds hard ceilings for multi-source arrival history and alert fingerprint tracking so sustained workloads do not create unbounded state growth.

---

## Declarative detection rules

AegisLog loads declarative JSON rule packs from its `rules.d` configuration directory. Python files placed there are not imported or executed as rules.

```json
{
  "rules": [
    {
      "id": "custom-01",
      "severity": "HIGH",
      "category": "application",
      "title": "Sensitive service failure",
      "pattern": "payment-worker.*fatal",
      "recommendation": "Review the affected worker and surrounding telemetry."
    }
  ]
}
```

---

## Optional AI providers

AegisLog does **not** require an AI account for its core workflow.

Optional compatible providers can be configured for assisted analysis where supported. Remote-provider context is minimized and redacted, telemetry is treated as untrusted, private-network remote endpoints are rejected, and redirects are disabled.

See [`docs/AI_PROVIDERS.md`](docs/AI_PROVIDERS.md) for the provider model and data-handling boundaries.

---

## Security model

AegisLog is defensive tooling.

Findings, anomaly scores, confidence values, correlations, triage priorities, ATT&CK mappings, and behavioral deltas are **investigative signals**. They are not proof of compromise, attacker attribution, or malicious intent by themselves.

AegisLog does not perform exploitation, automatic remediation, credential theft, persistence, privilege escalation, evasion, firewall changes, service changes, or account modifications.

For the full security and privacy model, read:

- [`docs/THREAT_MODEL.md`](docs/THREAT_MODEL.md)
- [`docs/PRIVACY.md`](docs/PRIVACY.md)
- [`docs/NO_AUTOREMEDIATION.md`](docs/NO_AUTOREMEDIATION.md)
- [`SECURITY.md`](SECURITY.md)

To report a vulnerability, use the private reporting path described in `SECURITY.md`; do not place sensitive details in a public issue.

---

## Developer setup

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

AegisLog requires Python 3.10+ when run from source or installed as a Python package. The standalone Windows executable bundles its runtime for normal customer use.

---

## Release engineering

The stable v1.6.0 release is published through an explicit manual GitHub Actions workflow.

Publication requires the exact confirmation value `RELEASE-v1.6.0`, must run from `main`, verifies package/runtime version metadata, runs quality and security gates, builds and smoke-tests the one-file Windows executable, generates and verifies its SHA-256 checksum, and refuses to reuse an existing v1.6.0 tag or GitHub release.

Published customer assets:

```text
AegisLog.exe
AegisLog.exe.sha256
```

Current executable SHA-256:

```text
4eb81c9f66c865867e81987f2467bc9576019c805085e26f5da009566e86a02f
```

See [`docs/RELEASE_V1.6.0.md`](docs/RELEASE_V1.6.0.md) for release-specific details.

---

## Documentation

- [`docs/README.md`](docs/README.md) — documentation index
- [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) — complete usage guide
- [`docs/INSTALL.md`](docs/INSTALL.md) — installation and checksum verification
- [`docs/COMMANDS.md`](docs/COMMANDS.md) — command reference
- [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) — troubleshooting
- [`docs/PERFORMANCE.md`](docs/PERFORMANCE.md) — performance and bounded-state notes
- [`docs/PROJECT_STATUS.md`](docs/PROJECT_STATUS.md) — current project status
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — maintenance and future-direction notes
- [`docs/RELEASE_V1.6.0.md`](docs/RELEASE_V1.6.0.md) — stable release notes

---

## Contributing and support

- Read [`CONTRIBUTING.md`](CONTRIBUTING.md) before opening a pull request.
- Use the bug-report issue template with sanitized logs and reproducible steps.
- Feature requests should stay within the defensive, local-first scope.
- Check the FAQ and troubleshooting guide before opening a support issue.

---

## License

MIT

<div align="center">

**AegisLog AI v1.6.0 — local-first defensive analysis, built for evidence-led investigation.**

</div>
