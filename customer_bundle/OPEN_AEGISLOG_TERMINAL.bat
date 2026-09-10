@echo off
cd /d "%~dp0"
if not exist ".aegislog-venv\Scripts\aegislog.exe" (
  echo AegisLog is not installed in this folder.
  echo Run INSTALL_WINDOWS.bat first.
  pause
  exit /b 1
)
set "PATH=%CD%\.aegislog-venv\Scripts;%PATH%"
title AegisLog Terminal
cls
echo ========================================
echo               AEGISLOG
echo      Defensive Log Investigation
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
