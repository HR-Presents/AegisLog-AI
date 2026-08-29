# AegisLog AI v1.3.0

AegisLog AI v1.3.0 is the customer-ready terminal release focused on real-time defensive monitoring, investigation, and one-file Windows delivery.

## Customer download

Download only these two files from the release:

- `AegisLog.exe`
- `AegisLog.exe.sha256`

No Python installation, virtual environment, installer, requirements file, or support folder is required to run the Windows executable.

### Start AegisLog

Double-click `AegisLog.exe` to open the terminal control center, or run it from a terminal.

```text
AegisLog.exe
```

The executable remains local-first and read-only. It analyzes telemetry and presents investigation guidance; it does not automatically change accounts, services, firewall rules, privileges, or host configuration.

## Major v1.3 capabilities

- Single-file Windows `AegisLog.exe` delivery.
- Rich terminal analysis dashboard and interactive control center.
- Real-time monitoring for growing log files.
- Multi-source live SOC correlation.
- Native Windows Event Log, Linux journald, and Docker collection.
- Continuous native live monitoring.
- Incident correlation, confidence scoring, timelines, entities, and persistent case history.
- Evidence-based MITRE ATT&CK context.
- Local `Explain This Incident` analyst workflow.
- Rolling failed-login, error, and firewall-block rate intelligence with adaptive baselines and spike detection.
- Watch Mode Profiles: All, Security, Authentication, Web, Docker, and Operations.

## Useful commands

```text
AegisLog.exe dashboard <file>
AegisLog.exe live <file> --profile security
AegisLog.exe live-multi <file1> <file2> --profile authentication
AegisLog.exe native-sources
AegisLog.exe native-analyze windows --channel Security
AegisLog.exe native-analyze journald
AegisLog.exe native-analyze docker --container <name>
AegisLog.exe native-live windows --channel Security --profile security
AegisLog.exe incidents <file>
AegisLog.exe investigate <file> <incident-id>
AegisLog.exe explain <file> <incident-id>
AegisLog.exe mitre <file>
AegisLog.exe case-history
```

## Integrity verification

The release includes `AegisLog.exe.sha256`. Verify the downloaded executable before distribution or use.

PowerShell:

```powershell
Get-FileHash .\AegisLog.exe -Algorithm SHA256
Get-Content .\AegisLog.exe.sha256
```

The hashes must match.

## Security and trust notes

AegisLog treats log-derived text as untrusted terminal content and performs defensive analysis only. MITRE mappings and incident confidence are investigative context, not proof of compromise or attacker attribution.

The Windows executable is built as a PyInstaller one-file console application. Unless a future release is explicitly documented as code-signed, customers should not assume the binary is digitally signed. Windows SmartScreen or antivirus reputation warnings can occur with unsigned one-file executables.

## Release engineering

This release is published only through the explicit `Release v1.3.0` manual workflow. The workflow verifies the exact v1.3.0 version, runs tests and security/package gates, builds and smoke-tests the Windows executable, verifies its SHA-256 checksum, and refuses to reuse or modify an existing `v1.3.0` tag or GitHub release.
