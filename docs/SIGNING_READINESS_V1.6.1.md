# AegisLog v1.6.1 Windows signing readiness

This checklist covers the non-code signing configuration required before the guarded `v1.6.1` release workflow can publish a Windows executable.

The repository must never contain the signing certificate, private key, PFX password, secret values, or decoded PFX bytes.

## Required GitHub configuration

An authorized repository or organization administrator must provision and verify these values outside the repository:

### Repository or organization secrets

- `WINDOWS_SIGNING_PFX_BASE64`
  - Base64 representation of the release code-signing PFX.
  - The PFX must contain the private key.
  - Do not paste the decoded PFX into issues, pull requests, logs, documentation, or chat.

- `WINDOWS_SIGNING_PFX_PASSWORD`
  - Password protecting the PFX.
  - Store only as a GitHub Actions secret.

- `WINDOWS_SIGNING_CERT_THUMBPRINT`
  - Thumbprint of the exact certificate expected to sign `AegisLog.exe`.
  - The release workflow and verification script compare the actual signer against this value and fail on mismatch.

### Repository or organization variable

- `WINDOWS_SIGNING_TIMESTAMP_URL`
  - HTTPS RFC3161 timestamp service URL approved for release signing.
  - The signing script rejects a non-HTTPS timestamp URL.

## Certificate requirements

Before provisioning the PFX, confirm that the certificate:

- is the organization-approved release identity;
- contains the Code Signing EKU (`1.3.6.1.5.5.7.3.3`);
- includes an accessible private key in the PFX;
- has a thumbprint that exactly matches `WINDOWS_SIGNING_CERT_THUMBPRINT` after normalization;
- is valid for the intended release-signing period;
- chains correctly on a clean supported Windows system;
- is permitted for software-distribution signing under the organization's certificate policy.

## What the workflow enforces

The guarded release workflow:

1. Fails during preflight if the expected signing thumbprint or timestamp URL is missing or invalid.
2. Fails during the Windows build if any required signing configuration is blank.
3. Decodes the PFX only into the ephemeral GitHub-hosted runner's temporary directory.
4. Imports the certificate into `Cert:\CurrentUser\My` as non-exportable.
5. Refuses to reuse a pre-existing certificate with the configured thumbprint on the runner.
6. Verifies that the imported certificate thumbprint matches the configured expected thumbprint.
7. Verifies the Code Signing EKU and private-key availability.
8. Signs `AegisLog.exe` with SHA-256 and an RFC3161 timestamp.
9. Re-verifies the resulting Authenticode signature, signer thumbprint, Code Signing EKU, and presence of a timestamp.
10. Removes the imported certificate and temporary PFX file from the runner after signing.

No unsigned executable should be promoted as the `v1.6.1` release asset if any of these checks fail.

## Administrator verification before release

Because GitHub does not expose secret values to workflows or repository readers, an authorized administrator must verify the configuration in repository/organization settings before dispatching the release workflow.

Record only non-secret confirmation in the release review, for example:

```text
WINDOWS_SIGNING_PFX_BASE64: configured (value not disclosed)
WINDOWS_SIGNING_PFX_PASSWORD: configured (value not disclosed)
WINDOWS_SIGNING_CERT_THUMBPRINT: configured and independently matched to release certificate
WINDOWS_SIGNING_TIMESTAMP_URL: configured and approved HTTPS RFC3161 endpoint
Certificate Code Signing EKU: verified
Certificate private key present: verified
Certificate validity period: verified
Certificate chain/trust: verified on clean Windows system
```

Do not record the PFX, password, private key, or secret values.

## Release-time evidence

A successful release run should provide observable evidence that:

- the signing step completed successfully;
- `verify_authenticode.ps1` reported a valid signature;
- the signer thumbprint matched the configured expected thumbprint;
- a timestamp signer was present;
- the staged release directory contained exactly `AegisLog.exe` and `AegisLog.exe.sha256`;
- the checksum verification passed before publication;
- the executable provenance attestation completed;
- the GitHub Release was created only after all prior gates succeeded.

## Current readiness status

Repository code contains the required fail-closed signing and verification machinery.

Actual signing-secret and variable provisioning cannot be verified from repository source code and must be confirmed by an authorized GitHub administrator. Until that confirmation exists, signing configuration remains an external release-readiness item rather than a completed gate.

This checklist does not authorize a release. PR #77 remains a Draft change set until separately approved, merged, and released through the guarded workflow.