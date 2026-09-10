# AegisLog documentation

Welcome to the AegisLog documentation hub. Start with the user guide for the complete workflow, or jump directly to the area you need.

> **Project posture:** AegisLog is defensive, terminal-first, local-first, read-only by default, and deterministic for detection and correlation. AI Analyst and remote-provider workflows are not part of the supported public product surface.

## Start here

| Goal | Guide |
|---|---|
| Install AegisLog | [Installation](INSTALL.md) |
| Run your first analysis | [Quick Start](QUICKSTART.md) |
| Learn the complete workflow | [User Guide](USER_GUIDE.md) |
| Find a command | [Command Reference](COMMANDS.md) |
| Try safe synthetic data | [Demo](DEMO.md) |
| Fix a problem | [Troubleshooting](TROUBLESHOOTING.md) / [FAQ](FAQ.md) |

## Detection and investigation

- [Detection pipeline](DETECTION_PIPELINE.md) — how telemetry moves through the analysis path
- [Parsers](PARSERS.md) — normalization and supported input structures
- [Rules](RULES.md) — declarative detection behavior
- [Collectors](COLLECTORS.md) — supported native telemetry sources
- [Incidents](INCIDENTS.md) — correlation and incident handling
- [Anomalies](ANOMALIES.md) — anomaly-scoring context and limitations
- [Watch Mode](WATCH.md) — live monitoring behavior
- [Report schema](REPORT_SCHEMA.md) — structured report output

## Security and data handling

- [Threat model](THREAT_MODEL.md)
- [Security notes](SECURITY_NOTES.md)
- [Privacy](PRIVACY.md)
- [Why local-first](WHY_LOCAL_FIRST.md)
- [No automatic remediation](NO_AUTOREMEDIATION.md)

Older AI/provider documents may remain in repository history for traceability, but they do not define the supported v2 product surface.

## Product and operator experience

- [User Guide](USER_GUIDE.md) — Mission Control and direct CLI workflows
- [Commands](COMMANDS.md) — supported CLI entry points
- [Screenshot capture](SCREENSHOT_CAPTURE.md) — requirements for verified public product screenshots
- [Community reviews](COMMUNITY_REVIEWS.md) — transparent public feedback policy
- [Support](../SUPPORT.md) — choosing the right help or reporting path

Public screenshots should come from a verified build and sanitized or synthetic telemetry. Automated rendering checks do not, by themselves, establish visual acceptance on Windows.

## Engineering

- [Architecture](ARCHITECTURE.md)
- [Design principles](DESIGN_PRINCIPLES.md)
- [Configuration](CONFIGURATION.md)
- [Testing](TESTING.md)
- [Performance](PERFORMANCE.md)
- [Limitations](LIMITATIONS.md)
- [Project status](PROJECT_STATUS.md)
- [Roadmap](ROADMAP.md)
- [Versioning](VERSIONING.md)
- [Maintainer guide](MAINTAINERS.md)
- [Release checklist](RELEASE_CHECKLIST.md)
- [External evaluation runbook](EXTERNAL_EVALUATION.md)

## Release status

- **Published stable:** [v2.1.3 release notes](RELEASE_V2.1.3.md)
- **Release target commit:** `c01247b34a2dd54c863dd142c618f03e184af8f8`
- **Windows EXE SHA-256:** `1ddda99e03fd36ba1816b1567a28b8cc23d410583f34771c1287f9e3c1a28155`
- **Release history:** see the repository [CHANGELOG](../CHANGELOG.md) and [GitHub Releases](https://github.com/HR-Presents/AegisLog-AI/releases)
- [Upgrading](UPGRADING.md)
- [Latest GitHub release](https://github.com/HR-Presents/AegisLog-AI/releases/latest)

The published v2.1.3 Windows UI did not pass later real-Windows visual acceptance, so no newer UI state should be described as accepted merely because a development build or CI render exists. Official customer downloads remain GitHub Release assets; CI artifacts are validation outputs rather than the permanent distribution channel.

## Contributing

Want to improve AegisLog? Read [CONTRIBUTING.md](../CONTRIBUTING.md) before opening a pull request. Keep changes focused, defensive, testable, and free of real credentials or sensitive production telemetry.
