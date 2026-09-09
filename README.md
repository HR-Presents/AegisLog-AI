<div align="center">

<img src="docs/assets/aegislog-logo.svg" alt="AegisLog — local-first defensive security log analysis" width="720" />

### Local-first security log analysis, live monitoring, and incident investigation

[![CI](https://github.com/HR-Presents/AegisLog-AI/actions/workflows/ci.yml/badge.svg)](https://github.com/HR-Presents/AegisLog-AI/actions/workflows/ci.yml)
[![Security](https://github.com/HR-Presents/AegisLog-AI/actions/workflows/security.yml/badge.svg)](https://github.com/HR-Presents/AegisLog-AI/actions/workflows/security.yml)
[![Latest release](https://img.shields.io/github/v/release/HR-Presents/AegisLog-AI?display_name=tag&style=flat-square)](https://github.com/HR-Presents/AegisLog-AI/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)

**Stable release: v1.6.3** · **Windows standalone EXE** · **Python package/source**

[Download](https://github.com/HR-Presents/AegisLog-AI/releases/latest) · [User Guide](docs/USER_GUIDE.md) · [Commands](docs/COMMANDS.md) · [Security](SECURITY.md) · [Contributing](CONTRIBUTING.md)

**Deterministic · Local-first · Read-only · Defensive**

</div>

---

## What is AegisLog?

AegisLog is an open-source, terminal-first defensive security tool for turning raw logs into structured investigation context while keeping analysis local and evidence visible.

It is designed for analysts, defenders, students, homelabs, and security teams that need practical workflows for:

- static log analysis;
- live single-source monitoring;
- multi-source correlation;
- Windows, Linux, and Docker telemetry where supported;
- incident reconstruction and evidence review;
- MITRE ATT&CK context based on observed evidence;
- analyst-oriented HTML reporting;
- local case and entity investigation.

AegisLog does not automatically remediate systems, change firewall rules, modify accounts or services, deploy persistence, steal credentials, or perform exploitation. Findings are investigation signals, not proof of compromise or attribution.

---

## Product direction

AegisLog intentionally keeps the core workflow deterministic. The current product surface does **not** include an AI Analyst, Ollama controls, or remote model-provider actions.

The interface is built around three principles:

1. **Quiet navigation** — minimal menus, restrained color, clear labels.
2. **Evidence-rich investigation** — findings, incidents, severity, confidence, and telemetry get the visual emphasis.
3. **Semantic color** — color indicates navigation state, health, warning, or severity instead of decorating every panel.

---

## Current terminal design

```text
AEGISLOG  v1.6.3
Defensive log investigation
────────────────────────────────────────────────────────
● READY   LOCAL-FIRST   READ-ONLY   DEFENSIVE

INVESTIGATE
01  Analyze            Investigate a log and generate a report
06  Incidents          Review correlated evidence chains
04  Native logs        Inspect operating-system or container telemetry

MONITOR
02  Live monitor       Watch one log source continuously
03  Multi-source       Correlate activity across live sources
05  Native monitor     Watch native telemetry read-only

TOOLS
07  Demo               Run the built-in investigation dataset
08  Health             Check engine and collector readiness
09  Help               Open the command reference

────────────────────────────────────────────────────────
Select an action  ›  01-09    C command mode    Q exit
```

Heavy nested panels are avoided. Workspaces use flat page titles, aligned metadata, whitespace, and borderless tables. Severity colors are reserved for genuine security state.

---

## Quick start

### Windows

1. Open the [latest release](https://github.com/HR-Presents/AegisLog-AI/releases/latest).
2. Download `AegisLog.exe`.
3. Optionally download `AegisLog.exe.sha256` and verify the checksum.
4. Run `AegisLog.exe start`.

The Windows executable is currently unsigned, so Windows SmartScreen or endpoint-security reputation warnings may appear even when the published checksum matches.

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

## Common workflows

### Analyze a log

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

See the full [Command Reference](docs/COMMANDS.md).

---

## Investigation model

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
Evidence-led local explanation
   ↓
Analyst review / HTML report
```

AegisLog deliberately separates **signal** from **verdict**. A high-severity finding or confidence score means “review this evidence carefully,” not “this system is definitely compromised.”

---

## Reports

Static analysis can produce a self-contained investigation report with:

- executive assessment;
- case reference and source metadata;
- event, finding, and incident counts;
- severity distribution;
- incident queue;
- retained evidence;
- recommendations;
- anomaly signals;
- telemetry distribution;
- processing and evidence limitations.

Reports remain local and read-only and can be printed or saved as PDF from the browser.

---

## Security and privacy

AegisLog treats log-derived content as untrusted input.

Core principles:

- read-only host interaction;
- deterministic local analysis;
- no automatic remediation;
- no exploitation or persistence behavior;
- no telemetry added simply to count installations;
- evidence and uncertainty remain visible;
- public issues and reviews should use sanitized or synthetic data.

Read more in [SECURITY.md](SECURITY.md), [Threat Model](docs/THREAT_MODEL.md), [Privacy](docs/PRIVACY.md), and [No Auto-Remediation](docs/NO_AUTOREMEDIATION.md).

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

Contributions are welcome when they preserve the project's defensive, local-first, evidence-led model.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest
ruff check .
bandit -q -r src
```

Keep pull requests focused, add tests for behavioral changes, and never commit credentials, customer information, or sensitive production logs.

---

## License

AegisLog is released under the [MIT License](LICENSE).

<div align="center">

**AegisLog — investigate locally, preserve evidence, keep the analyst in control.**

</div>
