"""CLI Commands for Data Fabric Platform."""

import argparse
from typing import Dict, Any
from app.data_fabric.manager import DataFabricManager

fabric_manager = DataFabricManager()


def format_output(data: Any, fmt: str = "json") -> None:
    import json
    if fmt == "json":
        print(json.dumps(data, indent=2, default=str))
    else:
        print(str(data))


def add_data_fabric_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("data-fabric", help="Data Fabric platform commands")
    sub = p.add_subparsers(dest="command")

    summary_p = sub.add_parser("summary", help="Get data fabric platform summary")
    summary_p.add_argument("--format", default="json", choices=["json", "text"])

    list_p = sub.add_parser("list-sources", help="List registered data sources")
    list_p.add_argument("--format", default="json", choices=["json", "text"])


def handle_data_fabric_command(args: argparse.Namespace) -> None:
    if args.command == "summary":
        format_output(fabric_manager.get_summary(), args.format)
    elif args.command == "list-sources":
        sources = fabric_manager.source_manager.list_sources()
        format_output({"data_sources": [s.model_dump() for s in sources]}, args.format)
