# AegisLog AI v1.4.6

AegisLog AI v1.4.6 is a focused Windows terminal polish and launch-readiness update built on v1.4.5.

## Fixed

- Live single-file monitoring now prints the initial analyzed dashboard immediately before entering continuous refresh mode.
- Multi-source live SOC now prints the initial correlated dashboard immediately before continuous monitoring starts.
- Native live monitoring now prints its initial analyzed snapshot immediately.
- Users no longer need to press Ctrl+C just to reveal the first live scan result in affected Windows terminal environments.
- Live monitoring continues normally after the first result is shown, with clear status text explaining that the initial scan is complete.
- Incident explanations now use the shared AegisLog semantic terminal theme instead of mostly plain white output.
- Incident severity, confidence, MITRE context, evidence, safe investigation steps, analyst notes, and panel borders are now color-coded while retaining readable labels.

## Quality

- Added regression coverage for immediate live snapshot rendering and semantic incident-explanation colors.
- Verified the fix through CI, security checks, package builds, and the Windows single-executable workflow before release preparation.
- Release metadata is version-locked to v1.4.6 to prevent mismatched package, executable, and release assets.

## Customer delivery

The Windows release is a single `AegisLog.exe` console executable. No Python installation or virtual environment is required for the released EXE.

A matching `AegisLog.exe.sha256` checksum is published beside the executable.

## Security model

AegisLog remains defensive, local-first, and read-only. Findings and correlations are investigative signals rather than proof of compromise. The application does not automatically change accounts, firewall rules, services, or system configuration.

## Windows note

The executable is currently unsigned. Windows SmartScreen or antivirus products may show reputation-based warnings even when the published SHA-256 checksum matches.
