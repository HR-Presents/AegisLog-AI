from typer.testing import CliRunner

from aegislog import __version__
from aegislog.cli import app

runner = CliRunner()


def test_version_flag():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert result.stdout.strip() == f"AegisLog AI {__version__}"


def test_doctor():
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "Local detection engine: ready" in result.stdout


def test_analyze_sample():
    result = runner.invoke(app, ["analyze", "examples/auth.log"])
    assert result.exit_code == 0
    assert "Possible brute-force" in result.stdout


def test_incidents_sample():
    result = runner.invoke(app, ["incidents", "examples/auth.log"])
    assert result.exit_code == 0
    assert "authentication" in result.stdout
