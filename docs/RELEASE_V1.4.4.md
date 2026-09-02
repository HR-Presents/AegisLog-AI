# AegisLog AI v1.4.4

AegisLog AI v1.4.4 is a focused Windows terminal runtime reliability update built on v1.4.3.

## Fixed

- Fixed the interactive control center return flow so pressing Enter after an analysis returns cleanly to a freshly redrawn main menu.
- Removed the confusing empty-default `()` prompt from the menu pause.
- Fixed interactive real-time file monitoring so it analyzes the selected file's current contents before following new lines, instead of appearing idle on existing logs.
- Fixed interactive native live monitoring so it loads the current native source snapshot before following new events.
- Updated interactive multi-source monitoring to include current source contents when launched from the control center.
- Improved Ctrl+C handling so live monitors stop safely and return control to AegisLog instead of feeling like the application has crashed or become trapped.
- Disabled alternate-screen live rendering for the affected file and native dashboards to avoid blank/stuck behavior in Windows console hosts and the packaged executable.
- Forced visible live refreshes even when no new events arrive so the monitor remains visibly responsive.

## Quality

- Added regression tests covering the hardened terminal runtime behavior.
- Verified the fix through CI, security checks, package builds, and the Windows single-executable workflow before release preparation.

## Customer delivery

The Windows release is a single `AegisLog.exe` console executable. No Python installation or virtual environment is required for the released EXE.

A matching `AegisLog.exe.sha256` checksum is published beside the executable.

## Security model

AegisLog remains defensive, local-first, and read-only. Findings and correlations are investigative signals rather than proof of compromise. The application does not automatically change accounts, firewall rules, services, or system configuration.

## Windows note

The executable is currently unsigned. Windows SmartScreen or antivirus products may show reputation-based warnings even when the published SHA-256 checksum matches.
