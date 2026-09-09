# AegisLog README Screenshot Capture Guide

This guide defines how to capture **real product screenshots** for the AegisLog README from a verified Windows build. It exists to prevent mocked, stale, or misleading screenshots from being published.

## Build provenance model

AegisLog uses two different kinds of Windows build output, and they must not be confused.

### PR preview build — temporary CI evidence

For the current Draft PR, the latest exact-head Windows build validated at the time this guide was updated is:

```text
Commit: 7b5269e8990fcd3743f28bfaea720dfd00828060
Workflow: Windows single executable #434
Artifact name: AegisLog-Windows-Single-EXE
Artifact ID: 10074199022
Artifact digest: sha256:2514932a6687f045fa6877de20c42c70db892a1dd20808f013a43a4dbb819720
```

This GitHub Actions artifact is **temporary CI evidence**. It expires according to GitHub Actions retention policy and is not the permanent customer download.

Screenshots captured from it may be used only as **validated PR-build previews**. Do not label them as stable-release screenshots.

### Stable release build — permanent customer distribution

After an approved change is merged and a guarded release is published, the canonical customer download is the Windows executable attached to the corresponding **GitHub Release**, together with its SHA-256 checksum.

Release assets are the long-term distribution source. GitHub Actions artifacts are not.

For a stable-release screenshot:

1. Download `AegisLog.exe` from the exact published GitHub Release being represented.
2. Download its published `AegisLog.exe.sha256` file.
3. Verify the executable checksum before capture.
4. Record the release tag and executable SHA-256 with the screenshot commit.
5. Label the screenshot as a stable-release screenshot only after those checks succeed.

Never imply that a PR artifact is the permanent download source, and never imply that an unreleased PR build is already a stable release.

## Capture rules

- Use the actual `AegisLog.exe` from the exact build being represented.
- Capture on Windows, using a normal terminal window at a readable size.
- Do not crop away warnings, status lines, source paths, or evidence context in a way that changes meaning.
- Do not use production logs, credentials, real customer data, private hostnames, private IP addressing, tokens, or personal information.
- Prefer repository-provided example logs or deliberately synthetic data.
- Do not manually edit findings, counts, risk state, incidents, evidence, or report text after capture.
- UI-only cropping is acceptable for framing, but never alter the product output.
- Record the exact commit SHA for PR previews, or the exact release tag and executable SHA-256 for stable-release screenshots.

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

For PR screenshots, identify them as previews of the validated PR build. For stable-release screenshots, identify the exact release represented. Never relabel a PR preview as a stable-release screenshot merely because the PR was later merged; recapture or verify against the published release asset when release fidelity matters.
