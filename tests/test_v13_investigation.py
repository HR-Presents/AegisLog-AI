from aegislog.investigation import build_incidents, build_timeline, entity_profiles


LOGS = [
    "Aug 29 14:22:01 server sshd[1]: Failed password for root from 203.0.113.45 port 22 ssh2\n",
    "Aug 29 14:22:02 server sshd[2]: Failed password for root from 203.0.113.45 port 22 ssh2\n",
    "Aug 29 14:22:03 server sshd[3]: Failed password for admin from 203.0.113.45 port 22 ssh2\n",
    "Aug 29 14:22:04 server sshd[4]: Failed password for admin from 203.0.113.45 port 22 ssh2\n",
    "Aug 29 14:22:05 server sshd[5]: Failed password for ubuntu from 203.0.113.45 port 22 ssh2\n",
    'Aug 29 14:23:00 server nginx[4]: 203.0.113.99 - - "GET /.env HTTP/1.1" 404 153\n',
]


def test_incident_ids_confidence_and_entities_are_stable():
    first = build_incidents(LOGS)
    second = build_incidents(LOGS)
    auth = next(item for item in first if item.category == "authentication")
    assert auth.id.startswith("INC-")
    assert auth.id == next(item for item in second if item.category == "authentication").id
    assert auth.severity == "HIGH"
    assert 80 <= auth.confidence <= 99
    assert "203.0.113.45" in auth.entities


def test_timeline_extracts_service_time_and_entities():
    timeline = build_timeline(LOGS)
    assert timeline[0].timestamp == "14:22:01"
    assert timeline[0].service == "sshd"
    assert "203.0.113.45" in timeline[0].entities
    assert any("user:root" in item.entities for item in timeline)


def test_entity_profiles_track_occurrences_and_services():
    profiles = entity_profiles(LOGS)
    ip = next(item for item in profiles if item.value == "203.0.113.45")
    assert ip.kind == "ip"
    assert ip.occurrences == 5
    assert "sshd" in ip.services
    root = next(item for item in profiles if item.kind == "user" and item.value == "root")
    assert root.occurrences == 2
