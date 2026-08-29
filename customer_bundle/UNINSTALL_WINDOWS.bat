@echo off
setlocal
cd /d "%~dp0"
echo This removes only the private AegisLog environment in this customer folder.
echo It does not remove reports or logs you created elsewhere.
set /p "CONFIRM=Type YES to continue: "
if /I not "%CONFIRM%"=="YES" exit /b 1
if exist ".aegislog-venv" rmdir /s /q ".aegislog-venv"
echo AegisLog AI local environment removed.
pause
