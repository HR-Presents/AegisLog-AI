$ErrorActionPreference = "Stop"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python 3.10+ is required."
}

if (Get-Command pipx -ErrorAction SilentlyContinue) {
    pipx install . --force
} else {
    python -m pip install --user .
}

Write-Host "AegisLog AI installed. Run: aegislog doctor"
