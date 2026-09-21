"""Unit tests for CLI integration."""

from click.testing import CliRunner

from cli.commands.applications import applications_cli


def test_cli_commands():
    runner = CliRunner()

    res_create = runner.invoke(applications_cli, ["create", "--name", "CLI App", "--tenant-id", "t_cli"])
    assert res_create.exit_code == 0
    assert "CLI App" in res_create.output

    res_list = runner.invoke(applications_cli, ["list", "--tenant-id", "t_cli"])
    assert res_list.exit_code == 0
    assert "t_cli" in res_list.output
