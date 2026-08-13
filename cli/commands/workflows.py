"""
CLI Commands for Enterprise Workflows Subsystem
"""

import argparse
import sys
import json
import os
import yaml

from sdk.python.llm_engine.client import LLMEngineClient

BASE_URL = os.environ.get("WORKFLOW_API_URL", "http://localhost:8000")


def get_client():
    return LLMEngineClient(base_url=BASE_URL)


def format_output(data, fmt):
    if fmt == "json":
        print(json.dumps(data, indent=2))
    elif fmt == "yaml":
        print(yaml.dump(data))
    elif fmt == "table":
        if isinstance(data, list):
            for item in data:
                print("---")
                if isinstance(item, dict):
                    for k, v in item.items():
                        print(f"{k}: {v}")
                else:
                    print(item)
        elif isinstance(data, dict):
            for k, v in data.items():
                print(f"{k}: {v}")
        else:
            print(data)
    elif fmt == "markdown":
        print("```json\n" + json.dumps(data, indent=2) + "\n```")


def handle_create(args):
    print(f"Creating workflow '{args.name}'...")
    client = get_client()
    spec = json.loads(args.spec) if args.spec else None
    data = client.workflows.create(name=args.name, description=args.description or "", spec=spec, workflow_id=args.id)
    format_output(data, args.format)


def handle_list(args):
    print("Listing workflows...")
    client = get_client()
    data = client.workflows.list()
    format_output(data, args.format)


def handle_run(args):
    print(f"Running workflow '{args.id}'...")
    client = get_client()
    inputs = json.loads(args.inputs) if args.inputs else {}
    data = client.workflows.run(args.id, inputs=inputs)
    format_output(data, args.format)


def handle_resume(args):
    print(f"Resuming run '{args.run_id}'...")
    client = get_client()
    data = client.workflows.resume(args.run_id, approved=args.approved, feedback=args.feedback)
    format_output(data, args.format)


def handle_approve(args):
    print(f"Approving run '{args.run_id}'...")
    client = get_client()
    data = client.workflows.approve(args.run_id, approved=True, feedback=args.feedback)
    format_output(data, args.format)


def handle_history(args):
    print(f"Fetching history for run '{args.run_id}'...")
    client = get_client()
    data = client.workflows.history(args.run_id)
    format_output(data, args.format)


def handle_rollback(args):
    print(f"Rolling back run '{args.run_id}'...")
    client = get_client()
    data = client.workflows.rollback(args.run_id, checkpoint_id=args.checkpoint_id)
    format_output(data, args.format)


def handle_fork(args):
    print(f"Forking run '{args.run_id}'...")
    client = get_client()
    data = client.workflows.fork(args.run_id, checkpoint_id=args.checkpoint_id)
    format_output(data, args.format)


def add_workflows_parser(subparsers):
    wf_parser = subparsers.add_parser("workflows", help="Manage and execute enterprise workflows")
    wf_parser.add_argument("--format", choices=["json", "yaml", "table", "markdown"], default="json")
    wf_subparsers = wf_parser.add_subparsers(dest="command")

    # create
    create_p = wf_subparsers.add_parser("create", help="Create a workflow")
    create_p.add_argument("name", help="Workflow name")
    create_p.add_argument("--id", help="Optional workflow ID")
    create_p.add_argument("--description", help="Description")
    create_p.add_argument("--spec", help="JSON string spec")

    # list
    wf_subparsers.add_parser("list", help="List all workflows")

    # run
    run_p = wf_subparsers.add_parser("run", help="Run a workflow")
    run_p.add_argument("id", help="Workflow ID")
    run_p.add_argument("--inputs", help="JSON inputs string")

    # resume
    resume_p = wf_subparsers.add_parser("resume", help="Resume a paused workflow run")
    resume_p.add_argument("run_id", help="Run ID")
    resume_p.add_argument("--approved", action="store_true", help="Set approval decision")
    resume_p.add_argument("--feedback", help="Approval feedback")

    # approve
    approve_p = wf_subparsers.add_parser("approve", help="Approve a waiting workflow run")
    approve_p.add_argument("run_id", help="Run ID")
    approve_p.add_argument("--feedback", help="Approval feedback")

    # history
    history_p = wf_subparsers.add_parser("history", help="Get workflow execution history")
    history_p.add_argument("run_id", help="Run ID")

    # rollback
    rb_p = wf_subparsers.add_parser("rollback", help="Rollback a run to a checkpoint")
    rb_p.add_argument("run_id", help="Run ID")
    rb_p.add_argument("--checkpoint-id", help="Checkpoint ID")

    # fork
    fork_p = wf_subparsers.add_parser("fork", help="Fork a workflow run")
    fork_p.add_argument("run_id", help="Run ID")
    fork_p.add_argument("--checkpoint-id", help="Checkpoint ID")
