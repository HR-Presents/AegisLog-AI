# AegisLog documentation

Welcome to the AegisLog documentation hub. Start with the user guide if you want the complete workflow, or jump directly to the area you need.

> **Project posture:** AegisLog is defensive, local-first, read-only by default, and does not require remote AI for its core investigation workflow.

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
- [AI safety](AI_SAFETY.md)
- [AI providers](AI_PROVIDERS.md)
- [Remote AI boundaries](REMOTE_AI.md)

Remote AI is optional. Supplying provider credentials does not change the project’s core local-first model, and the normal deterministic analysis path remains available without a remote AI service.

## Product and operator experience

- [User Guide](USER_GUIDE.md) — Mission Control and direct CLI workflows
- [Commands](COMMANDS.md) — supported CLI entry points
- [Screenshot capture](SCREENSHOT_CAPTURE.md) — requirements for verified public product screenshots
- [Community reviews](COMMUNITY_REVIEWS.md) — transparent public feedback policy
- [Support](../SUPPORT.md) — choosing the right help or reporting path

Public screenshots should come from a verified build and sanitized or synthetic telemetry. The project intentionally avoids publishing mock product screenshots as if they were real captures.

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

## Release status

- **Published stable:** [v1.6.0 release notes](RELEASE_V1.6.0.md)
- **Current unreleased work:** [v1.6.1 release notes](RELEASE_V1.6.1.md)
- [Upgrading](UPGRADING.md)
- [Latest GitHub release](https://github.com/HR-Presents/AegisLog-AI/releases/latest)

The `main` branch can contain reviewed improvements newer than the current stable release. A v1.6.1 build should not be described as published until the release process is explicitly completed. CI artifacts are validation outputs; official customer downloads belong on GitHub Releases.

## Contributing

Want to improve AegisLog? Read [CONTRIBUTING.md](../CONTRIBUTING.md) before opening a pull request. Keep changes focused, defensive, testable, and free of real credentials or sensitive production telemetry.
