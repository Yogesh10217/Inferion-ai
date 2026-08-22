"""CLI Commands for Developers & Projects."""

import argparse
from typing import Dict, Any
from app.developer_platform.manager import DeveloperPlatformManager

dev_manager = DeveloperPlatformManager()


def format_output(data: Any, fmt: str = "json") -> None:
    import json
    if fmt == "json":
        print(json.dumps(data, indent=2, default=str))
    else:
        print(str(data))


def add_developers_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("developers", help="Developer platform commands")
    sub = p.add_subparsers(dest="command")

    summary_p = sub.add_parser("summary", help="Get developer platform summary")
    summary_p.add_argument("--format", default="json", choices=["json", "text"])


def handle_developers_command(args: argparse.Namespace) -> None:
    if args.command == "summary":
        format_output(dev_manager.get_summary(), args.format)
