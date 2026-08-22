"""CLI Commands for Enterprise Control Plane & Platform Management."""

import argparse
from typing import Dict, Any
from app.control_plane.manager import ControlPlaneManager

cp_manager = ControlPlaneManager()


def format_output(data: Any, fmt: str = "json") -> None:
    import json
    if fmt == "json":
        print(json.dumps(data, indent=2, default=str))
    else:
        print(str(data))


def add_control_plane_parser(subparsers: argparse._SubParsersAction) -> None:
    cp_parser = subparsers.add_parser("control-plane", help="Enterprise Control Plane management")
    cp_sub = cp_parser.add_subparsers(dest="command")

    # summary
    summary_p = cp_sub.add_parser("summary", help="Get control plane summary")
    summary_p.add_argument("--format", default="json", choices=["json", "text"])

    # tenants list
    t_list = cp_sub.add_parser("tenants-list", help="List tenants")
    t_list.add_argument("--format", default="json", choices=["json", "text"])

    # tenants create
    t_create = cp_sub.add_parser("tenants-create", help="Create new tenant")
    t_create.add_argument("--name", required=True, help="Tenant name")
    t_create.add_argument("--format", default="json", choices=["json", "text"])


def handle_control_plane_command(args: argparse.Namespace) -> None:
    if args.command == "summary":
        res = cp_manager.get_summary()
        format_output(res, args.format)
    elif args.command == "tenants-list":
        tenants = cp_manager.tenant_manager.list_tenants()
        format_output({"tenants": [t.model_dump() for t in tenants]}, args.format)
    elif args.command == "tenants-create":
        bundle = cp_manager.provisioning_engine.provision_new_tenant(tenant_name=args.name)
        format_output({"tenant_bundle": bundle.model_dump()}, args.format)
