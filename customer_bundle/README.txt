AEGISLOG AI CUSTOMER BUNDLE
===========================

AegisLog is designed to run locally in one terminal. Customers do not need GitHub access or a global Python package installation.

RECOMMENDED: ONE-FILE START
---------------------------
Windows:
1. Install Python 3.10 or newer if it is not already installed.
2. Double-click START_AEGISLOG.bat.
3. On the first run it installs AegisLog into a private environment inside this folder.
4. The same terminal immediately opens the AegisLog control center.
5. On future runs, double-click the same START_AEGISLOG.bat file. It skips installation and opens AegisLog directly.

Linux / macOS:
1. Install Python 3.10 or newer if required.
2. Run:

   chmod +x START_AEGISLOG.sh
   ./START_AEGISLOG.sh

The same script installs AegisLog on first run and then opens the terminal control center.

TERMINAL CONTROL CENTER
-----------------------
The `aegislog start` control center keeps the customer in one terminal and provides menu options to:
- analyze a log file
- analyze the bundled demo log
- run a system check
- view useful advanced commands
- exit safely

When selecting a log, provide the path to an actual file such as auth.log, syslog, messages, application.log, or a text log export. If a folder is entered by mistake, AegisLog explains the problem and returns to the menu.

ADVANCED / MANUAL COMMANDS
--------------------------
Customers who prefer direct commands can still use:

   aegislog --version
   aegislog doctor
   aegislog dashboard C:\path\to\your\logfile.log
   aegislog analyze C:\path\to\your\logfile.log
   aegislog stream C:\path\to\your\logfile.log

LEGACY LAUNCHERS
----------------
The separate installers and launchers remain included for support and troubleshooting:
- INSTALL_WINDOWS.bat
- OPEN_AEGISLOG_TERMINAL.bat
- RUN_DASHBOARD.bat
- INSTALL_LINUX_MACOS.sh
- OPEN_AEGISLOG_TERMINAL.sh
- RUN_DASHBOARD.sh

WHAT IS INCLUDED
----------------
- START_AEGISLOG.bat / START_AEGISLOG.sh: recommended one-file startup
- package/: AegisLog AI wheel
- vendor/: offline Python dependency wheels
- sample_logs/: bundled demonstration log
- support installers and terminal launchers
- uninstall scripts
- SHA256SUMS for integrity verification

The first run creates a private .aegislog-venv inside this folder. AegisLog does not need to modify system services, firewall rules, user accounts, Docker containers, or other privileged system state.

The terminal dashboard shows analyzed lines, risk state, findings, severity distribution, categories, services, incidents, anomalies, and evidence. Findings are defensive investigative signals, not proof of compromise.
