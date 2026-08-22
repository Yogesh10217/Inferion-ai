"""CLI Commands for Operations & SRE Platform."""

import argparse
from typing import Dict, Any
from app.operations.manager import OperationsManager

operations_manager = OperationsManager()


def format_output(data: Any, fmt: str = "json") -> None:
    import json
    if fmt == "json":
        print(json.dumps(data, indent=2, default=str))
    else:
        print(str(data))


def add_operations_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("operations", help="Operations & SRE platform commands")
    sub = p.add_subparsers(dest="command")

    health_p = sub.add_parser("health", help="Get operational health")
    health_p.add_argument("--format", default="json", choices=["json", "text"])

    incidents_p = sub.add_parser("incidents", help="List active incidents")
    incidents_p.add_argument("--format", default="json", choices=["json", "text"])


def handle_operations_command(args: argparse.Namespace) -> None:
    if args.command == "health":
        format_output(operations_manager.get_summary(), args.format)
    elif args.command == "incidents":
        incidents = operations_manager.incident_manager.list_incidents()
        format_output([i.model_dump() for i in incidents], args.format)
