# AegisLog AI v1.3 User Guide

This guide explains how to run AegisLog AI v1.3.0 from the standalone Windows executable and how to use its main terminal workflows safely and effectively.

## 1. Windows quick start

For normal Windows use, you need only:

```text
AegisLog.exe
```

1. Download `AegisLog.exe` from the v1.3.0 GitHub release.
2. Keep `AegisLog.exe.sha256` if you want to verify the download.
3. Double-click `AegisLog.exe` to open the terminal control center.
4. Choose an action from the menu, or run a command directly from Command Prompt, PowerShell, or Windows Terminal.

The standalone executable does not require Python, a virtual environment, `requirements.txt`, an installer, or a support folder.

> AegisLog v1.3.0 is built as a PyInstaller one-file console executable. Unless a release explicitly documents code signing, do not assume the EXE is digitally signed. Windows SmartScreen or antivirus reputation warnings can occur with unsigned one-file executables.

## 2. Opening AegisLog

### Interactive control center

Double-click the EXE or run:

```text
AegisLog.exe
```

You can also explicitly open the control center with:

```text
AegisLog.exe start
```

The control center is the easiest starting point for file analysis, live monitoring, native telemetry, incident explanation, system checks, and command help.

### Command help

Use Typer's built-in help whenever you are unsure about a command or its options:

```text
AegisLog.exe --help
AegisLog.exe live --help
AegisLog.exe native-live --help
AegisLog.exe investigate --help
```

## 3. Analyze a saved log file

For a fast analysis:

```text
AegisLog.exe analyze C:\logs\auth.log
```

For the richer terminal dashboard:

```text
AegisLog.exe dashboard C:\logs\auth.log
```

The dashboard summarizes risk, severity, categories, parsed log levels, services, incidents, anomalies, findings, evidence, and investigation recommendations.

If a path contains spaces, quote it:

```text
AegisLog.exe dashboard "C:\Security Logs\auth.log"
```

## 4. Live monitoring of a growing file

Use `live` when another service is continuously appending lines to a log file:

```text
AegisLog.exe live C:\logs\server.log
```

AegisLog maintains a bounded rolling view and updates the terminal with event rate, findings, incidents, anomalies, risk, recent detections, and adaptive rate/baseline intelligence.

Use a Watch Mode Profile to focus the display:

```text
AegisLog.exe live C:\logs\auth.log --profile security
AegisLog.exe live C:\logs\auth.log --profile authentication
AegisLog.exe live C:\logs\nginx.log --profile web
```

Stop live monitoring with `Ctrl+C`.

## 5. Multi-source live SOC view

Use `live-multi` to monitor multiple growing files together:

```text
AegisLog.exe live-multi C:\logs\auth.log C:\logs\nginx.log C:\logs\application.log
```

You can focus the unified view:

```text
AegisLog.exe live-multi C:\logs\auth.log C:\logs\web.log --profile security
AegisLog.exe live-multi C:\logs\auth.log C:\logs\web.log --profile authentication
AegisLog.exe live-multi C:\logs\nginx.log C:\logs\application.log --profile web
```

The multi-source view keeps source attribution while combining defensive findings, incidents, alerts, event rates, and trend signals.

## 6. Watch Mode Profiles

Profiles change what the live terminal emphasizes. They do not turn AegisLog into an active remediation tool and do not change its read-only defensive model.

| Profile | Best for |
| --- | --- |
| `all` | Complete live defensive view |
| `security` | Broad security activity, authentication, attack, firewall, privilege, and suspicious web signals |
| `authentication` | Login failures, account activity, credentials, SSH and PAM-related activity |
| `web` | HTTP activity, probes, suspicious paths, traversal, SQL injection-style signals, `.env` and `/etc/passwd` probing |
| `docker` | Docker, containers, container services, and related operational/security telemetry |
| `operations` | Errors, failures, timeouts, service health, OOM, database, and systemd-style operational signals |

Direct CLI commands default to `all` unless a profile is supplied. The interactive control center may suggest a more focused profile such as `security`.

## 7. Native telemetry

AegisLog can collect supported telemetry directly instead of requiring you to export it first.

