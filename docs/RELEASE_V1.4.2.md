# AegisLog AI v1.4.2

AegisLog AI v1.4.2 is a Windows control-center reliability patch based on real-machine acceptance testing.

## Fixed

- Fixed the interactive **Option 2 — real-time file dashboard** launch path. The control center now passes concrete runtime values to the Typer-backed live command instead of leaving omitted options as Typer metadata objects.
- Applied the same defensive launch pattern to **Option 3 — multi-source live SOC**, **Option 4 — native analysis**, and **Option 5 — native real-time monitor**.
- Added menu-level exception containment so a launch failure is reported inside AegisLog instead of unexpectedly closing the customer control center.
- Added regression coverage for interactive live and multi-source launch defaults and crash containment.

## Included from v1.4.1

- Clear live-monitor startup semantics: default monitoring follows new lines; `--from-start` intentionally includes existing content.
- `Average rate` and live activity state instead of a misleading lifetime event-rate label.
- 60-second rolling rate/baseline context.
- Deduplicated growing live findings such as repeated authentication failures.
- Windows native telemetry normalization, Security Event intelligence, incident IDs, local incident explanation, MITRE context, watch profiles, native collectors, and read-only/local-first analysis.

## Customer delivery

The Windows customer artifact remains a single `AegisLog.exe`. No Python installation or virtual environment is required for the released EXE.

A SHA-256 checksum file is published beside the executable.

## Security model

AegisLog remains defensive, local-first, and read-only. Detection signals are investigative evidence rather than proof of compromise. The application does not automatically change accounts, firewall rules, services, or system configuration.

## Windows note

The executable is currently unsigned. Windows SmartScreen or antivirus products may therefore show reputation-based warnings even when the published SHA-256 checksum matches.
