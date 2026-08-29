@echo off
setlocal
cd /d "%~dp0"
if not exist ".aegislog-venv\Scripts\aegislog.exe" (
  echo AegisLog AI is not installed. Run INSTALL_WINDOWS.bat first.
  pause
  exit /b 1
)
set /p "LOGFILE=Enter full path to the log file: "
if "%LOGFILE%"=="" exit /b 1
"%CD%\.aegislog-venv\Scripts\aegislog.exe" dashboard "%LOGFILE%"
echo.
pause
