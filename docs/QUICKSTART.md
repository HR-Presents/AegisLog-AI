# Quickstart

```bash
git clone https://github.com/HR-Presents/AegisLog-AI.git
cd AegisLog-AI
python -m venv .venv
source .venv/bin/activate
pip install -e .
aegislog doctor
aegislog analyze examples/auth.log
aegislog incidents examples/auth.log
```

Windows PowerShell users can activate with `.venv\Scripts\Activate.ps1`.
