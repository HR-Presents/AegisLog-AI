# AegisLog AI v1.4.5

AegisLog AI v1.4.5 is a focused multi-source SOC usability and Windows terminal reliability update built on v1.4.4.

## Fixed

- Fixed Option 3 multi-source live monitoring so it no longer uses the alternate terminal screen in the interactive Windows experience.
- Preserved the normal console buffer so terminal history remains available while the multi-source SOC runs.
- Forced visible dashboard refreshes so the live SOC remains responsive even when no new lines arrive.
- Replaced the semicolon-only interactive path entry with a guided File 1, File 2, then Start/Add-more flow.
- Improved drag-and-drop usability by accepting one log file at a time instead of requiring users to manually combine paths.
- Added duplicate-source protection so the same file is not accidentally added twice.
- Kept CLI `live-multi` behavior compatible for scripted and advanced usage.

## Quality

- Verified the multi-source changes through CI, security checks, package builds, and the Windows single-executable workflow before release preparation.
- Release metadata is version-locked to v1.4.5 to prevent mismatched package, executable, and release assets.

## Customer delivery

The Windows release is a single `AegisLog.exe` console executable. No Python installation or virtual environment is required for the released EXE.

A matching `AegisLog.exe.sha256` checksum is published beside the executable.

## Security model

AegisLog remains defensive, local-first, and read-only. Findings and correlations are investigative signals rather than proof of compromise. The application does not automatically change accounts, firewall rules, services, or system configuration.

## Windows note

The executable is currently unsigned. Windows SmartScreen or antivirus products may show reputation-based warnings even when the published SHA-256 checksum matches.
