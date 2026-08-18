"""
CLI Commands for Enterprise Multi-Agent Collaboration Platform
"""

import argparse
import sys
import json
import os
import yaml

from sdk.python.llm_engine.teams import TeamsClient

BASE_URL = os.environ.get("TEAMS_API_URL", "http://localhost:8000")


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
    print(f"Creating team '{args.name}'...")
    client = TeamsClient(base_url=BASE_URL)
    res = client.create(args.name, team_type=args.type, description=args.description or "")
    format_output(res, args.format)


def handle_list(args):
    client = TeamsClient(base_url=BASE_URL)
    res = client.list(tenant_id=args.tenant)
    format_output(res, args.format)


def handle_run(args):
    print(f"Running team '{args.id}' with goal: '{args.goal}'...")
    client = TeamsClient(base_url=BASE_URL)
    res = client.run(args.id, args.goal)
    format_output(res, args.format)


def handle_pause(args):
    client = TeamsClient(base_url=BASE_URL)
    res = client.pause(args.id)
    format_output(res, args.format)


def handle_resume(args):
    client = TeamsClient(base_url=BASE_URL)
    res = client.resume(args.id)
    format_output(res, args.format)


def handle_cancel(args):
    client = TeamsClient(base_url=BASE_URL)
    res = client.cancel(args.id)
    format_output(res, args.format)


def handle_history(args):
    client = TeamsClient(base_url=BASE_URL)
    res = client.history(args.id)
    format_output(res, args.format)


def handle_metrics(args):
    client = TeamsClient(base_url=BASE_URL)
    res = client.metrics(args.id)
    format_output(res, args.format)


def handle_billing(args):
    client = TeamsClient(base_url=BASE_URL)
    res = client.billing(args.id)
    format_output(res, args.format)


def add_teams_parser(subparsers):
    teams_parser = subparsers.add_parser("teams", help="Manage and execute multi-agent teams")
    teams_parser.add_argument("--format", choices=["json", "yaml", "table", "markdown"], default="json")
    teams_subparsers = teams_parser.add_subparsers(dest="command")

    # create
    create_p = teams_subparsers.add_parser("create", help="Create an agent team")
    create_p.add_argument("name", help="Team Name")
    create_p.add_argument("--type", default="engineering", help="Team Type")
    create_p.add_argument("--description", "-d", help="Description")

    # list
    list_p = teams_subparsers.add_parser("list", help="List all agent teams")
    list_p.add_argument("--tenant", default="global", help="Tenant ID")

    # run
    run_p = teams_subparsers.add_parser("run", help="Run an agent team")
    run_p.add_argument("id", help="Team ID")
    run_p.add_argument("goal", help="Goal prompt for team execution")

    # pause / resume / cancel
    pause_p = teams_subparsers.add_parser("pause", help="Pause team execution")
    pause_p.add_argument("id", help="Team ID")

    resume_p = teams_subparsers.add_parser("resume", help="Resume team execution")
    resume_p.add_argument("id", help="Team ID")

    cancel_p = teams_subparsers.add_parser("cancel", help="Cancel team execution")
    cancel_p.add_argument("id", help="Team ID")

    # history / metrics / billing
    hist_p = teams_subparsers.add_parser("history", help="Get team blackboard history")
    hist_p.add_argument("id", help="Team ID")

    met_p = teams_subparsers.add_parser("metrics", help="Get team metrics")
    met_p.add_argument("id", help="Team ID")

    bill_p = teams_subparsers.add_parser("billing", help="Get team billing summary")
    bill_p.add_argument("id", help="Team ID")
