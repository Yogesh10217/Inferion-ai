"""CLI Commands for Extension Framework."""

import argparse
from typing import Dict, Any
from app.extensions.manager import ExtensionManager

ext_manager = ExtensionManager()


def format_output(data: Any, fmt: str = "json") -> None:
    import json
    if fmt == "json":
        print(json.dumps(data, indent=2, default=str))
    else:
        print(str(data))


def add_extensions_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("extensions", help="Extension framework commands")
    sub = p.add_subparsers(dest="command")

    list_p = sub.add_parser("list", help="List registered extensions")
    list_p.add_argument("--format", default="json", choices=["json", "text"])


def handle_extensions_command(args: argparse.Namespace) -> None:
    if args.command == "list":
        exts = ext_manager.registry.list_extensions()
        format_output({"extensions": [e.model_dump() for e in exts]}, args.format)
