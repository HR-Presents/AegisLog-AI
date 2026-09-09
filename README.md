<div align="center">

<img src="docs/assets/aegislog-logo.svg" alt="AegisLog — local-first defensive security log analysis" width="720" />

### Local-first security log analysis, live monitoring, and incident investigation

[![CI](https://github.com/HR-Presents/AegisLog-AI/actions/workflows/ci.yml/badge.svg)](https://github.com/HR-Presents/AegisLog-AI/actions/workflows/ci.yml)
[![Security](https://github.com/HR-Presents/AegisLog-AI/actions/workflows/security.yml/badge.svg)](https://github.com/HR-Presents/AegisLog-AI/actions/workflows/security.yml)
[![Latest release](https://img.shields.io/github/v/release/HR-Presents/AegisLog-AI?display_name=tag&style=flat-square)](https://github.com/HR-Presents/AegisLog-AI/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/HR-Presents/AegisLog-AI?style=flat-square&logo=github)](https://github.com/HR-Presents/AegisLog-AI/stargazers)

**Stable release: v1.6.0** · **Windows standalone EXE** · **Python package/source**

[Download for Windows](https://github.com/HR-Presents/AegisLog-AI/releases/tag/v1.6.0) · [Documentation](docs/README.md) · [User Guide](docs/USER_GUIDE.md) · [Commands](docs/COMMANDS.md) · [Security](SECURITY.md) · [Contributing](CONTRIBUTING.md)

**Defensive by design · Local-first · Read-only · Remote AI optional**

</div>

---

## What is AegisLog?

AegisLog is an open-source defensive security platform for turning raw logs into structured investigation context without making an external AI service part of the core workflow.

It is built for analysts, defenders, students, homelabs, and security teams that want a practical terminal-first workflow for:

- static log analysis;
- live single-source monitoring;
- multi-source correlation;
- native Windows, Linux, and Docker telemetry where supported;
- correlated incident review;
- evidence-led explanations and MITRE ATT&CK context;
- analyst-oriented HTML reports that can be printed or saved as PDF.

AegisLog does **not** automatically remediate hosts, change firewall rules, modify accounts or services, deploy persistence, steal credentials, or perform exploitation. Findings and scores are investigation signals, not proof of compromise or attribution.

---

## Why AegisLog

| Capability | AegisLog approach |
|---|---|
| **Core processing** | Local-first and deterministic |
| **Host behavior** | Read-only analysis and monitoring |
| **Primary UI** | Terminal-first Security Operations Console |
| **Windows delivery** | Standalone `AegisLog.exe` |
| **Reports** | Self-contained analyst HTML report / Save-to-PDF |
| **Remote AI** | Optional; not required for core analysis |
| **Telemetry** | File logs plus supported Windows Event Log, journald, and Docker sources |
| **Security model** | Defensive, evidence-led, non-attributive |
| **License** | MIT |

The project intentionally favors clear analyst workflows over flashy dashboards or opaque automation. The interface is designed to show what AegisLog observed, how it grouped evidence, and what an analyst should review next.

---

## Current interface

The current `main` branch includes the latest terminal UI refinements beyond the published v1.6.0 release. The public console now uses a consistent product hierarchy across Mission Control, source selection, analysis completion, health pages, command reference, and investigation output.

Key UI behaviors include:

- full-width responsive terminal layouts;
- clear `AEGISLOG // WORKSPACE` page identity;
- restrained color use with brighter colors reserved for meaningful severity states;
- primary-input emphasis during source selection;
- explicit `ANALYSIS COMPLETE` transition before investigation results;
- compact report handoff messaging;
- responsive System Health and Command Reference pages;
- narrow-terminal fallbacks that preserve readability instead of squeezing dense tables.

### Screenshots

Real product screenshots are intentionally not replaced with mockups or generated images. The repository contains a documented capture process in [`docs/SCREENSHOT_CAPTURE.md`](docs/SCREENSHOT_CAPTURE.md), and screenshots should only be published when captured from a verified Windows build using sanitized or synthetic telemetry.

---

## Quick start

### Windows — recommended for most users

1. Open the [v1.6.0 release](https://github.com/HR-Presents/AegisLog-AI/releases/tag/v1.6.0).
2. Download `AegisLog.exe`.
3. Optionally download `AegisLog.exe.sha256` and verify the checksum.
4. Run `AegisLog.exe` to open Mission Control.

The current Windows executable is unsigned, so Windows SmartScreen or endpoint-security reputation warnings may appear even when the published checksum matches.

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

## Mission Control

Run AegisLog without a subcommand:

```text
AegisLog.exe
```

The terminal control center provides direct entry points for:

```text
01  ANALYZE LOG
02  LIVE MONITOR
03  MULTI-SOURCE SOC
04  NATIVE LOGS
05  NATIVE MONITOR
06  INCIDENT INTEL
07  DEMO
08  HEALTH
09  COMMANDS
C   COMMAND MODE
Q   EXIT
```

The same workflows are available directly from the CLI.

---

## Common commands

### Static analysis

```text
AegisLog.exe dashboard C:\path\to\auth.log
AegisLog.exe incidents C:\path\to\auth.log
AegisLog.exe explain C:\path\to\auth.log <incident-id>
AegisLog.exe mitre C:\path\to\auth.log
```

### Live monitoring

```text
AegisLog.exe live C:\logs\auth.log --profile security
AegisLog.exe live-multi C:\logs\auth.log C:\logs\web.log --profile authentication
```

### Native telemetry

```text
AegisLog.exe native-sources
AegisLog.exe native-analyze windows --channel Security
AegisLog.exe native-live windows --channel Security --profile security
AegisLog.exe native-live journald --profile operations
AegisLog.exe native-live docker --container <name> --profile docker
```

### Diagnostics

```text
AegisLog.exe doctor
AegisLog.exe --help
AegisLog.exe <command> --help
```

For complete command coverage, see [`docs/COMMANDS.md`](docs/COMMANDS.md).

---

## Investigation workflow

A typical AegisLog investigation follows a simple path:

```text
Telemetry
   ↓
Parse and normalize
   ↓
Deterministic detections
   ↓
Correlation + anomaly context
   ↓
Incident queue
   ↓
Evidence-led explanation
   ↓
Analyst review / HTML report
```

The output can include severity, confidence, retained evidence, categories, anomaly signals, correlated incidents, source/service distributions, MITRE ATT&CK context, and recommended defensive follow-up.

AegisLog deliberately separates **signal** from **verdict**. A high-severity finding or confidence score means “review this evidence carefully,” not “this system is definitely compromised.”

---

## Reports

Static dashboard analysis automatically produces a self-contained investigation report. The report is designed for analyst handoff rather than marketing presentation and includes:

- executive assessment;
- case reference and source metadata;
- event/finding/incident counts;
- severity distribution;
- primary analyst decision context;
- incident queue;
- findings and recommendations;
- anomaly signals;
- observed telemetry distribution;
- processing and evidence limitations.

The report is local, read-only, and does not require remote AI. Use the browser action to print or save it as PDF.

---

## Optional AI providers

Remote AI is not required for the core product.

Where optional providers are supported, AegisLog keeps them secondary to deterministic local analysis and applies explicit data-handling boundaries. See [`docs/AI_PROVIDERS.md`](docs/AI_PROVIDERS.md), [`docs/AI_SAFETY.md`](docs/AI_SAFETY.md), and [`docs/REMOTE_AI.md`](docs/REMOTE_AI.md).

---

## Security and privacy

AegisLog is defensive tooling and treats log-derived content as untrusted input.

Core principles:

- read-only host interaction;
- no automatic remediation;
- no exploitation or persistence behavior;
- no user-tracking telemetry added simply to count installations;
- remote AI remains optional;
- evidence and uncertainty are kept visible to the analyst;
- public bug reports and reviews must use sanitized or synthetic data.

Read the full model:

- [`SECURITY.md`](SECURITY.md)
- [`docs/THREAT_MODEL.md`](docs/THREAT_MODEL.md)
- [`docs/PRIVACY.md`](docs/PRIVACY.md)
- [`docs/NO_AUTOREMEDIATION.md`](docs/NO_AUTOREMEDIATION.md)

Please report security vulnerabilities privately using the process in [`SECURITY.md`](SECURITY.md). Do not place sensitive proof-of-concept material or real production telemetry in a public issue.

---

## Documentation

| Start here | Engineering / reference |
|---|---|
| [Installation](docs/INSTALL.md) | [Architecture](docs/ARCHITECTURE.md) |
| [Quick Start](docs/QUICKSTART.md) | [Detection Pipeline](docs/DETECTION_PIPELINE.md) |
| [User Guide](docs/USER_GUIDE.md) | [Parsers](docs/PARSERS.md) |
| [Commands](docs/COMMANDS.md) | [Rules](docs/RULES.md) |
| [Demo](docs/DEMO.md) | [Collectors](docs/COLLECTORS.md) |
| [Troubleshooting](docs/TROUBLESHOOTING.md) | [Testing](docs/TESTING.md) |
| [FAQ](docs/FAQ.md) | [Performance](docs/PERFORMANCE.md) |
| [Documentation Index](docs/README.md) | [Limitations](docs/LIMITATIONS.md) |

---

## Contributing

Contributions are welcome when they preserve the project’s defensive, local-first, evidence-led model.

```bash
git clone https://github.com/HR-Presents/AegisLog-AI.git
cd AegisLog-AI
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e '.[dev]'
pytest
ruff check .
bandit -q -r src
```

Before opening a pull request, read [`CONTRIBUTING.md`](CONTRIBUTING.md). Keep PRs focused, add tests for behavioral changes, and never commit credentials, customer information, or real sensitive logs.

---

## Support and community

- **Bug or reproducible UX issue:** use the GitHub issue templates with sanitized reproduction data.
- **Feature idea:** request defensive, local-first improvements.
- **Security vulnerability:** follow [`SECURITY.md`](SECURITY.md) privately.
- **Usage help:** start with [`SUPPORT.md`](SUPPORT.md) and the [User Guide](docs/USER_GUIDE.md).
- **Public experience:** use the [User Review](https://github.com/HR-Presents/AegisLog-AI/issues/new?template=user_review.yml) form.

Stars, forks, issues, pull requests, and public reviews are GitHub-native community signals. A star is support or interest; it is not proof that someone installed the application.

---

## Release status

**Published stable:** v1.6.0

The `main` branch may contain reviewed improvements that are newer than the latest stable binary. v1.6.1 work remains unreleased until its release process is explicitly completed. Do not treat CI artifacts as permanent customer downloads; official user downloads are GitHub Release assets.

See [`CHANGELOG.md`](CHANGELOG.md), [`docs/RELEASE_V1.6.0.md`](docs/RELEASE_V1.6.0.md), and the [GitHub Releases](https://github.com/HR-Presents/AegisLog-AI/releases) page.

---

## License

AegisLog is released under the [MIT License](LICENSE).

<div align="center">

**AegisLog — investigate locally, preserve evidence, keep the analyst in control.**

</div>
