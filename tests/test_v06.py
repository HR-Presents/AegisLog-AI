from pathlib import Path

from aegislog.behavior import compare_windows
from aegislog.correlation import correlate_entities
from aegislog.engine import Finding
from aegislog.streaming import analyze_stream


def test_entity_correlation_prioritizes_repeated_ip():
    findings = [
        Finding("HIGH", "authentication", "failure", "sshd: failed password for admin from 203.0.113.9", "review"),
        Finding("CRITICAL", "authentication", "failure", "sshd: failed password for admin from 203.0.113.9", "review"),
    ]
    links = correlate_entities(findings)
    ip = next(item for item in links if item.entity_type == "ip")
    assert ip.entity == "203.0.113.9"
    assert ip.event_count == 2
    assert ip.score >= 2


def test_streaming_analysis_reads_multiple_chunks(tmp_path: Path):
    path = tmp_path / "large.log"
    path.write_text("\n".join(["INFO ok"] * 5 + ["ERROR timeout"] * 3) + "\n", encoding="utf-8")
    summary = analyze_stream(path, chunk_size=2)
    assert summary.lines == 8
    assert summary.chunks == 4
    assert summary.severities["MEDIUM"] == 3


def test_behavior_window_detects_growth():
    baseline = [["INFO service ready"] * 2, ["INFO service ready"] * 2]
    current = ["ERROR timeout"] * 6
    deltas = compare_windows(baseline, current)
    assert deltas
    assert any(item.current >= 6 for item in deltas)
