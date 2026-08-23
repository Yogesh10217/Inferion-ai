"""CLI Commands for Enterprise AI Data Governance Platform."""

import argparse
from typing import Dict, Any
from app.data_governance.manager import DataGovernanceManager

gov_manager = DataGovernanceManager()


def format_output(data: Any, fmt: str = "json") -> None:
    import json
    if fmt == "json":
        print(json.dumps(data, indent=2, default=str))
    else:
        print(str(data))


def add_data_governance_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("data-governance", help="Data Governance Platform commands")
    sub = p.add_subparsers(dest="subcommand")

    # assets subcommand
    assets_p = sub.add_parser("assets", help="Manage data assets")
    assets_sub = assets_p.add_subparsers(dest="asset_action")

    list_p = assets_sub.add_parser("list", help="List governed data assets")
    list_p.add_argument("--tenant-id", default="global")
    list_p.add_argument("--format", default="json", choices=["json", "text"])

    get_p = assets_sub.add_parser("get", help="Get a governed data asset")
    get_p.add_argument("asset_id", help="Data asset ID")
    get_p.add_argument("--tenant-id", default="global")
    get_p.add_argument("--format", default="json", choices=["json", "text"])

    classify_p = assets_sub.add_parser("classify", help="Classify a data asset")
    classify_p.add_argument("asset_id", help="Data asset ID")
    classify_p.add_argument("--sample", help="Content sample text")
    classify_p.add_argument("--tenant-id", default="global")
    classify_p.add_argument("--format", default="json", choices=["json", "text"])

    # contracts subcommand
    contracts_p = sub.add_parser("contracts", help="Manage data contracts")
    contracts_sub = contracts_p.add_subparsers(dest="contract_action")

    validate_p = contracts_sub.add_parser("validate", help="Validate producer schema compatibility")
    validate_p.add_argument("contract_id", help="Data contract ID")
    validate_p.add_argument("--tenant-id", default="global")
    validate_p.add_argument("--format", default="json", choices=["json", "text"])

    # lineage subcommand
    lineage_p = sub.add_parser("lineage", help="View data asset lineage")
    lineage_p.add_argument("asset_id", help="Data asset ID")
    lineage_p.add_argument("--tenant-id", default="global")
    lineage_p.add_argument("--format", default="json", choices=["json", "text"])

    # trust subcommand
    trust_p = sub.add_parser("trust", help="View data trust score")
    trust_p.add_argument("asset_id", help="Data asset ID")
    trust_p.add_argument("--tenant-id", default="global")
    trust_p.add_argument("--format", default="json", choices=["json", "text"])

    # analytics subcommand
    analytics_p = sub.add_parser("analytics", help="View data governance analytics")
    analytics_p.add_argument("--tenant-id", default="global")
    analytics_p.add_argument("--format", default="json", choices=["json", "text"])


def handle_data_governance_command(args: argparse.Namespace) -> None:
    if args.subcommand == "assets":
        if args.asset_action == "list":
            assets = gov_manager.asset_manager.list_assets(tenant_id=args.tenant_id)
            format_output({"assets": [a.model_dump() for a in assets]}, args.format)
        elif args.asset_action == "get":
            asset = gov_manager.asset_manager.get_asset(args.asset_id, tenant_id=args.tenant_id)
            format_output(asset.model_dump(), args.format)
        elif args.asset_action == "classify":
            res = gov_manager.classification_engine.classify_asset(
                tenant_id=args.tenant_id,
                asset_id=args.asset_id,
                content_sample=args.sample,
            )
            format_output(res.model_dump(), args.format)
    elif args.subcommand == "contracts":
        if args.contract_action == "validate":
            format_output({"status": "VALID", "contract_id": args.contract_id}, args.format)
    elif args.subcommand == "lineage":
        lin = gov_manager.lineage_manager.get_asset_lineage(args.asset_id, tenant_id=args.tenant_id)
        format_output(lin.model_dump(), args.format)
    elif args.subcommand == "trust":
        score = gov_manager.trust_engine.get_trust_score(args.asset_id, tenant_id=args.tenant_id)
        format_output(score.model_dump(), args.format)
    elif args.subcommand == "analytics":
        rep = gov_manager.analytics_engine.generate_report(tenant_id=args.tenant_id)
        format_output(rep.model_dump(), args.format)
