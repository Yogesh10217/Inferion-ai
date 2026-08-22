"""CLI Commands for Governance & Quota Management."""

import argparse
from typing import Dict, Any
from app.governance.quota_manager import QuotaManager

quota_manager = QuotaManager()


def format_output(data: Any, fmt: str = "json") -> None:
    import json
    if fmt == "json":
        print(json.dumps(data, indent=2, default=str))
    else:
        print(str(data))


def add_governance_parser(subparsers: argparse._SubParsersAction) -> None:
    gov_parser = subparsers.add_parser("governance", help="Governance & Quotas management")
    gov_sub = gov_parser.add_subparsers(dest="command")

    usage_p = gov_sub.add_parser("usage", help="Get tenant usage")
    usage_p.add_argument("--tenant-id", default="global", help="Tenant ID")
    usage_p.add_argument("--format", default="json", choices=["json", "text"])

    quotas_p = gov_sub.add_parser("quotas", help="Get tenant quotas")
    quotas_p.add_argument("--tenant-id", default="global", help="Tenant ID")
    quotas_p.add_argument("--format", default="json", choices=["json", "text"])


def handle_governance_command(args: argparse.Namespace) -> None:
    if args.command == "usage":
        u = quota_manager.get_usage(args.tenant_id)
        format_output({"usage": u.model_dump()}, args.format)
    elif args.command == "quotas":
        defn = quota_manager.get_definition(args.tenant_id)
        format_output({"definition": defn.model_dump()}, args.format)
