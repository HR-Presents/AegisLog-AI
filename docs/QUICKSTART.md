# Quickstart

## Windows

Download `AegisLog.exe` from the published [v1.6.0 release](https://github.com/HR-Presents/AegisLog-AI/releases/tag/v1.6.0) and run:

```text
AegisLog.exe
```

Mission Control is the easiest entry point for static analysis, live monitoring, incident intelligence, optional AI Analyst, system health, and command help.

## Source installation

```bash
git clone https://github.com/HR-Presents/AegisLog-AI.git
cd AegisLog-AI
python -m venv .venv
source .venv/bin/activate
pip install -e .
aegislog doctor
aegislog dashboard examples/auth.log
aegislog incidents examples/auth.log
```

Windows PowerShell users can activate with `.venv\Scripts\Activate.ps1`.

## Optional AI Analyst

Core detection does not require an AI provider. On current `main`, use:

```text
aegislog ai-analyst examples/auth.log --provider local
```

Mission Control exposes the same workflow as `A — AI ANALYST`. Ollama stays local; OpenAI-compatible remote AI requires explicit opt-in. See [AI Providers](AI_PROVIDERS.md).
