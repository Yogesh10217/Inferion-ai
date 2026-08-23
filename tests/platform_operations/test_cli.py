"""Unit tests for CLI Operations commands."""

import pytest
from click.testing import CliRunner
from cli.commands.operations import operations_cli


def test_cli_operations_services_list():
    runner = CliRunner()
    result = runner.invoke(operations_cli, ["services", "list"])
    assert result.exit_code == 0


def test_cli_operations_services_create():
    runner = CliRunner()
    result = runner.invoke(operations_cli, ["services", "create", "--name", "CLI Service Test", "--tenant-id", "t_cli"])
    assert result.exit_code == 0
    assert "Created service" in result.output
