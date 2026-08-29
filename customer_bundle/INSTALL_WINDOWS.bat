@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo       AegisLog AI Customer Installer
echo ========================================
echo.

where py >nul 2>nul
if %errorlevel%==0 (
  set "PY=py -3"
) else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo ERROR: Python 3.10 or newer is required.
    echo Install Python, then run this installer again.
    pause
    exit /b 1
  )
  set "PY=python"
)

if not exist ".aegislog-venv\Scripts\python.exe" (
  echo Creating private AegisLog environment...
  %PY% -m venv .aegislog-venv
  if errorlevel 1 goto :fail
)

set "VPY=%CD%\.aegislog-venv\Scripts\python.exe"

echo Installing AegisLog AI and bundled dependencies offline...
"%VPY%" -m pip install --disable-pip-version-check --no-index --find-links "%CD%\vendor" "%CD%\package\aegislog_ai-*.whl"
if errorlevel 1 goto :fail

"%VPY%" -m aegislog --version
if errorlevel 1 goto :fail

echo.
echo Installation complete.
echo Double-click OPEN_AEGISLOG_TERMINAL.bat to start AegisLog.
echo.
pause
exit /b 0

:fail
echo.
echo Installation failed. Review the error shown above.
pause
exit /b 1
