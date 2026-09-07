# Release security and reproducibility

AegisLog release workflows already run tests, linting, Bandit, dependency audit, package validation, executable smoke tests, and SHA-256 checksum generation. These controls improve release quality, but checksums alone do not establish publisher identity or make a build reproducible.

## Current reproducibility status

The current package and Windows workflows install build tools and dependencies from version ranges or unconstrained package names, and GitHub-hosted runner images also evolve. As a result, two builds of the same source commit can resolve different dependency versions or execute on different runner images.

A future release workflow should use a reviewed lock or constraints file that includes transitive dependencies and hashes for the supported build platform, pin action revisions by immutable commit SHA, and record the runner/toolchain identity in release metadata. Any lock update should be a normal reviewed pull request that:

1. updates dependency versions and hashes intentionally;
2. runs unit, security, package, installer, and CLI smoke checks;
3. records material compatibility or security changes in the changelog; and
4. is merged before a release tag is created.

Pinning only direct tools such as `build`, `twine`, or `pyinstaller` is useful but is not sufficient to claim bit-for-bit reproducibility.

## Windows code signing

The generated `AegisLog.exe` is currently unsigned. Production distribution should use an organization-controlled Windows code-signing identity and sign the final executable before checksum generation/publication. Verification should fail when the expected signature is absent or invalid.

This repository cannot safely include the signing private key. External setup is required, such as an EV/OV code-signing certificate backed by a hardware/security service or a managed signing provider. CI then needs narrowly scoped credentials/identity federation for that service. Those credentials are not available in this hardening work, so no signing step is fabricated or bypassed here.

## Artifact provenance

A SHA-256 file allows consumers to detect accidental or malicious changes only when they already trust the checksum source. Stronger provenance should bind the artifact to the repository, workflow, source commit, and build identity using a supported attestation mechanism. The release process should publish and verify that attestation in addition to checksums and code signing.

Provenance is not currently enforced, so release artifacts should not be described as supply-chain-attested until that external/workflow setup is completed and validated.

## Release gate

Before calling a build production-ready for external distribution, require all of the following: green test/security/package/Windows smoke workflows, reviewed locked build inputs, code-signature verification on Windows artifacts, provenance/attestation verification, checksum verification, and a release built from the exact reviewed commit/tag. Any missing gate should be documented in the release notes instead of silently waived.
