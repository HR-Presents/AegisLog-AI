AEGISLOG AI CUSTOMER BUNDLE
===========================

This folder is designed for customers who should not need GitHub access or a global Python package installation.

WINDOWS
-------
1. Install Python 3.10 or newer if it is not already installed.
2. Double-click INSTALL_WINDOWS.bat.
3. Double-click OPEN_AEGISLOG_TERMINAL.bat.
4. Run one of these commands:

   aegislog --version
   aegislog doctor
   aegislog dashboard C:\path\to\your\logfile.log
   aegislog analyze C:\path\to\your\logfile.log

LINUX / macOS
-------------
1. Install Python 3.10 or newer if required.
2. In Terminal, run:

   chmod +x INSTALL_LINUX_MACOS.sh OPEN_AEGISLOG_TERMINAL.sh RUN_DASHBOARD.sh UNINSTALL_LINUX_MACOS.sh
   ./INSTALL_LINUX_MACOS.sh
   ./OPEN_AEGISLOG_TERMINAL.sh

3. Then run:

   aegislog dashboard /path/to/logfile.log

WHAT IS INCLUDED
----------------
- package/: AegisLog AI wheel
- vendor/: offline Python dependency wheels
- INSTALL_WINDOWS.bat and INSTALL_LINUX_MACOS.sh
- ready-to-use terminal launchers
- dashboard launchers
- uninstall scripts
- SHA256SUMS for integrity verification

The installer creates a private .aegislog-venv inside this folder. It does not need to modify system services, firewall rules, user accounts, Docker containers, or other privileged system state.

The terminal dashboard shows analyzed lines, risk state, findings, severity distribution, categories, services, incidents, anomalies, and evidence. Findings are defensive investigative signals, not proof of compromise.
