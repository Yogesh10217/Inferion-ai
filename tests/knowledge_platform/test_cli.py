"""Integration tests for Knowledge Platform CLI commands."""

from click.testing import CliRunner

from cli.commands.knowledge_platform import knowledge_cli


def test_knowledge_platform_cli_commands():
    runner = CliRunner()

    res_ret = runner.invoke(knowledge_cli, ["retrieve", "--query", "policy", "--tenant-id", "t_cli_kp"])
    assert res_ret.exit_code == 0
    assert "policy" in res_ret.output

    res_mem = runner.invoke(knowledge_cli, ["memory", "--tenant-id", "t_cli_kp"])
    assert res_mem.exit_code == 0
    assert "t_cli_kp" in res_mem.output
