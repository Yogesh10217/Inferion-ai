"""Unit tests for `llm-engine integrations` CLI commands."""

from click.testing import CliRunner

from cli.commands.integrations import integrations_cli


def test_cli_integration_commands():
    runner = CliRunner()
    res_list = runner.invoke(integrations_cli, ["connectors", "--tenant-id", "t_cli"])
    assert res_list.exit_code == 0
    assert "t_cli" in res_list.output

    res_wf = runner.invoke(integrations_cli, ["workflows", "--tenant-id", "t_cli"])
    assert res_wf.exit_code == 0
    assert "t_cli" in res_wf.output
