"""CLI Commands for Marketplace Platform."""

import argparse
from typing import Dict, Any
from app.marketplace.manager import MarketplaceManager

mkt_manager = MarketplaceManager()


def format_output(data: Any, fmt: str = "json") -> None:
    import json
    if fmt == "json":
        print(json.dumps(data, indent=2, default=str))
    else:
        print(str(data))


def add_marketplace_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("marketplace", help="Marketplace commands")
    sub = p.add_subparsers(dest="command")

    list_p = sub.add_parser("list", help="List marketplace items")
    list_p.add_argument("--format", default="json", choices=["json", "text"])


def handle_marketplace_command(args: argparse.Namespace) -> None:
    if args.command == "list":
        items = mkt_manager.registry.list_items(published_only=False)
        format_output({"items": [i.model_dump() for i in items]}, args.format)
