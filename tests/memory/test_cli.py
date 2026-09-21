"""
Tests for Memory CLI Command Parser & Registration
"""

import argparse

from cli.commands.memory import add_memory_parser


def test_cli_memory_parser_registration():
    parser = argparse.ArgumentParser(prog="llm-engine")
    subparsers = parser.add_subparsers(dest="subcommand")
    add_memory_parser(subparsers)

    args = parser.parse_args(["memory", "create", "Fact: Python 3.12 is used"])
    assert args.subcommand == "memory"
    assert args.command == "create"
    assert args.content == "Fact: Python 3.12 is used"

    args_search = parser.parse_args(["memory", "search", "Python", "--top-k", "5"])
    assert args_search.command == "search"
    assert args_search.query == "Python"
    assert args_search.top_k == 5
