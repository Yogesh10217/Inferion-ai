"""Unit tests for Control Plane CLI commands."""

import pytest
import argparse
from cli.commands.control_plane import add_control_plane_parser, handle_control_plane_command


def test_cli_parser_registration():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    add_control_plane_parser(subparsers)

    args = parser.parse_args(["control-plane", "summary"])
    assert args.command == "summary"