Check what is available:

```text
AegisLog.exe native-sources
```

### Windows Event Logs

Analyze a snapshot of the Windows Security channel:

```text
AegisLog.exe native-analyze windows --channel Security
```

Other supported allowlisted Windows channels include System and Application:

```text
AegisLog.exe native-analyze windows --channel System
AegisLog.exe native-analyze windows --channel Application
```

Continuously monitor Windows Security telemetry:

```text
AegisLog.exe native-live windows --channel Security --profile security
```

### Linux journald

Snapshot analysis:

```text
AegisLog.exe native-analyze journald
```

Continuous monitoring:

```text
AegisLog.exe native-live journald --profile operations
```

This requires `journalctl` and sufficient permission to read the requested journal data.

### Docker

Snapshot analysis for a container:

```text
AegisLog.exe native-analyze docker --container api
```

Continuous monitoring:

```text
AegisLog.exe native-live docker --container api --profile docker
```

Docker must be installed/running and the current user must have permission to access the requested container logs.

### Native live options

Useful `native-live` controls include:

```text
--profile <profile>
--refresh <seconds>
--window <seconds>
--limit <count>
--from-start
```

Run this for the exact options supported by your build:

```text
AegisLog.exe native-live --help
```

## 8. Incident investigation

List incidents detected in a log:

```text
AegisLog.exe incidents C:\logs\auth.log
```

Copy the incident ID shown in the table, then inspect it:

```text
AegisLog.exe investigate C:\logs\auth.log INC-XXXXXXXX
```

AegisLog builds evidence-led incident context including severity, confidence, category, timeline, findings, and extracted entities.

Incident IDs are deterministic for the evidence currently available, but an ID can change if the underlying evidence/entity set changes.

## 9. Explain This Incident

Use the same incident ID:

```text
AegisLog.exe explain C:\logs\auth.log INC-XXXXXXXX
```

`explain` produces a local deterministic analyst explanation containing:

- a plain-language summary;
- why the activity matters;
- the evidence AegisLog observed;
- evidence-consistent MITRE ATT&CK context where available;
- safe investigation steps; and
- an uncertainty caveat.

The local `explain` workflow does not send the log content to an external AI service.

## 10. MITRE ATT&CK context

Show evidence-consistent ATT&CK mappings for incidents in a file:

```text
AegisLog.exe mitre C:\logs\auth.log
```

Mappings are investigation context, not proof that an attacker executed a particular technique. AegisLog maps only when local evidence is consistent with a supported technique.

Examples include brute-force authentication activity, password spraying, credential stuffing, account discovery, suspicious public-facing web probing, command/scripting signals, scheduled jobs, service creation, privilege-elevation context, and network/firewall discovery signals.

## 11. Entity intelligence

Extract and summarize incident entities:

```text
AegisLog.exe intel-entities C:\logs\auth.log
```

Additional entity-oriented commands available in the CLI include:

```text
AegisLog.exe entities <file>
AegisLog.exe index-entities <file>
AegisLog.exe entity <value>
AegisLog.exe entity-top
```

Use `--help` on each command for its exact arguments and options.

## 12. Save and review investigations

Save an incident to the local investigation case store:

```text
AegisLog.exe save-investigation C:\logs\auth.log INC-XXXXXXXX
```

List saved cases:

```text
AegisLog.exe case-history
```

Open a saved case:

```text
AegisLog.exe case-show INC-XXXXXXXX
```

The case store keeps local investigation history such as first/last recorded time, severity, confidence, category, entities, findings, timeline data, and observation count.

## 13. Large-file streaming

For large logs, use the streaming command rather than relying only on whole-file workflows:

```text
AegisLog.exe stream C:\logs\huge-server.log --chunk-size 2000
```

This is intended to keep processing memory bounded by analyzing chunks.

## 14. Behavioral comparison

Compare a current log with one or more baseline logs:

```text
AegisLog.exe behavior --baseline monday.log --baseline tuesday.log --current today.log
```

This helps identify behavioral differences between normal/reference telemetry and the current dataset.

## 15. Reports and additional commands

