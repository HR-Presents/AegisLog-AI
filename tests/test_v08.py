from pathlib import Path

from aegislog.correlation import EntityLink
from aegislog.database import add_incidents, list_incidents
from aegislog.entity_store import find_entity, replace_incident_entities, top_entities
from aegislog.incidents import Incident
from aegislog.live import RollingAnalyzer


def test_entity_graph_roundtrip(tmp_path: Path):
    db = tmp_path / "graph.db"
    incident = Incident(id="INC-X", category="authentication", severity="HIGH", count=4, title="Repeated auth failures", evidence=("failed from 203.0.113.7",))
    add_incidents("auth.log", "2026-08-29T00:00:00+00:00", [incident], db)
    row_id = list_incidents(path=db)[0]["id"]
    entities = [EntityLink("ip", "203.0.113.7", 4, ("authentication",), ("HIGH",), 10)]
    assert replace_incident_entities(row_id, entities, db) == 1
    matches = find_entity("ip", "203.0.113.7", path=db)
    assert matches[0]["incident_id"] == row_id
    assert matches[0]["title"] == "Repeated auth failures"
    ranked = top_entities(path=db)
    assert ranked[0]["entity_value"] == "203.0.113.7"
    assert ranked[0]["incident_count"] == 1


def test_entity_graph_replace_is_idempotent(tmp_path: Path):
    db = tmp_path / "graph.db"
    incident = Incident(id="INC-X", category="authentication", severity="HIGH", count=2, title="Auth", evidence=("x",))
    add_incidents("auth.log", "2026-08-29T00:00:00+00:00", [incident], db)
    row_id = list_incidents(path=db)[0]["id"]
    entity = EntityLink("user", "admin", 2, ("authentication",), ("HIGH",), 8)
    replace_incident_entities(row_id, [entity], db)
    replace_incident_entities(row_id, [entity], db)
    assert len(find_entity("user", "admin", path=db)) == 1


def test_rolling_analyzer_keeps_state_and_bounds_memory():
    analyzer = RollingAnalyzer(window_size=3)
    for index in range(6):
        analyzer.push(f"INFO event {index}")
    assert analyzer.buffered_lines == 3


def test_rolling_analyzer_detects_across_lines():
    analyzer = RollingAnalyzer(window_size=20)
    observed = []
    for _ in range(8):
        observed.extend(analyzer.push("sshd: Failed password for admin from 203.0.113.8 port 22 ssh2"))
    assert observed
    assert any("auth" in item.category.lower() or "password" in item.title.lower() for item in observed)
