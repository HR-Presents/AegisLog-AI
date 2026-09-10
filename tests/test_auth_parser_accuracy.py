from aegislog.engine import _auth_event


def test_rfc3164_auth_event_extracts_host_account_source_and_timestamp() -> None:
    event = _auth_event(
        "Jan 10 12:34:56 web-01 sshd[4242]: Failed password for invalid user admin "
        "from 203.0.113.7 port 55221 ssh2",
        year_hint=2026,
    )

    assert event.timestamp is not None
    assert event.timestamp.isoformat() == "2026-01-10T12:34:56+00:00"
    assert event.host == "web-01"
    assert event.account == "admin"
    assert event.source_ip == "203.0.113.7"


def test_ipv6_source_is_validated_and_normalized() -> None:
    event = _auth_event(
        "2026-09-10T10:00:00Z host=api-01 sshd: Failed password for root "
        "from [2001:0db8:0:0:0:0:0:7] port 22"
    )

    assert event.source_ip == "2001:db8::7"
    assert event.host == "api-01"
    assert event.account == "root"


def test_destination_address_is_not_used_as_auth_source() -> None:
    event = _auth_event(
        "2026-09-10T10:00:00Z host=api-01 authentication failure "
        "user=alice dst=198.51.100.20 destination_ip=198.51.100.21"
    )

    assert event.source_ip is None
    assert event.account == "alice"
    assert event.host == "api-01"


def test_invalid_source_address_is_rejected() -> None:
    event = _auth_event(
        "2026-09-10T10:00:00Z host=api-01 authentication failure "
        "user=alice src=999.999.999.999 dst=198.51.100.20"
    )

    assert event.source_ip is None


def test_explicit_host_field_takes_priority_over_rfc3164_position() -> None:
    event = _auth_event(
        "Jan 10 12:34:56 relay-01 sshd[4242]: authentication failure "
        "user=alice host=canonical-01 rhost=203.0.113.9",
        year_hint=2026,
    )

    assert event.host == "canonical-01"
    assert event.source_ip == "203.0.113.9"
