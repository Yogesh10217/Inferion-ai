"""
CLI Commands for Enterprise Agent Subsystem
"""

import argparse
import sys
import json
import os
import yaml

BASE_URL = os.environ.get("AGENT_API_URL", "http://localhost:8002/v1")


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
    print(f"Creating agent '{args.id}'...")
    data = {
        "id": args.id,
        "name": args.name or args.id,
        "description": args.description or "",
        "system_prompt": args.prompt or "You are a helpful agent."
    }
    format_output({"status": "created", "agent": data}, args.format)


def handle_list(args):
    print("Listing agents...")
    format_output([{"id": "agent_demo", "name": "Demo Agent", "status": "active"}], args.format)


def handle_run(args):
    print(f"Running agent '{args.id}' with prompt: '{args.prompt}'...")
    format_output({"status": "completed", "agent_id": args.id, "output": "Execution completed successfully."}, args.format)


def handle_resume(args):
    print(f"Resuming session '{args.session_id}'...")
    format_output({"status": "resumed", "session_id": args.session_id}, args.format)


def handle_cancel(args):
    print(f"Cancelling session '{args.session_id}'...")
    format_output({"status": "cancelled", "session_id": args.session_id}, args.format)


def add_agents_parser(subparsers):
    agents_parser = subparsers.add_parser("agents", help="Manage and run enterprise agents")
    agents_parser.add_argument("--format", choices=["json", "yaml", "table", "markdown"], default="json")
    agent_subparsers = agents_parser.add_subparsers(dest="command")

    # create
    create_p = agent_subparsers.add_parser("create", help="Create an agent")
    create_p.add_argument("id", help="Agent ID")
    create_p.add_argument("--name", help="Agent Name")
    create_p.add_argument("--description", help="Agent Description")
    create_p.add_argument("--prompt", help="System Prompt")

    # list
    agent_subparsers.add_parser("list", help="List all agents")

    # run
    run_p = agent_subparsers.add_parser("run", help="Run an agent")
    run_p.add_argument("id", help="Agent ID")
    run_p.add_argument("prompt", help="User execution prompt")

    # resume
    resume_p = agent_subparsers.add_parser("resume", help="Resume an agent session")
    resume_p.add_argument("session_id", help="Session ID")

    # cancel
    cancel_p = agent_subparsers.add_parser("cancel", help="Cancel an agent session")
    cancel_p.add_argument("session_id", help="Session ID")
