from __future__ import annotations

from .cli import app
from .commands_v07 import behavior, entities, stream
from .commands_v08 import entity, entity_top, index_entities
from .commands_v11 import dashboard, replace_analyze_command
from .commands_v12 import start
from .commands_v13 import live_dashboard
from .commands_v14 import live_multi
from .commands_v15 import incidents, intel_entities, investigate

replace_analyze_command(app)
app.command("start")(start)
app.command("dashboard")(dashboard)
app.command("live")(live_dashboard)
app.command("live-multi")(live_multi)
app.command("incidents")(incidents)
app.command("investigate")(investigate)
app.command("intel-entities")(intel_entities)
app.command("stream")(stream)
app.command("entities")(entities)
app.command("behavior")(behavior)
app.command("index-entities")(index_entities)
app.command("entity")(entity)
app.command("entity-top")(entity_top)

__all__ = ["app"]
