# AegisLog AI v1.4.0

AegisLog AI v1.4.0 focuses on stronger real-Windows telemetry, clearer investigation workflows, and useful Windows Security Event intelligence while preserving the local-first, read-only defensive model.

## Highlights

- Improved Windows Event Log timestamp, provider, level, and service normalization.
- Friendly permission guidance when the protected Windows Security Event Log cannot be read.
- Docker readiness now distinguishes missing CLI, unavailable engine/access, and ready state.
- Correlated incidents display actionable `INC-XXXXXXXX` identifiers directly in the dashboard.
- Correct investigation workflow using `incidents`, `investigate`, and `explain` commands.
- Dedicated Windows Security Event parsing and defensive context for important audit events.
- Repeated Windows Event ID 4625 failed logons can feed the brute-force correlation model by source IP.
- Defensive signals for audit-log clearing, account creation, account lockout, privileged logon, process creation, and security-group membership changes.
- Regression coverage based on real Windows acceptance-test findings.

## Windows Security Event context

v1.4.0 recognizes selected Security Auditing event IDs including 4625, 4672, 4688, 4720, 4728, 4732, 4740, and 1102. These mappings provide investigation context only. A mapped event is evidence to review, not proof that a host or account is compromised.

## Customer download

Windows customers need only:

- `AegisLog.exe`
- `AegisLog.exe.sha256` (optional checksum verification)

No Python installation, virtual environment, requirements file, installer, or support folder is required. Double-click `AegisLog.exe` to open the terminal control center, or run commands directly from a terminal.

## Safety model

AegisLog remains defensive and read-only. Native collectors read telemetry and do not change accounts, firewall rules, services, registry settings, privileges, or system configuration. External AI is used only when explicitly configured and supported data is redacted before transmission.

## Windows notice

The Windows executable is not digitally signed. Windows SmartScreen or antivirus products may therefore show a warning, especially for a newly published build. Verify the SHA-256 checksum when desired.
