# AegisLog AI v1.6.0

AegisLog AI v1.6.0 improves analyst workflow quality, native telemetry diagnostics, live-source resilience, and long-running multi-source runtime bounds while preserving the project's local-first, read-only defensive model.

## Highlights

- Added an analyst triage summary to investigations using existing severity and confidence signals, with explicit non-attribution guidance.
- Improved Windows Event Log, journald, and Docker diagnostics by distinguishing unsupported sources from temporarily unavailable sources and providing source-specific read-only troubleshooting guidance.
- Hardened single-file and multi-source live monitoring so temporary source loss is reported clearly, the current dashboard stays visible, recovery is recognized, and monitoring resumes safely.
- Improved long-running multi-source memory behavior by aggregating arrival history, bounding arrival buckets, and bounding alert fingerprint state.
- Added focused regression coverage for investigation triage, native diagnostics, source loss/recovery, 50,000-line ingest batches, bounded runtime state, and configuration validation.
- Preserved deterministic local analysis as the primary workflow. Findings, anomaly scores, incident priorities, and ATT&CK mappings are investigative signals and are not proof of compromise, attribution, or attacker intent.
- Remote AI is disabled by default. Core analysis and local Ollama workflows do not require remote-network consent; remote providers require explicit `AEGISLOG_ALLOW_REMOTE_AI` opt-in.

## Distribution

The GitHub release publishes the standalone Windows `AegisLog.exe` plus `AegisLog.exe.sha256`. The executable does not require a separate Python installation or virtual environment for normal customer use.

Production release hardening requires the Windows executable to pass the repository's Authenticode signer and timestamp verification gates before publication. If the organization has not provisioned an approved signing identity, the release must remain blocked rather than publishing an unsigned replacement through the hardened workflow.

## Safety model

AegisLog remains defensive and read-only. It does not automatically remediate hosts, modify source telemetry, change host security policy, deploy persistence, steal credentials, evade security controls, or provide exploitation tooling.

## Release operator checklist

The hardened release path is fail-closed. Do not substitute placeholder credentials, fabricated reviewer metadata, synthetic telemetry, or a manual checkbox for the required evidence.

Before an authorized release:

1. Confirm the candidate commit is the exact reviewed commit intended for release and that it is on `main`.
2. Confirm all required CI, security, package, Windows-build, runtime-lock, build-lock, and validation-lock workflows are green for the release candidate.
3. Have an organization administrator provision the real Windows signing material outside the repository and chat systems:
   - `WINDOWS_SIGNING_PFX_BASE64` — GitHub Actions secret containing the organization-controlled PFX in the format expected by the signing adapter.
   - `WINDOWS_SIGNING_PFX_PASSWORD` — GitHub Actions secret for that PFX.
   - `WINDOWS_SIGNING_CERT_THUMBPRINT` — GitHub Actions secret containing the approved 40-hex certificate thumbprint.
   - `WINDOWS_SIGNING_TIMESTAMP_URL` — GitHub Actions variable containing the approved credential-free HTTPS RFC3161 timestamp URL.
4. Prepare an authorized, minimized, sanitized, independently labeled external JSONL evaluation dataset. Do not commit the underlying production/customer telemetry merely to run the evaluation.
5. Generate the release evidence from the actual dataset and exact candidate commit. Example:

```text
python tools/build_external_evidence.py /secure/path/sanitized_external.jsonl \
  --evaluated-commit <40-character-release-commit> \
  --provenance "Describe source population, sampling period/method, sanitization, exclusions, and deployment relevance." \
  --labeling-procedure "Describe independent labeling, adjudication, and review procedure." \
  --reviewer "<reviewer name or approved identifier>" \
  --reviewer-role "<reviewer role>" \
  --independent-labeling \
  --sanitized
```

The generator derives the dataset SHA-256, sample count, precision, recall, case accuracy, false positives, false negatives, and confidence intervals from the actual labeled corpus. It refuses to overwrite an existing evidence file and refuses generation unless sanitization and independent labeling are explicitly confirmed.

6. Review `evaluation/external-release-evidence.json` for accuracy. The evidence must describe the real evaluation and its limitations and must identify the exact release commit.
7. Run the release preflight. It must validate the repository/ref, release tag/version/confirmation, signing thumbprint, HTTPS timestamp URL, and external evidence before the release workflow proceeds.
8. Authorize the release only after the preflight is green. The workflow must build the Windows executable, sign it, verify Authenticode signer/timestamp requirements, generate and verify the SHA-256 checksum, and produce provenance/attestation before publication.
9. After publication, perform a clean-install smoke test using the published artifact and verify its signature and checksum against the published metadata.

Do not release if signing, external evidence, CI, preflight, checksum verification, provenance, or post-build smoke testing fails.

## Verification

Verify the downloaded executable against the accompanying SHA-256 file before use. For hardened releases, also verify the Authenticode signature and approved signer identity. The release workflow refuses to overwrite or reuse an existing `v1.6.0` tag or GitHub release.
