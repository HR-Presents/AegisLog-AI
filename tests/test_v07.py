import sqlite3
from pathlib import Path

import pytest

from aegislog.entry import app
from aegislog.migrations import LATEST_SCHEMA, migrate
from aegislog.streaming import analyze_stream


def test_schema_migration_reaches_latest(tmp_path: Path):
    db = sqlite3.connect(tmp_path / "migrate.db")
    db.execute("CREATE TABLE incidents (id INTEGER PRIMARY KEY)")
    assert migrate(db) == LATEST_SCHEMA
    row = db.execute("SELECT value FROM schema_meta WHERE key='schema_version'").fetchone()
    assert row[0] == str(LATEST_SCHEMA)


def test_future_schema_is_rejected(tmp_path: Path):
    db = sqlite3.connect(tmp_path / "future.db")
    db.execute("CREATE TABLE schema_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
    db.execute("INSERT INTO schema_meta(key, value) VALUES('schema_version', '999')")
    with pytest.raises(RuntimeError):
        migrate(db)


def test_v07_commands_registered():
    names = {command.name for command in app.registered_commands}
    assert {"stream", "entities", "behavior"}.issubset(names)


def test_streaming_finding_cap(tmp_path: Path):
    path = tmp_path / "many.log"
    path.write_text("ERROR timeout\n" * 30, encoding="utf-8")
    summary = analyze_stream(path, chunk_size=4, max_findings=5)
    assert summary.lines == 30
    assert len(summary.findings) == 5
    assert summary.severities["MEDIUM"] == 30
