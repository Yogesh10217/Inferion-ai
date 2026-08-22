"""CLI Commands for MLOps Platform."""

import argparse
from typing import Dict, Any
from app.mlops.manager import MLOpsManager

mlops_manager = MLOpsManager()


def format_output(data: Any, fmt: str = "json") -> None:
    import json
    if fmt == "json":
        print(json.dumps(data, indent=2, default=str))
    else:
        print(str(data))


def add_mlops_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("mlops", help="MLOps platform commands")
    sub = p.add_subparsers(dest="command")

    summary_p = sub.add_parser("summary", help="Get MLOps platform summary")
    summary_p.add_argument("--format", default="json", choices=["json", "text"])

    list_p = sub.add_parser("list-assets", help="List registered AI assets")
    list_p.add_argument("--format", default="json", choices=["json", "text"])


def handle_mlops_command(args: argparse.Namespace) -> None:
    if args.command == "summary":
        format_output(mlops_manager.get_summary(), args.format)
    elif args.command == "list-assets":
        assets = mlops_manager.registry.list_assets()
        format_output({"assets": [a.model_dump() for a in assets]}, args.format)
