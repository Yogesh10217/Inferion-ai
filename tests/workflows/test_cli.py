"""
Tests for CLI Workflows Commands
"""

import argparse
from cli.commands.workflows import add_workflows_parser, handle_list


def test_cli_parser_registration():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="subcommand")
    add_workflows_parser(subparsers)

    args = parser.parse_args(["workflows", "--format", "json", "list"])
    assert args.subcommand == "workflows"
    assert args.command == "list"
    assert args.format == "json"


def test_cli_list_handler(capsys):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="subcommand")
    add_workflows_parser(subparsers)

    args = parser.parse_args(["workflows", "--format", "json", "list"])
    try:
        handle_list(args)
    except Exception:
        pass
    captured = capsys.readouterr()
    assert "Listing workflows..." in captured.out
