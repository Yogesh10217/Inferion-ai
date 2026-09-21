"""
Tests for CLI Commands
"""

import argparse

from cli.commands.tools import add_tools_parser, format_output


def test_cli_parser_setup():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="subcommand")
    add_tools_parser(subparsers)

    args = parser.parse_args(["tools", "--format", "json", "list", "--category", "builtin"])
    assert args.subcommand == "tools"
    assert args.command == "list"
    assert args.category == "builtin"
    assert args.format == "json"


def test_cli_format_output(capsys):
    data = {"status": "ok", "count": 5}
    format_output(data, "json")
    captured = capsys.readouterr()
    assert '"status": "ok"' in captured.out
