from __future__ import annotations

import re

CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]|\x1b\[[0-?]*[ -/]*[@-~]")


def terminal_safe(text: str) -> str:
    """Remove terminal control/ANSI sequences from untrusted log text."""
    return CONTROL.sub("", text)
