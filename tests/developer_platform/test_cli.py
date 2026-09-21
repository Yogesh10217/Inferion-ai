"""Unit tests for `llm-engine developer-platform` CLI commands."""

from click.testing import CliRunner

from cli.commands.developer_platform import developer_platform_cli


def test_cli_developer_platform_commands():
    runner = CliRunner()
    res_projects = runner.invoke(developer_platform_cli, ["projects", "--tenant-id", "t_cli_dev"])
    assert res_projects.exit_code == 0
    assert "t_cli_dev" in res_projects.output

    res_apis = runner.invoke(developer_platform_cli, ["apis", "--tenant-id", "t_cli_dev"])
    assert res_apis.exit_code == 0
    assert "t_cli_dev" in res_apis.output
