from __future__ import annotations

from .cli import app
from .commands import register_commands, start
from .console_pages import system_check


def _remove_ai_surface() -> None:
    """Remove legacy AI/provider commands from the public executable surface."""
    retained = []
    for command in app.registered_commands:
        callback = getattr(command, "callback", None)
        callback_name = getattr(callback, "__name__", "")
        if callback_name in {"ask_log", "config", "doctor"}:
            continue
        retained.append(command)
    app.registered_commands = retained


_remove_ai_surface()
register_commands(app)
app.command("doctor")(system_check)

__all__ = ["app", "start"]
