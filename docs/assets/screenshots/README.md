# AegisLog screenshot assets

This directory is reserved for **real product screenshots** captured from a verified Windows build. Do not add mockups, generated UI images, or screenshots whose source build cannot be identified.

## Current PR preview capture source

The current PR screenshot set must come from the CI-validated Windows artifact built from:

```text
7b5269e8990fcd3743f28bfaea720dfd00828060
```

Temporary GitHub Actions validation artifact:

```text
Name: AegisLog-Windows-Single-EXE
Artifact ID: 10074199022
Artifact digest: sha256:2514932a6687f045fa6877de20c42c70db892a1dd20808f013a43a4dbb819720
```

This artifact is temporary CI evidence. It is not the permanent customer download channel and must not be presented as a stable release asset. Permanent customer downloads are published as GitHub Release assets only after the guarded release workflow succeeds on `main`.

See [`../../SCREENSHOT_CAPTURE.md`](../../SCREENSHOT_CAPTURE.md) for the full capture, provenance, release-channel, and sanitization procedure.

## Required filenames

Commit the verified PNG files using exactly these paths:

```text
docs/assets/screenshots/aegislog-mission-control.png
docs/assets/screenshots/aegislog-investigation-dashboard.png
docs/assets/screenshots/aegislog-incident-investigation.png
docs/assets/screenshots/aegislog-executive-report.png
```

## Intended README gallery

When all four verified images exist, the README gallery should present them in this order:

1. **Mission Control** — the primary operator command surface.
2. **Investigation dashboard** — investigation summary and Analyst Focus prioritization.
3. **Incident investigation** — correlated incident evidence and safe next steps.
4. **Executive report** — the self-contained investigation report's executive-first page.

Do not add image links to the public README before the corresponding PNG exists in this directory. This prevents broken images and avoids implying that an unverified or simulated capture is part of the product.

## Acceptance checklist

Before a screenshot is committed, verify all of the following:

- captured from the exact validated Windows executable identified above;
- product output was not manually altered after capture;
- no credentials, tokens, email addresses, personal data, customer names, internal domains, private production hostnames, or real production logs are visible;
- example or synthetic data is used;
- the screenshot remains readable at normal GitHub README width;
- cropping does not remove context in a way that changes the meaning of the output;
- the commit message or PR discussion records the source build SHA;
- PR preview screenshots are labeled as preview captures until the corresponding build is actually released;
- stable-release screenshots are only labeled as such when captured from the exact published release executable and verified against its published checksum.

If a clean capture cannot be produced, leave the screenshot absent rather than substituting a mockup.
