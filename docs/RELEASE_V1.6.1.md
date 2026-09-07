# AegisLog AI v1.6.1

AegisLog AI v1.6.1 is the hardened follow-up to the existing public v1.6.0 release. It preserves the local-first, read-only defensive model while adding the production hardening, privacy controls, deterministic build gates, signing verification, and external-evidence requirements developed in this branch.

## Highlights

- Added an analyst triage summary to investigations using existing severity and confidence signals, with explicit non-attribution guidance.
- Improved Windows Event Log, journald, and Docker diagnostics by distinguishing unsupported sources from temporarily unavailable sources and providing source-specific read-only troubleshooting guidance.
- Hardened single-file and multi-source live monitoring so temporary source loss is reported clearly, the current dashboard stays visible, recovery is recognized, and monitoring resumes safely.
- Improved long-running multi-source memory behavior by aggregating arrival history, bounding arrival buckets, and bounding alert fingerprint state.
- Added focused regression coverage for investigation triage, native diagnostics, source loss/recovery, bounded runtime state, authentication correlation, streaming, provider transport, release evidence, and privacy boundaries.
- Preserved deterministic local analysis as the primary workflow. Findings, anomaly scores, incident priorities, and ATT&CK mappings are investigative signals and are not proof of compromise, attribution, or attacker intent.
- Remote AI is disabled by default. Core analysis and local Ollama workflows do not require remote-network consent; remote providers require explicit `AEGISLOG_ALLOW_REMOTE_AI` opt-in.
- Outbound application networking is centralized in `providers.py` and enforced by regression tests so alternate application modules cannot silently introduce a second remote-egress path.
- Release evidence must be based on a real sanitized, independently labeled external dataset and bound to the exact release commit.
- Windows publication is fail-closed unless the executable passes the approved Authenticode signer and timestamp verification gates.

## Distribution

The hardened GitHub release is intended to publish the standalone Windows `AegisLog.exe` plus `AegisLog.exe.sha256`. The executable does not require a separate Python installation or virtual environment for normal customer use.

The already-published v1.6.0 release remains historical and unchanged. Its release notes state that its executable was unsigned. v1.6.1 must not be published unless the repository's current signing, checksum, provenance, CI, and external-evidence gates pass.

## Safety model

AegisLog remains defensive and read-only. It does not automatically remediate hosts, modify source telemetry, change host security policy, deploy persistence, steal credentials, evade security controls, or provide exploitation tooling.

## Release operator checklist

The hardened release path is fail-closed. Do not substitute placeholder credentials, fabricated reviewer metadata, synthetic telemetry, or a manual checkbox for the required evidence.

Before an authorized release:

1. Confirm the candidate commit is the exact reviewed commit intended for release and that it is on `main`.
2. Confirm all required CI, security, package, Windows-build, runtime-lock, build-lock, and validation-lock workflows are green for the release candidate.
3. Have an organization administrator provision the real Windows signing material outside the repository and chat systems:
   - `WINDOWS_SIGNING_PFX_BASE64`
   - `WINDOWS_SIGNING_PFX_PASSWORD`
   - `WINDOWS_SIGNING_CERT_THUMBPRINT`
   - `WINDOWS_SIGNING_TIMESTAMP_URL`
4. Prepare an authorized, minimized, sanitized, independently labeled external JSONL evaluation dataset. Do not commit the underlying production/customer telemetry merely to run the evaluation.
5. Generate the release evidence from the actual dataset and exact candidate commit using `tools/build_external_evidence.py` with real provenance, labeling procedure, reviewer metadata, `--independent-labeling`, and `--sanitized`.
6. Review `evaluation/external-release-evidence.json` for accuracy and ensure it identifies the exact release commit.
7. Run the release preflight. It must validate repository/ref, release tag/version/confirmation, signing thumbprint, HTTPS timestamp URL, and external evidence.
8. Authorize the release only after the preflight is green. The workflow must build, sign, verify, checksum, attest, and then publish.
9. After publication, perform a clean-install smoke test using the published artifact and verify its signature and checksum.

Do not release if signing, external evidence, CI, preflight, checksum verification, provenance, or post-build smoke testing fails.

## Verification

Verify the downloaded executable against the accompanying SHA-256 file and verify the Authenticode signature and approved signer identity. The v1.6.1 release workflow refuses to overwrite or reuse an existing `v1.6.1` tag or GitHub release.
