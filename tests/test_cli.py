# ABOUTME: Tests for the CLI entry point using Click's test runner.
# ABOUTME: Tests command registration and help output.

from click.testing import CliRunner

from llm_weather.cli import main


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "run" in result.output
    assert "report" in result.output
    assert "publish" in result.output


def test_cli_run_help():
    runner = CliRunner()
    result = runner.invoke(main, ["run", "--help"])
    assert result.exit_code == 0


def test_cli_report_help():
    runner = CliRunner()
    result = runner.invoke(main, ["report", "--help"])
    assert result.exit_code == 0
    assert "run-dir" in result.output.lower() or "RUN_DIR" in result.output


def test_cli_publish_help():
    runner = CliRunner()
    result = runner.invoke(main, ["publish", "--help"])
    assert result.exit_code == 0
