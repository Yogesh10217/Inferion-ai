"""
CLI Commands for Digital Workers
"""

import argparse
import sys
import json
import os
import yaml

from sdk.python.llm_engine.autonomy import WorkersClient

BASE_URL = os.environ.get("AUTONOMY_API_URL", "http://localhost:8000")


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
    client = WorkersClient(base_url=BASE_URL)
    res = client.create(args.name, template_type=args.type, tenant_id=args.tenant)
    format_output(res, args.format)


def handle_list(args):
    client = WorkersClient(base_url=BASE_URL)
    res = client.list(tenant_id=args.tenant)
    format_output(res, args.format)


def handle_goal(args):
    client = WorkersClient(base_url=BASE_URL)
    res = client.assign_goal(args.id, args.goal)
    format_output(res, args.format)


def handle_terminate(args):
    client = WorkersClient(base_url=BASE_URL)
    res = client.terminate(args.id)
    format_output(res, args.format)


def add_workers_parser(subparsers):
    w_parser = subparsers.add_parser("workers", help="Digital worker management commands")
    w_parser.add_argument("--format", choices=["json", "yaml", "table", "markdown"], default="json")
    w_sub = w_parser.add_subparsers(dest="command")

    c_p = w_sub.add_parser("create", help="Create a digital worker")
    c_p.add_argument("name", help="Worker name")
    c_p.add_argument("--type", default="engineering", help="Template type")
    c_p.add_argument("--tenant", default="global", help="Tenant ID")

    l_p = w_sub.add_parser("list", help="List workers")
    l_p.add_argument("--tenant", default="global", help="Tenant ID")

    g_p = w_sub.add_parser("goal", help="Assign goal to worker")
    g_p.add_argument("id", help="Worker ID")
    g_p.add_argument("goal", help="Goal prompt")

    t_p = w_sub.add_parser("terminate", help="Terminate worker")
    t_p.add_argument("id", help="Worker ID")
