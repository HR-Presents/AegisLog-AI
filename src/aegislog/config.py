from __future__ import annotations

import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "aegislog"
CONFIG_FILE = CONFIG_DIR / "config.json"
DEFAULTS = {"ai_provider": "none", "model": "", "redact": True, "max_ai_events": 80}


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return DEFAULTS.copy()
    try:
        data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return DEFAULTS.copy()
    return {**DEFAULTS, **data}


def save_config(data: dict) -> Path:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps({**DEFAULTS, **data}, indent=2), encoding="utf-8")
    return CONFIG_FILE
