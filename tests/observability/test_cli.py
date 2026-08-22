"""CLI Unit tests for Observability parser and output formatters."""

import pytest
import argparse
from cli.commands.observability import add_observability_parser, format_output


def test_cli_parser_registration():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="sub")
    add_observability_parser(subparsers)

    args = parser.parse_args(["observability", "--format", "json", "traces"])
    assert args.command == "traces"
    assert args.format == "json"



def test_cli_format_output(capsys):
    data = {"status": "ok", "count": 5}
    format_output(data, "json")
    captured = capsys.readouterr()
    assert '"status": "ok"' in captured.out
