# AegisLog AI v1.6.3

AegisLog AI v1.6.3 is a focused acceptance-test patch following real Windows validation of v1.6.2.

## What changed

### Correct product version in Mission Control

- Mission Control now reads the version from runtime package metadata instead of a hard-coded historical string.
- The packaged Windows executable therefore reports the same release identity in both `--version` and the interactive console banner.
- Regression coverage verifies the console header contains the current package version and does not regress to `v1.6.1`.

### More grounded AI Analyst responses

- The AI Analyst prompt now requires factual claims to be grounded in supplied findings and log excerpts.
- It explicitly prevents unsupported assertions about IP trust, reputation, ownership, compromise, malicious intent, malware, or successful access.
- It forbids invented numeric confidence percentages and requires qualitative confidence with evidence.
- Brute force, scanning, exploitation, and coordinated activity must be framed as hypotheses unless evidence directly establishes them.
- Verification and context collection are required before disruptive actions such as blocking, credential changes, or containment are recommended.

## Confirmed real-world behavior

During Windows acceptance testing, the local Ollama path successfully returned a `llama3.2` AI Analyst response, confirming that the v1.6.2 local-model timeout fix resolved the previously observed timeout on the tested CPU-only system.

## Security model

AegisLog remains local-first, read-only, and defensive. Core detection and correlation remain deterministic. Optional AI assistance does not modify deterministic findings. Remote AI remains opt-in.

## Windows release assets

The guarded release workflow publishes exactly:

- `AegisLog.exe`
- `AegisLog.exe.sha256`

The executable is not Authenticode-signed, so Windows SmartScreen may display a warning. Verify the SHA-256 checksum before use.
