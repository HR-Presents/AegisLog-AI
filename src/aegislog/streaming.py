from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .engine import AnalysisState, Finding


@dataclass(frozen=True)
class StreamSummary:
    lines: int
    chunks: int
    findings: tuple[Finding, ...]
    severities: dict[str, int]
    dropped_findings: int = 0
    dropped_auth_events: int = 0
    truncated_lines: int = 0


def analyze_stream(
    path: Path,
    chunk_size: int = 2000,
    max_findings: int = 5000,
    *,
    auth_window_seconds: int = 300,
    max_auth_events: int = 10_000,
    max_auth_sources: int = 2_048,
    max_line_bytes: int = 1_000_000,
) -> StreamSummary:
    """Analyze incrementally with shared bounded correlation state.

    ``chunk_size`` controls progress batching only; detection state is shared so findings do
    not depend on chunk boundaries. Oversized lines are explicitly truncated before analysis.
    Correlation sources, retained auth events, and non-auth findings are bounded while ingesting.
    Severity totals still include findings dropped after the retention cap.
    """
    if chunk_size < 1 or max_findings < 0 or max_line_bytes < 1 or max_auth_sources < 1:
        raise ValueError("stream limits must be valid positive values")
    total = chunks = truncated_lines = 0
    state = AnalysisState(
        auth_window_seconds=auth_window_seconds,
        max_auth_events=max_auth_events,
        max_auth_sources=max_auth_sources,
        max_findings=max_findings,
    )
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            total += 1
            if (total - 1) % chunk_size == 0:
                chunks += 1
            encoded = line.encode("utf-8", errors="replace")
            if len(encoded) > max_line_bytes:
                line = encoded[:max_line_bytes].decode("utf-8", errors="ignore") + " [TRUNCATED]"
                truncated_lines += 1
            state.process(line)
    all_findings = state.findings()
    kept = all_findings[:max_findings]
    return StreamSummary(
        total,
        chunks,
        tuple(kept),
        state.severity_counts(),
        dropped_findings=state.dropped_findings + max(0, len(all_findings) - len(kept)),
        dropped_auth_events=state.dropped_auth_events,
        truncated_lines=truncated_lines,
    )
