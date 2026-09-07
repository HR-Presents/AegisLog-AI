from __future__ import annotations

from .cli import app
from .commands import register_commands, start

register_commands(app)

__all__ = ["app", "start"]
