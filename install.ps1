$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$Python = Get-Command py -ErrorAction SilentlyContinue
if ($Python) {
    $Py = @("py", "-3")
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $Py = @("python")
} else {
    throw "Python 3.10 or newer is required. Install Python and run this installer again."
}

$Venv = Join-Path $PSScriptRoot ".aegislog-venv"
if (-not (Test-Path $Venv)) {
    & $Py[0] $Py[1..($Py.Count-1)] -m venv $Venv
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
