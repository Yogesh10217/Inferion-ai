"""
CLI Commands for Enterprise Tool Calling Subsystem
"""

import argparse
import sys
import json
import os
import yaml

from sdk.python.llm_engine.tools import ToolsClient

BASE_URL = os.environ.get("TOOLS_API_URL", "http://localhost:8000")


def format_output(data, fmt):
    if fmt == "json":
        print(json.dumps(data, indent=2))
    elif fmt == "yaml":
        print(yaml.dump(data))
    elif fmt == "table":
        if isinstance(data, list):
            for item in data:
                print("---")
                for k, v in item.items():
                    print(f"{k}: {v}")
        elif isinstance(data, dict):
            for k, v in data.items():
                print(f"{k}: {v}")
        else:
            print(data)
    elif fmt == "markdown":
        print("```json\n" + json.dumps(data, indent=2) + "\n```")


def handle_create(args):
    print(f"Creating tool '{args.name}'...")
    client = ToolsClient(base_url=BASE_URL)
    res = client.create(args.name, args.description or "", category=args.category)
    format_output(res, args.format)


def handle_list(args):
    client = ToolsClient(base_url=BASE_URL)
    res = client.list(category=args.category, tenant_id=args.tenant)
    format_output(res, args.format)


def handle_execute(args):
    client = ToolsClient(base_url=BASE_URL)
    params = json.loads(args.params) if args.params else {}
    res = client.execute(args.id, params)
    format_output(res, args.format)


def handle_validate(args):
    client = ToolsClient(base_url=BASE_URL)
    params = json.loads(args.params) if args.params else {}
    res = client.validate(args.id, params)
    format_output(res, args.format)


def handle_metrics(args):
    client = ToolsClient(base_url=BASE_URL)
    res = client.metrics(args.id, tenant_id=args.tenant)
    format_output(res, args.format)


def handle_audit(args):
    client = ToolsClient(base_url=BASE_URL)
    res = client.audit(args.id, tenant_id=args.tenant)
    format_output(res, args.format)


def add_tools_parser(subparsers):
    tools_parser = subparsers.add_parser("tools", help="Manage and execute enterprise tools")
    tools_parser.add_argument("--format", choices=["json", "yaml", "table", "markdown"], default="json")
    tools_subparsers = tools_parser.add_subparsers(dest="command")

    # create
    create_p = tools_subparsers.add_parser("create", help="Create a tool")
    create_p.add_argument("name", help="Tool Name")
    create_p.add_argument("--description", "-d", help="Description")
    create_p.add_argument("--category", default="custom", help="Category")

    # list
    list_p = tools_subparsers.add_parser("list", help="List all tools")
    list_p.add_argument("--category", help="Filter by category")
    list_p.add_argument("--tenant", default="global", help="Tenant ID")

    # execute
    exec_p = tools_subparsers.add_parser("execute", help="Execute a tool")
    exec_p.add_argument("id", help="Tool ID")
    exec_p.add_argument("--params", help="JSON parameters string")

    # validate
    val_p = tools_subparsers.add_parser("validate", help="Validate tool parameters")
    val_p.add_argument("id", help="Tool ID")
    val_p.add_argument("--params", help="JSON parameters string")

    # metrics
    met_p = tools_subparsers.add_parser("metrics", help="Get tool metrics")
    met_p.add_argument("id", help="Tool ID")
    met_p.add_argument("--tenant", default="global", help="Tenant ID")

    # audit
    aud_p = tools_subparsers.add_parser("audit", help="Get tool audit logs")
    aud_p.add_argument("id", help="Tool ID")
    aud_p.add_argument("--tenant", default="global", help="Tenant ID")