AegisLog's underlying CLI also includes analysis/reporting, anomaly, threat, hunting, baseline, indicator, and related defensive workflows depending on the installed build.

Always use the executable's own help as the authoritative command reference:

```text
AegisLog.exe --help
AegisLog.exe <command> --help
```

For example:

```text
AegisLog.exe report auth.log --output report.json
AegisLog.exe hunt --severity HIGH
```

## 16. Recommended analyst workflow

A practical workflow for a suspicious authentication log is:

```text
AegisLog.exe dashboard C:\logs\auth.log
AegisLog.exe incidents C:\logs\auth.log
AegisLog.exe investigate C:\logs\auth.log INC-XXXXXXXX
AegisLog.exe explain C:\logs\auth.log INC-XXXXXXXX
AegisLog.exe mitre C:\logs\auth.log
AegisLog.exe save-investigation C:\logs\auth.log INC-XXXXXXXX
AegisLog.exe case-history
```

For a live Windows security-monitoring session:

```text
AegisLog.exe native-sources
AegisLog.exe native-live windows --channel Security --profile security
```

For a small file-based SOC view:

```text
AegisLog.exe live-multi C:\logs\auth.log C:\logs\nginx.log C:\logs\application.log --profile security
```

## 17. Verify the downloaded EXE

The official release includes `AegisLog.exe.sha256`.

In PowerShell:

```powershell
Get-FileHash .\AegisLog.exe -Algorithm SHA256
Get-Content .\AegisLog.exe.sha256
```

The hash printed by `Get-FileHash` must match the hash stored in the checksum file.

For the official v1.3.0 release, the published `AegisLog.exe` SHA-256 is:

```text
8763b843faa32e5848a4fe116dedb1e3316accbc55dd70f6fdae4601fe1b572a
```

## 18. Troubleshooting

### Double-click opens and closes immediately

Open Command Prompt, PowerShell, or Windows Terminal in the folder containing the EXE and run:

```text
AegisLog.exe
```

You will then be able to read any error message instead of losing the terminal window.

### File not found

Use the full path and quote paths containing spaces:

```text
AegisLog.exe dashboard "C:\Users\YourName\Desktop\Security Logs\auth.log"
```

### Windows blocks or warns about the EXE

The v1.3.0 one-file executable should not be assumed to be digitally signed. SmartScreen or antivirus reputation systems can therefore show warnings. Verify that you downloaded the file from the official release and compare its SHA-256 before deciding whether to run it.

### Windows Security channel cannot be read

Your Windows account may not have sufficient access to the requested event channel. Run `native-sources` first and use an account/environment that is authorized to read the telemetry. Do not weaken system security merely to make collection work.

### journald does not work

Confirm `journalctl` is installed and that your current account has permission to read the journal.

### Docker collection does not work

Confirm Docker is installed and running, the container name is correct, and your account is authorized to read Docker logs.

### Live dashboard shows little activity

`live` follows newly appended content. If the file is not changing, there may be nothing new to display. Use `dashboard` for a static existing file or the appropriate native snapshot command.

### Need exact syntax

Run:

```text
AegisLog.exe <command> --help
```

## 19. Security model

AegisLog is defensive, local-first, and read-only by design. It analyzes telemetry and presents investigation guidance. It does not exploit hosts or automatically modify accounts, privileges, services, firewall rules, or system configuration.

Treat findings, anomaly scores, confidence values, correlations, behavioral deltas, and MITRE ATT&CK mappings as investigative signals rather than proof of compromise or attacker attribution.

Log-derived terminal values are untrusted input. AegisLog's terminal rendering is designed to avoid interpreting log content as terminal markup.

## 20. Source/developer installation

The standalone Windows customer workflow does not require Python. Developers who intentionally run AegisLog from source can use Python 3.10+:

```bash
git clone https://github.com/HR-Presents/AegisLog-AI.git
cd AegisLog-AI
python -m venv .venv
```

Activate the environment, then:

```bash
pip install -e '.[dev]'
aegislog doctor
aegislog --help
pytest
ruff check .
bandit -q -r src
```

For customers using the official Windows release, prefer the simpler `AegisLog.exe` workflow described at the beginning of this guide.
