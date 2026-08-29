from __future__ import annotations

import pytest

from aegislog import native_live as nl


def test_prime_suppresses_existing_snapshot(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(nl, "collect", lambda *args, **kwargs: ["one\n", "two\n"])
    poller = nl.NativeLivePoller("journald", limit=20)
    assert poller.prime(include_existing=False) == []
    assert poller.poll() == []


def test_prime_can_include_existing_snapshot(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(nl, "collect", lambda *args, **kwargs: ["one\n", "two\n"])
    poller = nl.NativeLivePoller("journald", limit=20)
    assert poller.prime(include_existing=True) == ["one\n", "two\n"]


def test_poll_returns_only_new_native_events(monkeypatch: pytest.MonkeyPatch) -> None:
    snapshots = iter(
        [
            ["old-a\n", "old-b\n"],
            ["old-a\n", "old-b\n", "new-c\n"],
            ["old-b\n", "new-c\n", "new-d\n"],
        ]
    )
    monkeypatch.setattr(nl, "collect", lambda *args, **kwargs: next(snapshots))
    poller = nl.NativeLivePoller("windows", limit=50)
    poller.prime()
    assert poller.poll() == ["new-c\n"]
    assert poller.poll() == ["new-d\n"]


def test_poller_passes_native_options(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_collect(source: str, **kwargs: object) -> list[str]:
        captured["source"] = source
        captured.update(kwargs)
        return []

    monkeypatch.setattr(nl, "collect", fake_collect)
    poller = nl.NativeLivePoller("docker", limit=25, channel="Application", container="api-1")
    poller.poll()
    assert captured == {
        "source": "docker",
        "limit": 25,
        "channel": "Application",
        "container": "api-1",
    }


def test_seen_cache_is_bounded(monkeypatch: pytest.MonkeyPatch) -> None:
    snapshots = iter([[f"line-{i}\n" for i in range(10)], ["line-0\n"]])
    monkeypatch.setattr(nl, "collect", lambda *args, **kwargs: next(snapshots))
    poller = nl.NativeLivePoller("journald", limit=2, seen_limit=4)
    poller.prime()
    assert len(poller._seen) == 4
    assert poller.poll() == ["line-0\n"]
