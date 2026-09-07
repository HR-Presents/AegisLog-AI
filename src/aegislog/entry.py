from __future__ import annotations

from .cli import app
from .commands import register_commands

register_commands(app)

__all__ = ["app"]
