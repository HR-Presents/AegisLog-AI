# Installation

## Windows standalone executable

The recommended Windows installation is the one-file console application:

1. Open the [latest GitHub release](https://github.com/HR-Presents/AegisLog-AI/releases/latest).
2. Download `AegisLog.exe`.
3. Optionally download `AegisLog.exe.sha256` and verify the executable before running it.
4. Run `AegisLog.exe` to open the terminal control center.

No Python installation or support directory is required. Unless the release notes explicitly say otherwise, do not assume the executable is digitally signed; Windows SmartScreen or antivirus reputation warnings can occur for unsigned PyInstaller applications.

PowerShell checksum verification:

```powershell
Get-FileHash .\AegisLog.exe -Algorithm SHA256
Get-Content .\AegisLog.exe.sha256
```

Compare the two SHA-256 values exactly before running the executable. See the [v1.4.2 release notes](RELEASE_V1.4.2.md) for release-specific details.

## Python source installation

AegisLog AI requires Python 3.10 or newer when installed from source.

## Recommended: pipx

```bash
git clone https://github.com/HR-Presents/AegisLog-AI.git
cd AegisLog-AI
pipx install .
aegislog doctor
```

## Development installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest
```

On Windows PowerShell activate with `.venv\Scripts\Activate.ps1`.

The repository also includes `install.sh` and `install.ps1` helpers for source checkouts.
