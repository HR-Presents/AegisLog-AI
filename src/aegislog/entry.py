from __future__ import annotations

from .cli import app
from .commands_v07 import behavior, entities, stream
from .commands_v08 import entity, entity_top, index_entities
from .commands_v11 import dashboard, replace_analyze_command
from .commands_v12 import start
from .commands_v13 import live_dashboard
from .commands_v14 import live_multi
from .commands_v15 import incidents, intel_entities, investigate
from .commands_v16 import case_history, case_show, save_investigation
from .commands_v17 import native_analyze, native_sources
from .commands_v18 import native_live

replace_analyze_command(app)
app.command("start")(start)
app.command("dashboard")(dashboard)
app.command("live")(live_dashboard)
app.command("live-multi")(live_multi)
app.command("native-sources")(native_sources)
app.command("native-analyze")(native_analyze)
app.command("native-live")(native_live)
app.command("incidents")(incidents)
app.command("investigate")(investigate)
app.command("intel-entities")(intel_entities)
app.command("save-investigation")(save_investigation)
app.command("case-history")(case_history)
app.command("case-show")(case_show)
app.command("stream")(stream)
app.command("entities")(entities)
app.command("behavior")(behavior)
app.command("index-entities")(index_entities)
app.command("entity")(entity)
app.command("entity-top")(entity_top)

__all__ = ["app"]
