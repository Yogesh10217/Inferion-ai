"""Unit tests for CLI Intelligence Commands."""

from click.testing import CliRunner

from cli.commands.intelligence import intelligence_cli


def test_cli_intelligence_signal():
    runner = CliRunner()
    result = runner.invoke(
        intelligence_cli,
        [
            "signal",
            "--source",
            "OPERATIONS",
            "--type",
            "METRIC_THRESHOLD",
            "--message",
            "CLI Test Signal",
            "--tenant-id",
            "t_cli",
        ],
    )
    assert result.exit_code == 0
    assert "Ingested intelligence signal" in result.output


def test_cli_intelligence_insights():
    runner = CliRunner()
    result = runner.invoke(intelligence_cli, ["insights", "--tenant-id", "t_cli"])
    assert result.exit_code == 0
