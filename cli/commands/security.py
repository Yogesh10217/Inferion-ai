"""CLI Commands for Security & API Key Management."""

import argparse
from typing import Dict, Any
from app.security.api_keys import APIKeyManager, APIKeyPolicy

key_manager = APIKeyManager()


def format_output(data: Any, fmt: str = "json") -> None:
    import json
    if fmt == "json":
        print(json.dumps(data, indent=2, default=str))
    else:
        print(str(data))


def add_security_parser(subparsers: argparse._SubParsersAction) -> None:
    sec_parser = subparsers.add_parser("security", help="Enterprise Security & API Keys management")
    sec_sub = sec_parser.add_subparsers(dest="command")

    # api-keys list
    list_p = sec_sub.add_parser("api-keys-list", help="List API keys")
    list_p.add_argument("--tenant-id", default="global", help="Tenant ID")
    list_p.add_argument("--format", default="json", choices=["json", "text"])

    # api-keys create
    create_p = sec_sub.add_parser("api-keys-create", help="Create new API key")
    create_p.add_argument("--name", required=True, help="Key name")
    create_p.add_argument("--tenant-id", default="global", help="Tenant ID")
    create_p.add_argument("--format", default="json", choices=["json", "text"])


def handle_security_command(args: argparse.Namespace) -> None:
    if args.command == "api-keys-list":
        keys = key_manager.list_api_keys(tenant_id=args.tenant_id)
        format_output({"api_keys": [k.model_dump() for k in keys]}, args.format)
    elif args.command == "api-keys-create":
        res = key_manager.generate_api_key(name=args.name, tenant_id=args.tenant_id)
        format_output({"api_key": res}, args.format)
