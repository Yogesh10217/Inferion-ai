"""CLI Commands for Security & Security Intelligence Management (Phase 5.32)."""

import argparse
import json
from typing import Dict, Any
from app.security.api_keys import APIKeyManager
from app.security_intelligence.manager import SecurityIntelligenceManager
from app.security_intelligence.assets import SecurityAssetType, SecurityAssetCriticality

key_manager = APIKeyManager()
sec_intel_manager = SecurityIntelligenceManager()


def format_output(data: Any, fmt: str = "json") -> None:
    if fmt == "json":
        print(json.dumps(data, indent=2, default=str))
    else:
        print(str(data))


def add_security_parser(subparsers: argparse._SubParsersAction) -> None:
    sec_parser = subparsers.add_parser("security", help="Enterprise Security & Security Intelligence Management")
    sec_sub = sec_parser.add_subparsers(dest="command")

    # Legacy api-keys list/create
    list_p = sec_sub.add_parser("api-keys-list", help="List API keys")
    list_p.add_argument("--tenant-id", default="global", help="Tenant ID")
    list_p.add_argument("--format", default="json", choices=["json", "text"])

    create_p = sec_sub.add_parser("api-keys-create", help="Create new API key")
    create_p.add_argument("--name", required=True, help="Key name")
    create_p.add_argument("--tenant-id", default="global", help="Tenant ID")
    create_p.add_argument("--format", default="json", choices=["json", "text"])

    # Phase 5.32 Security Intelligence Commands
    assets_p = sec_sub.add_parser("assets", help="List security assets")
    assets_p.add_argument("--tenant-id", required=True, help="Tenant ID")
    assets_p.add_argument("--format", default="json")

    threats_p = sec_sub.add_parser("threats", help="List security threats")
    threats_p.add_argument("--tenant-id", required=True, help="Tenant ID")
    threats_p.add_argument("--format", default="json")

    vulns_p = sec_sub.add_parser("vulnerabilities", help="List vulnerabilities")
    vulns_p.add_argument("--tenant-id", required=True, help="Tenant ID")
    vulns_p.add_argument("--format", default="json")

    posture_p = sec_sub.add_parser("posture", help="Get security posture")
    posture_p.add_argument("--tenant-id", required=True, help="Tenant ID")
    posture_p.add_argument("--format", default="json")

    analytics_p = sec_sub.add_parser("analytics", help="Get security analytics report")
    analytics_p.add_argument("--tenant-id", required=True, help="Tenant ID")
    analytics_p.add_argument("--format", default="json")


def handle_security_command(args: argparse.Namespace) -> None:
    if args.command == "api-keys-list":
        keys = key_manager.list_api_keys(tenant_id=args.tenant_id)
        format_output({"api_keys": [k.model_dump() for k in keys]}, args.format)
    elif args.command == "api-keys-create":
        res = key_manager.generate_api_key(name=args.name, tenant_id=args.tenant_id)
        format_output({"api_key": res}, args.format)
    elif args.command == "assets":
        assets = sec_intel_manager.asset_manager.list_assets(tenant_id=args.tenant_id)
        format_output({"assets": [a.model_dump() for a in assets]}, args.format)
    elif args.command == "threats":
        threats = sec_intel_manager.threat_manager.list_threats(tenant_id=args.tenant_id)
        format_output({"threats": [t.model_dump() for t in threats]}, args.format)
    elif args.command == "posture":
        posture = sec_intel_manager.posture_manager.calculate_posture(tenant_id=args.tenant_id)
        format_output(posture.model_dump(), args.format)
    elif args.command == "analytics":
        report = sec_intel_manager.analytics_engine.generate_report(tenant_id=args.tenant_id)
        format_output(report.model_dump(), args.format)
