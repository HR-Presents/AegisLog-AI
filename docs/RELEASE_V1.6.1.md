# AegisLog AI v1.6.1

AegisLog AI v1.6.1 is a production-hardening release focused on reliable defensive log analysis, safer investigation workflows, privacy, deterministic validation, and a polished terminal-first experience.

AegisLog remains **local-first, read-only, and defensive by design**.

> **Release status:** v1.6.1 was published on September 9, 2026 from commit `f5a2eaf23893cf3cb40f93c55f642e8caab446f0`.

## Highlights

- Improved authentication-event analysis and correlation.
- More reliable streaming analysis with bounded long-running state.
- Improved Windows Event Log, journald, Docker, and multi-source diagnostics.
- Conservative analyst triage based on severity, confidence, timeline, and entity evidence.
- Responsive terminal experience with improved Mission Control, source input, investigation dashboards, system pages, and report handoff.
- Deterministic local analysis remains the primary detection workflow.
- Optional AI Analyst assistance for investigation context and explanation.
- Remote AI remains explicitly opt-in; core analysis does not require an external AI provider.
- Stronger automated release validation, dependency lock auditing, security checks, packaging checks, and Windows executable smoke testing.

## Windows download

The v1.6.1 GitHub Release contains exactly:

```text
AegisLog.exe
AegisLog.exe.sha256
```

`AegisLog.exe` is a standalone one-file Windows application. Normal use does not require a separate Python installation or virtual environment.

Published executable SHA-256:

```text
ceca4893de78271514d3ea07c7b2d6709b95d53ff2834c24e49e0e1ebda16546
```

Verify the executable against the accompanying `AegisLog.exe.sha256` file before running it.

## Release verification

The v1.6.1 release pipeline successfully completed:

- release preflight validation;
- version and release-state validation;
- automated tests and linting;
- security checks and dependency auditing;
- runtime, build, and validation toolchain lock audits;
- synthetic detection regression evaluation;
- package build validation;
- Windows one-file executable build;
- Windows release smoke tests;
- SHA-256 generation and verification;
- build provenance attestation; and
- final release collision/immutability checks before publication.

The release targets commit:

```text
f5a2eaf23893cf3cb40f93c55f642e8caab446f0
```

## Detection evidence

AegisLog includes automated and synthetic regression testing designed to prevent known detection behavior from silently regressing.

These tests are **engineering regression evidence, not a claim of universal real-world detection accuracy**.

Real-world effectiveness depends on telemetry quality, environment, configuration, attack behavior, and other deployment-specific conditions. AegisLog has not been independently benchmarked to establish a universal real-world detection percentage.

The repository retains tooling and documentation for future authorized external benchmarking. Genuine external evidence can be validated when supplied, but independent external benchmarking is not a v1.6.1 publication requirement.

## AI Analyst

AI assistance is optional and does not replace AegisLog's deterministic detection and correlation pipeline.

```text
Logs
  ↓
Deterministic detection & correlation
  ↓
Investigation findings
  ↓
Optional AI Analyst
```

Remote AI requires explicit opt-in. Provider context is bounded and redacted before transmission. Local-provider workflows can be used without intentionally sending investigation context to a remote AI service.

## Safety model

AegisLog is designed for defensive investigation. It does not automatically remediate hosts, modify source telemetry, change host security policies, deploy persistence, steal credentials, evade security controls, or perform exploitation workflows.

Findings, anomalies, incident priorities, confidence values, and ATT&CK mappings should be treated as **investigative signals rather than proof of compromise or attribution**.

## Windows security notice

The v1.6.1 Windows executable is distributed without Authenticode signing. Windows SmartScreen or endpoint-security reputation warnings may therefore occur, particularly for a newly published executable.

Authenticode signing was not a mandatory v1.6.1 publication gate. Verify the SHA-256 checksum before running the application.

## Contributing and feedback

AegisLog AI is an open-source defensive security project focused on practical, transparent, local-first investigation workflows.

Bug reports, reproducible test cases, defensive detection improvements, documentation contributions, and responsible security feedback are welcome.
