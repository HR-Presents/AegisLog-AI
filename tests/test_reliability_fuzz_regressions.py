from __future__ import annotations

import random
import string
from pathlib import Path

from aegislog.engine import AnalysisState, analyze_file, analyze_lines
from aegislog.streaming import analyze_stream


SEED = 0xAE615


def _signature(findings):
    return [(item.severity, item.category, item.title, item.evidence) for item in findings]


def _random_noise(rng: random.Random, max_length: int = 240) -> str:
    alphabet = string.ascii_letters + string.digits + string.punctuation + " \t" + "éΩ中🙂"
    return "".join(rng.choice(alphabet) for _ in range(rng.randint(0, max_length)))


def test_randomized_malformed_lines_do_not_crash_engine() -> None:
    rng = random.Random(SEED)
    lines = [_random_noise(rng) for _ in range(1000)]

    findings = analyze_lines(lines, timestamp_year_hint=2026)

    assert isinstance(findings, list)
    assert all(item.severity in {"LOW", "MEDIUM", "HIGH", "CRITICAL"} for item in findings)


def test_randomized_chunk_sizes_match_full_file(tmp_path: Path) -> None:
    rng = random.Random(SEED)
    lines: list[str] = []
    for second in range(12):
        lines.append(
            f"2026-09-10T10:00:{second:02d}Z web01 sshd: Failed password for root from 203.0.113.77 port 22"
        )
        lines.append(_random_noise(rng, max_length=120))
    lines.extend(
        [
            "2026-09-10T10:01:00Z api: ERROR database connection timeout",
            "2026-09-10T10:01:01Z host firewall: UFW BLOCK SRC=198.51.100.9 DST=192.0.2.2",
            "2026-09-10T10:01:02Z web: GET /../../etc/passwd HTTP/1.1",
        ]
    )
    path = tmp_path / "mixed.log"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    _, full_findings = analyze_file(path, timestamp_year_hint=2026)
    expected = _signature(full_findings)

    chunk_sizes = {1, 2, len(lines), len(lines) + 17}
    chunk_sizes.update(rng.randint(1, len(lines) + 10) for _ in range(24))
    for chunk_size in sorted(chunk_sizes):
        streamed = analyze_stream(path, chunk_size=chunk_size, timestamp_year_hint=2026)
        assert _signature(streamed.findings) == expected, chunk_size
        assert streamed.lines == len(lines), chunk_size


def test_out_of_order_auth_permutations_keep_same_window_result() -> None:
    lines = [
        f"2026-09-10T10:{minute:02d}:{second:02d}Z auth01 sshd: Failed password for admin from 2001:db8::44 port 22"
        for minute, second in [(0, 5), (1, 0), (2, 30), (4, 59), (3, 15), (0, 45)]
    ]
    expected = _signature(analyze_lines(lines, auth_window_seconds=300))
    rng = random.Random(SEED)

    for _ in range(40):
        candidate = list(lines)
        rng.shuffle(candidate)
        assert _signature(analyze_lines(candidate, auth_window_seconds=300)) == expected


def test_randomized_auth_source_flood_stays_bounded() -> None:
    rng = random.Random(SEED)
    state = AnalysisState(max_auth_sources=8, max_auth_events=20, max_findings=50)

    for index in range(200):
        source = f"198.51.100.{(index % 250) + 1}"
        second = rng.randint(0, 59)
        state.process(
            f"2026-09-10T10:{index % 60:02d}:{second:02d}Z auth{index % 5} sshd: "
            f"Failed password for user{index % 9} from {source} port 22"
        )

    auth_findings = [item for item in state.findings() if item.category == "authentication"]
    assert len(auth_findings) <= 8
    assert state.dropped_auth_sources > 0
    assert state.dropped_auth_events > 0 or state.expired_auth_events > 0
