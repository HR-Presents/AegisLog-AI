@echo off
setlocal
cd /d "%~dp0"
title AegisLog AI

cls
echo ========================================
echo             AegisLog AI
echo      One-File Customer Launcher
echo ========================================
echo.

where py >nul 2>nul
if %errorlevel%==0 (
  set "PY=py -3"
) else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo ERROR: Python 3.10 or newer is required.
    echo Install Python and run START_AEGISLOG.bat again.
    goto :fail
  )
  set "PY=python"
)

if not exist ".aegislog-venv\Scripts\python.exe" (
  echo First run detected. Installing AegisLog AI locally...
  echo.
  %PY% -m venv .aegislog-venv
  if errorlevel 1 goto :fail

  set "VPY=%CD%\.aegislog-venv\Scripts\python.exe"
  set "WHEEL="
  for %%F in ("%CD%\package\aegislog_ai-*.whl") do set "WHEEL=%%~fF"
  if not defined WHEEL (
    echo ERROR: AegisLog package wheel is missing.
    goto :fail
  )

  "%CD%\.aegislog-venv\Scripts\python.exe" -m pip install --disable-pip-version-check --no-index --find-links "%CD%\vendor" "%WHEEL%"
  if errorlevel 1 goto :fail
  echo.
  echo Installation complete.
  echo Starting AegisLog in this terminal...
  timeout /t 1 /nobreak >nul
)

set "PATH=%CD%\.aegislog-venv\Scripts;%PATH%"
"%CD%\.aegislog-venv\Scripts\aegislog.exe" start
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" goto :fail
exit /b 0

:fail
echo.
echo AegisLog could not start. Review the message above.
pause
exit /b 1
