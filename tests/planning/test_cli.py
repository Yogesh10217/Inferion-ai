"""
Tests for CLI Planning Commands
"""

import argparse

from cli.commands.planning import add_planning_parser, format_output


def test_cli_planning_parser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="subcommand")
    add_planning_parser(sub)

    args = parser.parse_args(["planning", "--format", "json", "create", "CLI Plan"])
    assert args.subcommand == "planning"
    assert args.command == "create"
    assert args.title == "CLI Plan"


def test_cli_format_output(capsys):
    data = {"plan_id": "p1", "status": "completed"}
    format_output(data, "yaml")
    captured = capsys.readouterr()
    assert "plan_id: p1" in captured.out
