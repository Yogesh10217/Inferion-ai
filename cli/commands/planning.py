"""
CLI Commands for Autonomous Planning Subsystem
"""

import argparse
import sys
import json
import os
import yaml

from sdk.python.llm_engine.planning import PlanningClient

BASE_URL = os.environ.get("PLANNING_API_URL", "http://localhost:8000")


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
    client = PlanningClient(base_url=BASE_URL)
    res = client.create(args.title, description=args.description or "")
    format_output(res, args.format)


def handle_list(args):
    client = PlanningClient(base_url=BASE_URL)
    res = client.list(tenant_id=args.tenant)
    format_output(res, args.format)


def handle_simulate(args):
    client = PlanningClient(base_url=BASE_URL)
    res = client.simulate(args.id)
    format_output(res, args.format)


def handle_execute(args):
    client = PlanningClient(base_url=BASE_URL)
    res = client.execute(args.id, budget_dollars=args.budget)
    format_output(res, args.format)


def handle_reflect(args):
    client = PlanningClient(base_url=BASE_URL)
    res = client.reflect(args.id)
    format_output(res, args.format)


def handle_optimize(args):
    client = PlanningClient(base_url=BASE_URL)
    res = client.optimize(args.id)
    format_output(res, args.format)


def handle_history(args):
    client = PlanningClient(base_url=BASE_URL)
    res = client.history(args.id)
    format_output(res, args.format)


def handle_metrics(args):
    client = PlanningClient(base_url=BASE_URL)
    res = client.metrics(args.id)
    format_output(res, args.format)


def handle_billing(args):
    client = PlanningClient(base_url=BASE_URL)
    res = client.billing(args.id)
    format_output(res, args.format)


def add_planning_parser(subparsers):
    p_parser = subparsers.add_parser("planning", help="Manage and execute autonomous plans")
    p_parser.add_argument("--format", choices=["json", "yaml", "table", "markdown"], default="json")
    p_sub = p_parser.add_subparsers(dest="command")

    # create
    create_p = p_sub.add_parser("create", help="Create a plan")
    create_p.add_argument("title", help="Plan Title")
    create_p.add_argument("--description", "-d", help="Description")

    # list
    list_p = p_sub.add_parser("list", help="List all plans")
    list_p.add_argument("--tenant", default="global", help="Tenant ID")

    # simulate
    sim_p = p_sub.add_parser("simulate", help="Simulate a plan")
    sim_p.add_argument("id", help="Plan ID")

    # execute
    exec_p = p_sub.add_parser("execute", help="Execute a plan")
    exec_p.add_argument("id", help="Plan ID")
    exec_p.add_argument("--budget", type=float, default=50.0, help="Budget Limit ($)")

    # reflect / optimize
    ref_p = p_sub.add_parser("reflect", help="Reflect on plan execution")
    ref_p.add_argument("id", help="Plan ID")

    opt_p = p_sub.add_parser("optimize", help="Optimize a plan")
    opt_p.add_argument("id", help="Plan ID")

    # history / metrics / billing
    hist_p = p_sub.add_parser("history", help="Get plan reflection history")
    hist_p.add_argument("id", help="Plan ID")

    met_p = p_sub.add_parser("metrics", help="Get planning metrics")
    met_p.add_argument("id", help="Plan ID")

    bill_p = p_sub.add_parser("billing", help="Get planning billing summary")
    bill_p.add_argument("id", help="Plan ID")
