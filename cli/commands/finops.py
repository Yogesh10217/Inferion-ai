"""CLI Commands for FinOps Platform."""

import argparse
from typing import Dict, Any
from app.finops.manager import FinOpsManager

finops_manager = FinOpsManager()


def format_output(data: Any, fmt: str = "json") -> None:
    import json
    if fmt == "json":
        print(json.dumps(data, indent=2, default=str))
    else:
        print(str(data))


def add_finops_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("finops", help="FinOps platform commands")
    sub = p.add_subparsers(dest="command")

    summary_p = sub.add_parser("summary", help="Get FinOps platform summary")
    summary_p.add_argument("--format", default="json", choices=["json", "text"])

    list_costs_p = sub.add_parser("costs", help="List cost ledger entries")
    list_costs_p.add_argument("--format", default="json", choices=["json", "text"])


def handle_finops_command(args: argparse.Namespace) -> None:
    if args.command == "summary":
        format_output(finops_manager.get_summary(), args.format)
    elif args.command == "costs":
        entries = finops_manager.cost_ledger.list_entries()
        total = finops_manager.cost_ledger.get_total_cost()
        format_output({"total_cost": str(total), "entries": [e.model_dump() for e in entries]}, args.format)
