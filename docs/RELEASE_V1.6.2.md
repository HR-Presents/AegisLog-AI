# AegisLog AI v1.6.2

AegisLog AI v1.6.2 is a focused patch release based on real Windows testing of the v1.6.1 executable.

## What changed

### Ollama reliability

- Increase the local Ollama request timeout so CPU-only systems have enough time to load and answer with local models.
- Keep remote-provider timeout behavior unchanged.
- Improve the timeout error so users can distinguish a slow local model from an unavailable Ollama server.

### Report correctness

- Parse ISO-style log lines such as `2026-09-02T12:00:18Z ERROR firewall[903]: ...` with service context intact.
- Preserve service names such as `firewall`, `sshd`, `app`, `sudo`, and `backup` instead of collapsing them to `unknown`.
- Prevent unrelated operational findings from being grouped into one misleading correlated incident when structured service/source context is available.
- Preserve compatibility for generic inputs that do not provide service or source context.

### Investigation report redesign

- Replace the dense report layout with a clearer analyst-oriented hierarchy.
- Use four prominent summary cards and a stronger "What needs attention" section.
- Present incidents and findings as clearer evidence/action cards.
- Separate telemetry into readable summary cards.
- Move anomaly and methodology sections below the core investigation evidence.
- Improve spacing, typography, responsive behavior, and Print / Save PDF output while retaining the restrained navy/teal/white product style.

## Security and analysis model

AegisLog remains local-first, read-only, and defensive. Core detection and correlation remain deterministic. Optional AI assistance does not modify detection results. Remote AI remains opt-in.

Automated and synthetic regression tests validate engineering behavior, but AegisLog does not claim a universal real-world detection-accuracy percentage without independent benchmarking.

## Windows release assets

The release workflow publishes exactly:

- `AegisLog.exe`
- `AegisLog.exe.sha256`

The executable is not Authenticode-signed, so Windows SmartScreen may display a warning on some systems. Verify the SHA-256 checksum before use.

## Validation

The release candidate must pass the repository CI suite, security checks, dependency audit, synthetic detection regression gate, package validation, lock audits, Windows one-file build, Windows smoke tests, checksum verification, and provenance attestation before publication.
