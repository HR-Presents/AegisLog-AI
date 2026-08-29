@echo off
cd /d "%~dp0"
if not exist ".aegislog-venv\Scripts\aegislog.exe" (
  echo AegisLog AI is not installed in this folder.
  echo Run INSTALL_WINDOWS.bat first.
  pause
  exit /b 1
)
set "PATH=%CD%\.aegislog-venv\Scripts;%PATH%"
title AegisLog AI Terminal
cls
echo ========================================
echo             AEGISLOG AI
echo      Defensive Log Intelligence
echo ========================================
echo.
aegislog --version
echo.
echo Ready. Examples:
echo   aegislog dashboard C:\path\to\auth.log
echo   aegislog analyze C:\path\to\server.log
echo   aegislog doctor
echo.
cmd /k
