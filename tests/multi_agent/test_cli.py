"""
Tests for CLI Team Commands
"""

import pytest
import argparse
from cli.commands.teams import add_teams_parser, format_output


def test_cli_teams_parser_setup():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="subcommand")
    add_teams_parser(subparsers)

    args = parser.parse_args(["teams", "--format", "json", "list", "--tenant", "org_a"])
    assert args.subcommand == "teams"
    assert args.command == "list"
    assert args.tenant == "org_a"
    assert args.format == "json"


def test_cli_format_output(capsys):
    data = {"team_id": "team_1", "status": "completed"}
    format_output(data, "json")
    captured = capsys.readouterr()
    assert '"team_id": "team_1"' in captured.out
