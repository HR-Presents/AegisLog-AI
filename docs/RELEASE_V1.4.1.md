# AegisLog AI v1.4.1

AegisLog AI v1.4.1 is a focused Windows customer-experience release built from real-machine acceptance testing of the v1.4.0 single-file executable.

## Highlights

- Live file monitoring now clearly explains that it follows NEW lines appended after monitoring starts by default.
- `--from-start` is documented directly at monitor startup when customers intentionally want existing file contents processed too.
- The live dashboard renames the confusing lifetime `Event rate` metric to `Average rate`.
- Live status now distinguishes waiting for new lines, receiving activity, and time since the last activity.
- Rolling rate-spike wording is clearer and tied to the rolling baseline window.
- Growing versions of the same live finding are collapsed so a brute-force finding evolving from 5 to 6 failed logins does not appear as duplicate dashboard rows.
- Empty live-finding messaging is clearer for first-time users.
- Regression coverage reproduces the real Windows test scenario of repeated SSH authentication failures from the same source.

## Customer download

Windows customers need only:

- `AegisLog.exe`
- `AegisLog.exe.sha256` (optional checksum verification)

No Python installation, virtual environment, requirements file, installer, or support folder is required. Double-click `AegisLog.exe` to open the terminal control center, or run commands directly from a terminal.

## Safety model

AegisLog remains defensive, local-first, and read-only. Monitoring and native collectors read telemetry only; they do not change accounts, firewall rules, services, registry settings, privileges, or system configuration. External AI is used only when explicitly configured and supported data is redacted before transmission.

## Windows notice

The Windows executable is not digitally signed. Windows SmartScreen or antivirus products may therefore show a warning, especially for a newly published build. Verify the SHA-256 checksum when desired.
