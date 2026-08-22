"""Unit tests for `llm-engine integrations` CLI commands."""

import pytest
from click.testing import CliRunner
from cli.commands.integrations import integrations_cli


def test_cli_integration_commands():
    runner = CliRunner()
    res_list = runner.invoke(integrations_cli, ["list", "--tenant-id", "t_cli"])
    assert res_list.exit_code == 0
    assert "t_cli" in res_list.output

    res_health = runner.invoke(integrations_cli, ["health", "--integration-id", "integ_101"])
    assert res_health.exit_code == 0
    assert "integ_101" in res_health.output
