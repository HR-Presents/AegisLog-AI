# Release security and reproducibility

AegisLog release workflows run tests, linting, Bandit, dependency audit, package validation, executable smoke tests, SHA-256 checksum generation, and artifact-provenance steps. These controls improve release quality, but checksums and provenance do not replace code signing or make a build bit-for-bit reproducible.

## Current reproducibility status

The reviewed direct artifact-build inputs are pinned in `packaging/build-tools.txt`: `pip==26.2.1`, `setuptools==84.0.0`, `build==1.6.0`, `twine==7.0.0`, and `pyinstaller==6.22.2`.

Their resolved transitive dependencies are SHA-256 locked separately for Python 3.12 on the two supported build environments:

- `packaging/build-lock-linux.txt` for `ubuntu-24.04`;
- `packaging/build-lock-windows.txt` for `windows-2025`.

The platform split is deliberate. Universal artifacts share hashes where appropriate, while platform-specific artifacts such as PyInstaller, `charset-normalizer`, `nh3`, `cffi`/`cryptography`, `pefile`, and `pywin32-ctypes` are locked to the wheel actually used by that build environment.

`.github/workflows/build-lock-audit.yml` independently resolves `packaging/build-tools.txt` on Linux and Windows, compares the exact name/version/artifact-hash set against the corresponding reviewed lock, and then performs a `pip download --require-hashes` verification. A changed direct version, dependency resolution, selected wheel, or artifact hash therefore fails the audit instead of silently changing the build environment.

Package and Windows executable workflows install these lockfiles with `--require-hashes`. Python package construction uses `python -m build --no-isolation`, so the build does not create a fresh isolated environment that re-downloads an unreviewed `setuptools`. The Windows executable path also installs the reviewed runtime lock and then installs AegisLog itself with `--no-deps --no-build-isolation`, preventing editable installation from resolving a second dependency set or creating a temporary build environment.

Runtime/customer-bundle dependencies are independently transitively pinned and SHA-256 locked in `packaging/runtime-lock.txt`. The eight universal runtime wheels were resolved on both `ubuntu-24.04` and `windows-2025` with Python 3.12 and produced the same hashes. Runtime-lock audit and customer-bundle workflows enforce that lock with `--require-hashes`, and the bundle includes `RUNTIME_LOCK.txt` for traceability.

## Release validation toolchain

The actual v1.6.0 release-validation environment is Python 3.12 on `ubuntu-24.04`. Its direct validation tools are exact pins in `packaging/validation-tools.txt`: `pytest==9.1.1`, `ruff==0.16.6`, `bandit==1.9.4`, and `pip-audit==2.10.1`.

Their complete resolved wheel set is SHA-256 locked in `packaging/validation-lock-py312-linux.txt`. `.github/workflows/validation-lock-audit.yml` independently re-resolves the direct validation pins, compares the exact name/version/artifact-hash set to the reviewed lock, and performs a `pip download --require-hashes` verification.

The v1.6.0 release validation job now installs, in order, the reviewed Linux build lock, validation lock, and runtime lock, then installs AegisLog with `--no-deps --no-build-isolation`. It therefore runs Ruff, pytest, the labeled detection evaluation, Bandit, pip-audit, package construction, and Twine checks without resolving an unreviewed dev-extra dependency graph.

The Python 3.12 CI lane exercises this same exact locked release-validation stack on every pull request. Python 3.10, 3.11, and 3.13 CI lanes remain compatibility tests and still use the project dev-extra ranges; their tool versions may drift and should not be treated as the reproducible release environment.

The active CI, security, package, Windows single-executable, runtime-lock-audit, build-lock-audit, validation-lock-audit, and v1.6.0 release workflows reference GitHub Actions by immutable commit SHA and use explicit hosted OS labels rather than `*-latest` aliases.

These controls materially reduce dependency and workflow drift, but they are not a bit-for-bit reproducibility guarantee. GitHub can refresh the underlying VM image behind a fixed OS label. Compatibility CI lanes outside Python 3.12 also remain intentionally less reproducible than the release-validation lane.

Any dependency lock update should be a reviewed pull request that intentionally changes versions/hashes, verifies the lock on the supported OS target, runs security/package/installer/executable/CLI gates, and is merged before a release tag is created. Do not regenerate or relax hashes during a release run.

## Windows code signing

The generated `AegisLog.exe` is currently unsigned. Production distribution should use an organization-controlled Windows code-signing identity and sign the final executable before checksum generation/publication. Verification should fail when the expected signature is absent or invalid.

The signing private key must not be stored in this repository. External setup is required, such as an EV/OV code-signing certificate backed by a hardware/security service or a managed signing provider, with narrowly scoped CI credentials or workload identity. Those credentials are not available in this hardening work, so no signing step is fabricated or bypassed.

## Artifact provenance

The package workflow requests GitHub build provenance for tagged Python/package-bundle artifacts. The Windows single-executable workflow requests provenance for non-PR builds, and the v1.6.0 release workflow requests provenance for the staged `AegisLog.exe` before upload. The provenance action is pinned by immutable commit SHA and receives scoped attestation permissions only where required.

Ordinary pull-request runs skip release attestation where appropriate. Because this hardening work does not publish a tag or release, the v1.6.0 release-path attestation has not been validated by an actual authorized release execution and must not be described as fully release-validated yet.

Consumers should verify provenance in addition to checksums and, once configured, Windows code signatures.

## Release gate

Before calling a build production-ready for external distribution, require green test/security/runtime-lock/build-lock/validation-lock/package/Windows smoke workflows, reviewed locked runtime/build/release-validation inputs, Windows code-signature verification, successful provenance verification, checksum verification, and a release built from the exact reviewed commit/tag. Any missing gate should be documented rather than silently waived.
