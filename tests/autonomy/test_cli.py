"""
Tests for Autonomy CLI Commands
"""

import argparse

from cli.commands.autonomy import add_autonomy_parser
from cli.commands.workers import add_workers_parser


def test_cli_autonomy_and_workers_parsers():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="subcommand")
    add_autonomy_parser(sub)
    add_workers_parser(sub)

    args_a = parser.parse_args(["autonomy", "run", "Test Goal"])
    assert args_a.subcommand == "autonomy"
    assert args_a.goal == "Test Goal"

    args_w = parser.parse_args(["workers", "create", "Dev Worker"])
    assert args_w.subcommand == "workers"
    assert args_w.name == "Dev Worker"
