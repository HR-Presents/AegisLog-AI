# Installation

## Windows standalone executable

The recommended Windows installation is the one-file console application:

1. Open the [v1.6.0 GitHub release](https://github.com/HR-Presents/AegisLog-AI/releases/tag/v1.6.0).
2. Download `AegisLog.exe`.
3. Optionally download `AegisLog.exe.sha256` and verify the executable before running it.
4. Run `AegisLog.exe` to open Mission Control.

No Python installation or support directory is required. Unless the release notes explicitly say otherwise, do not assume the executable is digitally signed; Windows SmartScreen or antivirus reputation warnings can occur for unsigned PyInstaller applications.

PowerShell checksum verification:

```powershell
Get-FileHash .\AegisLog.exe -Algorithm SHA256
Get-Content .\AegisLog.exe.sha256
```

Compare the two SHA-256 values exactly. Always use the checksum published beside the same release asset you downloaded. See [v1.6.0 release notes](RELEASE_V1.6.0.md) for stable-release details.

## Python source installation

AegisLog requires Python 3.10 or newer when installed from source.

### Recommended: pipx

```bash
git clone https://github.com/HR-Presents/AegisLog-AI.git
cd AegisLog-AI
pipx install .
aegislog doctor
```

### Development installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest
```

On Windows PowerShell activate with `.venv\Scripts\Activate.ps1`.

The repository also includes `install.sh` and `install.ps1` helpers for source checkouts.

## Optional AI providers

Core analysis does not require an AI provider. The current `main` branch exposes optional AI Analyst support through Mission Control and `aegislog ai-analyst FILE`.

- Local mode requires no model or network access.
- Ollama uses a local provider endpoint.
- OpenAI-compatible remote AI requires explicit opt-in before any provider request.

See [AI Providers](AI_PROVIDERS.md) and [Remote AI](REMOTE_AI.md) for setup and privacy boundaries.
