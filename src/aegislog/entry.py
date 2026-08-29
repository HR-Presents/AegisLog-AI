from __future__ import annotations

from .cli import app
from .commands_v07 import behavior, entities, stream

app.command("stream")(stream)
app.command("entities")(entities)
app.command("behavior")(behavior)

__all__ = ["app"]
