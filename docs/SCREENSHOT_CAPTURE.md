# AegisLog README Screenshot Capture Guide

This guide defines how to capture **real product screenshots** for the AegisLog README from a verified Windows build. It exists to prevent mocked, stale, or misleading screenshots from being published.

## Verified source build

Use the exact Windows artifact produced from commit:

```text
cbbc194490482c1c7c81140ac2fce67ed955c60e
```

Validated GitHub Actions artifact:

```text
Name: AegisLog-Windows-Single-EXE
Artifact ID: 10063724053
Artifact digest: sha256:2982d85450093b7c48f29c44ca9f476c6a93392bfb13e03d7991250d0e5fee49
```

Do not label screenshots from another commit as representing this build.

## Capture rules

- Use the actual `AegisLog.exe` from the artifact above.
- Capture on Windows, using a normal terminal window at a readable size.
- Do not crop away warnings, status lines, source paths, or evidence context in a way that changes meaning.
- Do not use production logs, credentials, real customer data, private hostnames, private IP addressing, tokens, or personal information.
- Prefer repository-provided example logs or deliberately synthetic data.
- Do not manually edit findings, counts, risk state, incidents, evidence, or report text after capture.
- UI-only cropping is acceptable for framing, but never alter the product output.
- Record the commit SHA used for each screenshot in the pull request or commit message that adds it.

## Required screenshot set

### 1. Mission Control / home

Launch:

```powershell
.\AegisLog.exe
```

Capture the full primary command surface at a normal desktop terminal width. The screenshot should show the AegisLog identity and the main operator workflow without opening unrelated menus.

Recommended output path:

```text
docs/assets/screenshots/aegislog-mission-control.png
```

### 2. Investigation dashboard

From the repository root, use a sanitized example log:

```powershell
.\AegisLog.exe dashboard .\examples\auth.log
```

Capture a view that includes the investigation summary and Analyst Focus section. If the example produces correlated incidents, keep the incident-led prioritization visible.

Recommended output path:

```text
docs/assets/screenshots/aegislog-investigation-dashboard.png
```

### 3. Incident / evidence workflow

First inspect incidents:

```powershell
.\AegisLog.exe incidents .\examples\auth.log
```

Then investigate a real incident ID returned by the build:

```powershell
.\AegisLog.exe investigate .\examples\auth.log <incident-id>
```

Capture the incident summary, evidence preview, and safe next steps if they fit in one readable frame.

Recommended output path:

```text
docs/assets/screenshots/aegislog-incident-investigation.png
```

### 4. HTML investigation report

Generate or open the report using the command supported by the exact build. Use `AegisLog.exe --help` and the relevant command help if needed rather than guessing syntax.

Capture the executive first page showing posture, disposition, primary analyst decision, severity distribution, and prioritized triage.

Recommended output path:

```text
docs/assets/screenshots/aegislog-executive-report.png
```

## Recommended terminal presentation

Use a standard Windows terminal configuration with:

- readable monospace font
- 100% display scale if practical
- no transparent background
- no personal shell prompt customizations in the frame
- enough width that the full-width layout is visible
- no unrelated desktop notifications or account information

Do not force a theme that changes AegisLog colors or contrast.

## Sanitization checklist

Before committing any screenshot, visually confirm it contains none of the following:

- credentials or API keys
- email addresses
- real usernames
- customer names
- real production hostnames
- internal domains
- secrets or bearer tokens
- sensitive filesystem paths
- personal data
- real production log lines

If any appear, re-run the product with sanitized data and recapture. Do not blur sensitive data and then publish the screenshot when a clean synthetic capture can be produced instead.

## README placement

When the four images are available, replace the current screenshot placeholder in `README.md` with a compact product gallery. Each image should have a short factual caption and should reference only behavior visible in that exact build.

Suggested order:

1. Mission Control
2. Investigation dashboard
3. Incident investigation
4. Executive report

The README should never imply that a screenshot comes from the stable `v1.6.0` release unless it was actually captured from the published `v1.6.0` executable. For PR screenshots, identify them as a preview of the validated PR build until that build is released.
