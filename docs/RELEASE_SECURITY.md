# Release security and reproducibility

AegisLog release workflows run tests, linting, Bandit, dependency audit, package validation, executable smoke tests, and SHA-256 checksum generation. These controls improve release quality, but checksums alone do not establish publisher identity or make a build reproducible.

## Current reproducibility status

This hardening branch pins the Python package build backend (`setuptools==84.0.0`) and direct release/build tools in `packaging/build-tools.txt` (`build==1.6.0`, `twine==7.0.0`, and `pyinstaller==6.22.2`). Package, Windows-executable, and v1.6.0 release workflows consume those direct pins.

That is a reproducibility improvement, not a bit-for-bit reproducibility guarantee. Runtime/customer-bundle dependencies are still resolved from version ranges, transitive build dependencies are not locked with hashes, GitHub Actions are referenced by major tags instead of immutable commit SHAs, and GitHub-hosted `*-latest` runner images evolve. Two builds of the same source commit can therefore still resolve different inputs or execute on different runner images.

A production release process should add a reviewed lock or constraints mechanism containing transitive dependencies and hashes for each supported build platform, pin action revisions by immutable commit SHA, and record the runner/toolchain identity in release metadata. Any lock update should be a normal reviewed pull request that:

1. updates dependency versions and hashes intentionally;
2. runs unit, security, package, installer, executable, and CLI smoke checks;
3. records material compatibility or security changes in the changelog; and
4. is merged before a release tag is created.

The direct tool pins in this branch should be updated only through that review process. Do not silently replace exact pins during a release run.

## Windows code signing

The generated `AegisLog.exe` is currently unsigned. Production distribution should use an organization-controlled Windows code-signing identity and sign the final executable before checksum generation/publication. Verification should fail when the expected signature is absent or invalid.

This repository cannot safely include the signing private key. External setup is required, such as an EV/OV code-signing certificate backed by a hardware/security service or a managed signing provider. CI then needs narrowly scoped credentials or workload identity for that service. Those credentials are not available in this hardening work, so no signing step is fabricated or bypassed here.

## Artifact provenance

A SHA-256 file allows consumers to detect accidental or malicious changes only when they already trust the checksum source. Stronger provenance should bind the artifact to the repository, workflow, source commit, and build identity using a supported attestation mechanism. The release process should publish and verify that attestation in addition to checksums and code signing.

Provenance is not currently enforced, so release artifacts should not be described as supply-chain-attested until that workflow/external setup is completed and validated.

## Release gate

Before calling a build production-ready for external distribution, require all of the following: green test/security/package/Windows smoke workflows, reviewed fully locked build inputs, code-signature verification on Windows artifacts, provenance/attestation verification, checksum verification, and a release built from the exact reviewed commit/tag. Any missing gate should be documented in the release notes instead of silently waived.
