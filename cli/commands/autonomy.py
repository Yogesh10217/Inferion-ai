"""
CLI Commands for Autonomous Execution
"""

import argparse
import sys
import json
import os
import yaml

from sdk.python.llm_engine.autonomy import AutonomyClient

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


def handle_run(args):
    client = AutonomyClient(base_url=BASE_URL)
    res = client.submit_goal(args.goal, tenant_id=args.tenant)
    format_output(res, args.format)


def handle_pause(args):
    client = AutonomyClient(base_url=BASE_URL)
    res = client.pause(args.id)
    format_output(res, args.format)


def handle_resume(args):
    client = AutonomyClient(base_url=BASE_URL)
    res = client.resume(args.id)
    format_output(res, args.format)


def handle_stop(args):
    client = AutonomyClient(base_url=BASE_URL)
    res = client.stop(args.id)
    format_output(res, args.format)


def add_autonomy_parser(subparsers):
    a_parser = subparsers.add_parser("autonomy", help="Autonomous execution commands")
    a_parser.add_argument("--format", choices=["json", "yaml", "table", "markdown"], default="json")
    a_sub = a_parser.add_subparsers(dest="command")

    run_p = a_sub.add_parser("run", help="Run goal autonomously")
    run_p.add_argument("goal", help="Goal prompt")
    run_p.add_argument("--tenant", default="global", help="Tenant ID")

    pause_p = a_sub.add_parser("pause", help="Pause execution")
    pause_p.add_argument("id", help="Execution ID")

    res_p = a_sub.add_parser("resume", help="Resume execution")
    res_p.add_argument("id", help="Execution ID")

    stop_p = a_sub.add_parser("stop", help="Stop execution")
    stop_p.add_argument("id", help="Execution ID")
