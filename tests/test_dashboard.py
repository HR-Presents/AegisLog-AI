from __future__ import annotations

import asyncio
from pathlib import Path

from textual.widgets import DataTable, Input

from aegislog.dashboard import AegisDashboard, build_dashboard_analysis


SAMPLE = Path("examples/auth.log")


def test_dashboard_analysis_runs_complete_pipeline() -> None:
    result = build_dashboard_analysis(SAMPLE)
    assert result.line_count == 7
    assert result.findings
    assert result.incidents
    assert "203.0.113.7" in result.indicators["ipv4"]


def test_dashboard_mounts_and_filters_findings() -> None:
    async def exercise() -> None:
        app = AegisDashboard(SAMPLE)
        async with app.run_test(size=(140, 44)) as pilot:
            await pilot.pause()
            table = app.query_one("#findings-table", DataTable)
            original_rows = table.row_count
            filter_input = app.query_one("#filter", Input)
            filter_input.value = "operational"
            await pilot.pause()
            assert 0 < table.row_count < original_rows
            app.action_refresh_analysis()
            await pilot.pause()
            assert app.analysis.line_count == 7

    asyncio.run(exercise())


def test_dashboard_live_mode_and_export(tmp_path) -> None:
    sample = tmp_path / "security.log"
    sample.write_text(SAMPLE.read_text(encoding="utf-8"), encoding="utf-8")

    async def exercise() -> None:
        app = AegisDashboard(sample)
        async with app.run_test(size=(140, 44)) as pilot:
            await pilot.pause()
            assert app._risk_level({"CRITICAL": 1}) == "CRITICAL"
            app.action_toggle_live()
            assert app.live_enabled is True
            app.action_export_report()
            await pilot.pause()

    asyncio.run(exercise())
    payload = (tmp_path / "security-aegislog-dashboard.json").read_text(encoding="utf-8")
    assert '"line_count": 7' in payload
    assert '"findings"' in payload
