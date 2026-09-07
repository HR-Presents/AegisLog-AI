# Documentation index

Use this page as the map for AegisLog AI documentation. For a guided, end-to-end reference, start with the [user guide](USER_GUIDE.md).

## Start here

- [Installation](INSTALL.md) — standalone Windows release, checksum verification, and Python setup
- [Quick start](QUICKSTART.md) — first local analysis
- [User guide](USER_GUIDE.md) — complete Windows and command-line workflow
- [Commands](COMMANDS.md) — command reference
- [Demo](DEMO.md) — synthetic-data walkthrough
- [Troubleshooting](TROUBLESHOOTING.md) and [FAQ](FAQ.md) — common questions and recovery steps

## Detection and investigation

- [Collectors](COLLECTORS.md), [parsers](PARSERS.md), and [rules](RULES.md)
- [Anomalies](ANOMALIES.md), [incidents](INCIDENTS.md), and [Watch Mode](WATCH.md)
- [Detection pipeline](DETECTION_PIPELINE.md) and [report schema](REPORT_SCHEMA.md)

## Security and data handling

- [Threat model](THREAT_MODEL.md) and [security notes](SECURITY_NOTES.md)
- [Privacy](PRIVACY.md), [why local-first](WHY_LOCAL_FIRST.md), and [no automatic remediation](NO_AUTOREMEDIATION.md)
- [AI safety](AI_SAFETY.md), [AI providers](AI_PROVIDERS.md), and [remote AI boundaries](REMOTE_AI.md)

Remote AI is disabled by default in the hardened candidate. Supplying an API key alone does not grant network consent; a remote provider requires explicit `AEGISLOG_ALLOW_REMOTE_AI` opt-in. Local core analysis and local Ollama workflows remain available without remote-AI consent.

## Project and engineering

- [Architecture](ARCHITECTURE.md), [design principles](DESIGN_PRINCIPLES.md), and [configuration](CONFIGURATION.md)
- [Testing](TESTING.md), [performance](PERFORMANCE.md), and [limitations](LIMITATIONS.md)
- [Project status](PROJECT_STATUS.md), [roadmap](ROADMAP.md), and [versioning](VERSIONING.md)
- [Maintainer guide](MAINTAINERS.md) and [release checklist](RELEASE_CHECKLIST.md)

## Release status

- **Published stable release:** [v1.6.0 release notes](RELEASE_V1.6.0.md). The published Windows executable is historically documented as unsigned.
- **Hardened candidate:** [v1.6.1 release notes](RELEASE_V1.6.1.md). This candidate is not yet published and remains blocked on real signing setup, independently labeled external evaluation evidence, and an authorized release run.
- [Upgrading](UPGRADING.md)
- [Latest GitHub release](https://github.com/HR-Presents/AegisLog-AI/releases/latest)
