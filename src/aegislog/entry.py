from __future__ import annotations

from .cli import app
from .commands_v07 import behavior, entities, stream
from .commands_v08 import entity, entity_top, index_entities

app.command("stream")(stream)
app.command("entities")(entities)
app.command("behavior")(behavior)
app.command("index-entities")(index_entities)
app.command("entity")(entity)
app.command("entity-top")(entity_top)

__all__ = ["app"]
