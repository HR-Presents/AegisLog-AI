# Release security and reproducibility

AegisLog release workflows run tests, linting, Bandit, dependency audit, package validation, executable smoke tests, SHA-256 checksum generation, and artifact-provenance steps. These controls improve release quality, but checksums and provenance do not replace code signing or make a build bit-for-bit reproducible.

## Current reproducibility status

This hardening branch pins the Python package build backend (`setuptools==84.0.0`) and direct release/build tools in `packaging/build-tools.txt` (`build==1.6.0`, `twine==7.0.0`, and `pyinstaller==6.22.2`). Package, Windows-executable, and v1.6.0 release workflows consume those direct pins.

Runtime/customer-bundle dependencies are now transitively pinned and SHA-256 locked in `packaging/runtime-lock.txt`. The lock contains the eight universal wheels required by the customer bundle (`rich`, `typer`, `colorama`, and their resolved runtime dependencies). The exact wheel set and hashes were independently resolved on the supported GitHub-hosted `ubuntu-24.04` and `windows-2025` runners with Python 3.12 and matched across both platforms. `pip download --require-hashes` now enforces that lock in both the dedicated runtime-lock audit and the Linux/Windows customer-bundle builds. The lock file is also copied into the customer bundle as `RUNTIME_LOCK.txt` for traceability.

The active CI, security, package, Windows single-executable, runtime-lock-audit, and v1.6.0 release workflows reference GitHub Actions by immutable commit SHA rather than moving major-version tags. Those workflows also use explicit hosted OS labels (`ubuntu-24.04` and `windows-2025`) instead of `*-latest` aliases.

These are material reproducibility and supply-chain improvements, not a bit-for-bit reproducibility guarantee. Transitive dependencies of the **build/release toolchain** are not yet fully hash-locked, and GitHub can refresh the underlying VM image associated with a fixed OS label. Two builds can therefore still execute with different preinstalled tool revisions even when the source, direct tool pins, runtime lock, action SHAs, and OS label text are unchanged.

Any lock update should be a normal reviewed pull request that:

1. changes dependency versions and hashes intentionally;
2. verifies the locked wheel set on both supported hosted OS targets;
3. runs unit, security, package, installer, executable, and CLI smoke checks;
4. records material compatibility or security changes in the changelog; and
5. is merged before a release tag is created.

The runtime lock, direct tool pins, action SHAs, and explicit OS labels in this branch should be updated only through that review process. Do not silently replace exact pins or hashes during a release run.

## Windows code signing

The generated `AegisLog.exe` is currently unsigned. Production distribution should use an organization-controlled Windows code-signing identity and sign the final executable before checksum generation/publication. Verification should fail when the expected signature is absent or invalid.

This repository cannot safely include the signing private key. External setup is required, such as an EV/OV code-signing certificate backed by a hardware/security service or a managed signing provider. CI then needs narrowly scoped credentials or workload identity for that service. Those credentials are not available in this hardening work, so no signing step is fabricated or bypassed here.

## Artifact provenance

The package workflow requests GitHub build provenance for tagged Python/package-bundle artifacts. The Windows single-executable workflow requests provenance for non-PR builds, and the v1.6.0 release workflow requests provenance for the staged `AegisLog.exe` before upload. The provenance action itself is pinned by immutable commit SHA and receives only the permissions required for attestations in jobs that need it.

These workflow definitions bind eligible artifacts to repository/workflow/source identity when the attestation service is available. Ordinary pull-request runs skip release attestation where appropriate. Because this hardening work does not publish a tag or release, the release-path attestation has not been validated by an actual authorized release execution yet; it should not be described as fully release-validated until that occurs.

Consumers should verify provenance in addition to checksums and, once configured, Windows code signatures.

## Release gate

Before calling a build production-ready for external distribution, require all of the following: green test/security/runtime-lock/package/Windows smoke workflows, reviewed hash-locked runtime inputs, reviewed fully locked build-tool inputs, code-signature verification on Windows artifacts, successful provenance/attestation verification, checksum verification, and a release built from the exact reviewed commit/tag. Any missing gate should be documented in the release notes instead of silently waived.
