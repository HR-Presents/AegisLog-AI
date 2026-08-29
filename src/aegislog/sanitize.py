from __future__ import annotations

import re

ANSI_ESCAPE = re.compile(r"\x1b(?:\[[0-?]*[ -/]*[@-~]|\][^\x07\x1b]*(?:\x07|\x1b\\)?)")
CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def terminal_safe(text: str) -> str:
    """Remove ANSI/terminal escape sequences and remaining control bytes."""
    return CONTROL.sub("", ANSI_ESCAPE.sub("", text))
