# Installation

AegisLog AI requires Python 3.10 or newer.

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

The repository also includes `install.sh` and `install.ps1` helpers for source checkouts. A future stable release can publish signed/tagged packages so users do not need to clone the repository first.
