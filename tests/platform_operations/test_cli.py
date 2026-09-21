"""Unit tests for CLI Operations commands."""

from click.testing import CliRunner

from cli.commands.operations import operations_cli


def test_cli_operations_services_list():
    runner = CliRunner()
    result = runner.invoke(operations_cli, ["services", "--tenant-id", "t_cli"])
    assert result.exit_code == 0
    assert "t_cli" in result.output


def test_cli_operations_incidents_list():
    runner = CliRunner()
    result = runner.invoke(operations_cli, ["incidents", "--tenant-id", "t_cli"])
    assert result.exit_code == 0
    assert "t_cli" in result.output
