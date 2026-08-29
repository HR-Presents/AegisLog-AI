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
    goto :fail
  )
  set "PY=python"
)

if not exist ".aegislog-venv\Scripts\python.exe" (
  echo Creating private AegisLog environment...
  %PY% -m venv .aegislog-venv
  if errorlevel 1 goto :fail
)

set "VPY=%CD%\.aegislog-venv\Scripts\python.exe"
set "WHEEL="
for %%F in ("%CD%\package\aegislog_ai-*.whl") do set "WHEEL=%%~fF"
if not defined WHEEL (
  echo ERROR: AegisLog package wheel is missing from the package folder.
  goto :fail
)

echo Installing AegisLog AI and bundled dependencies offline...
"%VPY%" -m pip install --disable-pip-version-check --no-index --find-links "%CD%\vendor" "%WHEEL%"
if errorlevel 1 goto :fail

"%VPY%" -m aegislog --version
if errorlevel 1 goto :fail

echo.
echo Installation complete.
echo Double-click OPEN_AEGISLOG_TERMINAL.bat to start AegisLog.
echo.
if /I not "%AEGISLOG_NONINTERACTIVE%"=="1" pause
exit /b 0

:fail
echo.
echo Installation failed. Review the error shown above.
if /I not "%AEGISLOG_NONINTERACTIVE%"=="1" pause
exit /b 1
