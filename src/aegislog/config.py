from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "aegislog"
CONFIG_FILE = CONFIG_DIR / "config.json"
CONFIG_SCHEMA_VERSION = 1
DEFAULTS = {
    "schema_version": CONFIG_SCHEMA_VERSION,
    "ai_provider": "none",
    "model": "",
    "base_url": None,
    "redact": True,
    "max_ai_events": 80,
}


def config_dir() -> Path:
    """Return the AegisLog state/config directory, creating it when needed."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if os.name != "nt":
        CONFIG_DIR.chmod(0o700)
    return CONFIG_DIR


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return DEFAULTS.copy()
    try:
        data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return DEFAULTS.copy()
    if not isinstance(data, dict):
        return DEFAULTS.copy()
    version = data.get("schema_version", 0)
    if not isinstance(version, int) or version > CONFIG_SCHEMA_VERSION:
        return DEFAULTS.copy()
    allowed = DEFAULTS.keys()
    return {**DEFAULTS, **{key: data[key] for key in allowed if key in data}, "schema_version": CONFIG_SCHEMA_VERSION}


def save_config(data: dict) -> Path:
    root = config_dir()
    payload = {**DEFAULTS, **{key: value for key, value in data.items() if key in DEFAULTS}}
    payload["schema_version"] = CONFIG_SCHEMA_VERSION
    fd, temporary = tempfile.mkstemp(prefix=".config-", suffix=".json", dir=root)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
            handle.write("\n")
        if os.name != "nt":
            os.chmod(temporary, 0o600)
        os.replace(temporary, CONFIG_FILE)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return CONFIG_FILE
