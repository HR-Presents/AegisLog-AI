# Release security and reproducibility

AegisLog release workflows run tests, linting, Bandit, dependency audit, package validation, executable smoke tests, SHA-256 checksum generation, and artifact-provenance steps. These controls improve release quality, but checksums and provenance do not replace code signing or make a build bit-for-bit reproducible.

## Current reproducibility status

This hardening branch pins the Python package build backend (`setuptools==84.0.0`) and direct release/build tools in `packaging/build-tools.txt` (`build==1.6.0`, `twine==7.0.0`, and `pyinstaller==6.22.2`). Package, Windows-executable, and v1.6.0 release workflows consume those direct pins.

The active CI, security, package, Windows single-executable, and v1.6.0 release workflows also reference `actions/checkout`, `actions/setup-python`, artifact upload/download actions, and the provenance action by immutable commit SHA rather than moving major-version tags.

That is a material reproducibility and supply-chain improvement, not a bit-for-bit reproducibility guarantee. Runtime/customer-bundle dependencies are still not fully transitively locked with reviewed hashes, and GitHub-hosted `*-latest` runner images evolve. Two builds of the same source commit can therefore still execute on different runner images or resolve different transitive Python packages.

A production release process should add a reviewed lock or constraints mechanism containing transitive dependencies and hashes for each supported build platform and record the runner/toolchain identity in release metadata. Any lock update should be a normal reviewed pull request that:

1. updates dependency versions and hashes intentionally;
2. runs unit, security, package, installer, executable, and CLI smoke checks;
3. records material compatibility or security changes in the changelog; and
4. is merged before a release tag is created.

The direct tool pins and action SHAs in this branch should be updated only through that review process. Do not silently replace exact pins during a release run.

## Windows code signing

The generated `AegisLog.exe` is currently unsigned. Production distribution should use an organization-controlled Windows code-signing identity and sign the final executable before checksum generation/publication. Verification should fail when the expected signature is absent or invalid.

This repository cannot safely include the signing private key. External setup is required, such as an EV/OV code-signing certificate backed by a hardware/security service or a managed signing provider. CI then needs narrowly scoped credentials or workload identity for that service. Those credentials are not available in this hardening work, so no signing step is fabricated or bypassed here.

## Artifact provenance

The package workflow now requests GitHub build provenance for tagged Python/package-bundle artifacts. The Windows single-executable workflow requests provenance for non-PR builds, and the v1.6.0 release workflow requests provenance for the staged `AegisLog.exe` before upload. The provenance action itself is pinned by immutable commit SHA and receives only the permissions required for attestations in jobs that need it.

These workflow definitions bind eligible artifacts to repository/workflow/source identity when the attestation service is available. Ordinary pull-request runs skip release attestation where appropriate. Because this hardening work does not publish a tag or release, the release-path attestation has not been validated by an actual authorized release execution yet; it should not be described as fully release-validated until that occurs.

Consumers should verify provenance in addition to checksums and, once configured, Windows code signatures.

## Release gate

Before calling a build production-ready for external distribution, require all of the following: green test/security/package/Windows smoke workflows, reviewed fully locked build inputs, code-signature verification on Windows artifacts, successful provenance/attestation verification, checksum verification, and a release built from the exact reviewed commit/tag. Any missing gate should be documented in the release notes instead of silently waived.
