# AegisLog AI v1.6.1

AegisLog AI v1.6.1 is the hardened follow-up to the existing public v1.6.0 release. It preserves the local-first, read-only defensive model while adding production hardening, privacy controls, deterministic release gates, external-evidence requirements, and the polished terminal experience now present on `main`.

> **Release status:** v1.6.1 is not published yet. The current public stable release remains v1.6.0.

## Highlights

- Conservative analyst triage based on existing severity, confidence, timeline, and entity evidence.
- Improved Windows Event Log, journald, and Docker diagnostics with clearer unsupported-versus-unavailable states.
- Safer single-file and multi-source live monitoring during temporary source loss and recovery.
- Bounded long-running multi-source state for sustained monitoring workloads.
- Responsive, full-width terminal UX with clearer Mission Control, source input, analysis-completion, report-handoff, health, command-reference, and narrow-terminal presentation.
- Deterministic local analysis remains the primary workflow. Findings, anomalies, incident priorities, confidence values, and ATT&CK mappings are investigative signals rather than proof of compromise or attribution.
- Remote AI remains optional and explicitly opt-in; core analysis does not require an external AI service.
- External release evidence must come from a real, authorized, sanitized, independently labeled dataset and be bound to the exact code commit evaluated for the release.

## Distribution

The intended GitHub Release contains exactly:

```text
AegisLog.exe
AegisLog.exe.sha256
```

The Windows executable is built as a standalone one-file application. Normal customer use does not require a separate Python installation or virtual environment.

The current v1.6.1 release workflow stages an **unsigned** executable, verifies the published SHA-256 checksum, creates build provenance attestation, and refuses to reuse an existing `v1.6.1` tag or GitHub Release. Windows SmartScreen or endpoint-security reputation warnings may therefore occur.

Windows Authenticode signing is **not a mandatory v1.6.1 publication gate**. Signing may be introduced separately in the future, but release readiness must not be represented as blocked merely because signing material is absent.

## Safety model

AegisLog remains defensive and read-only. It does not automatically remediate hosts, modify source telemetry, change host security policy, deploy persistence, steal credentials, evade controls, or provide exploitation workflows.

## Release operator checklist

Before an authorized release:

1. Freeze the exact `main` code commit intended for v1.6.1 and ensure the required CI, security, package, Windows-build, and lock-audit workflows are acceptable for that candidate.
2. Prepare a real, authorized, minimized, sanitized, independently labeled external evaluation dataset.
3. Generate `evaluation/external-release-evidence.json` with `tools/build_external_evidence.py`, recording the exact evaluated code commit plus truthful provenance, labeling procedure, reviewer metadata, metrics, uncertainty, and limitations.
4. Commit **only** `evaluation/external-release-evidence.json` as the immediate direct single-parent child of the evaluated code commit.
5. Run `tools/release_preflight.py` through the guarded release workflow. The preflight must validate the release ref/version/confirmation, evidence binding, parentage, and allowed changed path.
6. Confirm no `v1.6.1` tag or GitHub Release already exists.
7. Dispatch `.github/workflows/release-v1.6.1.yml` from the exact evidence-only release commit on `main` using the required confirmation `RELEASE-v1.6.1`.
8. Allow the workflow to run quality/security checks, build and smoke-test the Windows executable, generate and verify its checksum, create provenance attestation, and publish the release assets.
9. After publication, download the public GitHub Release assets, verify the checksum, and perform a clean-machine smoke test using the published executable rather than a temporary Actions artifact.

Do not release if external evidence is fabricated, synthetic-only, unauthorized, circularly labeled, stale, or bound to the wrong commit; if the evidence-only commit contains unrelated changes; if preflight or required validation fails; or if post-build checksum/smoke verification fails.

## Verification

After publication, verify `AegisLog.exe` against `AegisLog.exe.sha256` and confirm the release/tag targets the intended evidence-only release commit.

GitHub Actions artifacts are temporary validation evidence. Permanent customer downloads must come from the published GitHub Release.