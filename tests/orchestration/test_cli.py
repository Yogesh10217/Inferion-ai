"""Integration tests for Orchestration CLI commands."""

from click.testing import CliRunner

from cli.commands.orchestration import orchestration_cli


def test_orchestration_cli_commands():
    runner = CliRunner()

    res_wf = runner.invoke(orchestration_cli, ["workflow", "--tenant-id", "t_cli"])
    assert res_wf.exit_code == 0
    assert "t_cli" in res_wf.output

    res_ex = runner.invoke(orchestration_cli, ["execute", "--workflow-id", "wf_100"])
    assert res_ex.exit_code == 0
    assert "RUNNING" in res_ex.output
