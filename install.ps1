$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$HasPy = Get-Command py -ErrorAction SilentlyContinue
$HasPython = Get-Command python -ErrorAction SilentlyContinue
if (-not $HasPy -and -not $HasPython) {
    throw "Python 3.10 or newer is required. Install Python and run this installer again."
}

$Venv = Join-Path $PSScriptRoot ".aegislog-venv"
if (-not (Test-Path $Venv)) {
    if ($HasPy) {
        & py -3 -m venv $Venv
    } else {
        & python -m venv $Venv
    }
}

$VenvPython = Join-Path $Venv "Scripts\python.exe"
& $VenvPython -m pip install --upgrade pip
& $VenvPython -m pip install .

$Launcher = Join-Path $PSScriptRoot "aegislog.cmd"
@"
@echo off
setlocal
"$VenvPython" -m aegislog %*
"@ | Set-Content -Encoding ASCII $Launcher

$Shell = Join-Path $PSScriptRoot "OPEN_AEGISLOG_TERMINAL.bat"
@"
@echo off
title AegisLog AI
cd /d "%~dp0"
echo AegisLog AI terminal is ready.
echo.
echo Examples:
echo   aegislog analyze path\to\auth.log
echo   aegislog dashboard path\to\auth.log
echo   aegislog doctor
echo.
cmd /k "set PATH=%~dp0;%PATH%"
"@ | Set-Content -Encoding ASCII $Shell

Write-Host ""
Write-Host "AegisLog AI installed successfully." -ForegroundColor Green
Write-Host "Run .\aegislog.cmd --version"
Write-Host "Or double-click OPEN_AEGISLOG_TERMINAL.bat to open a ready terminal."
