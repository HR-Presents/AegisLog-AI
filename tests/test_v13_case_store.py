from pathlib import Path

from aegislog.case_store import get_case, list_cases, save_cases
from aegislog.investigation import build_incidents


LOGS = [
    "Aug 29 14:22:01 server sshd[1]: Failed password for root from 203.0.113.45 port 22 ssh2\n",
    "Aug 29 14:22:02 server sshd[2]: Failed password for root from 203.0.113.45 port 22 ssh2\n",
    "Aug 29 14:22:03 server sshd[3]: Failed password for admin from 203.0.113.45 port 22 ssh2\n",
    "Aug 29 14:22:04 server sshd[4]: Failed password for admin from 203.0.113.45 port 22 ssh2\n",
    "Aug 29 14:22:05 server sshd[5]: Failed password for ubuntu from 203.0.113.45 port 22 ssh2\n",
]


def test_cases_survive_new_database_connections(tmp_path: Path):
    db = tmp_path / "cases.db"
    incidents = build_incidents(LOGS)
    assert save_cases("auth.log", incidents, path=db) == 1
    rows = list_cases(path=db)
    assert len(rows) == 1
    saved = get_case(incidents[0].id, path=db)
    assert saved is not None
    assert saved["incident_id"] == incidents[0].id
    assert saved["confidence"] == incidents[0].confidence
    assert "203.0.113.45" in saved["entities"]
    assert saved["timeline"]


def test_saving_same_case_updates_observation_count(tmp_path: Path):
    db = tmp_path / "cases.db"
    incidents = build_incidents(LOGS)
    save_cases("auth.log", incidents, path=db)
    save_cases("auth.log", incidents, path=db)
    saved = get_case(incidents[0].id, path=db)
    assert saved is not None
    assert saved["observation_count"] == 2


def test_case_history_filters_severity(tmp_path: Path):
    db = tmp_path / "cases.db"
    incidents = build_incidents(LOGS)
    save_cases("auth.log", incidents, path=db)
    assert len(list_cases(severity="HIGH", path=db)) == 1
    assert list_cases(severity="CRITICAL", path=db) == []
