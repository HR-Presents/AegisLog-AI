# AegisLog screenshot assets

This directory is reserved for **real product screenshots** captured from a verified Windows build. Do not add mockups, generated UI images, or screenshots whose source build cannot be identified.

## Current capture source

The current PR screenshot set must come from the CI-validated Windows artifact built from:

```text
cbbc194490482c1c7c81140ac2fce67ed955c60e
```

Artifact metadata:

```text
Name: AegisLog-Windows-Single-EXE
Artifact ID: 10063724053
Artifact digest: sha256:2982d85450093b7c48f29c44ca9f476c6a93392bfb13e03d7991250d0e5fee49
```

See [`../../SCREENSHOT_CAPTURE.md`](../../SCREENSHOT_CAPTURE.md) for the full capture and sanitization procedure.

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
- the commit message or PR discussion records the source build SHA.

If a clean capture cannot be produced, leave the screenshot absent rather than substituting a mockup.
