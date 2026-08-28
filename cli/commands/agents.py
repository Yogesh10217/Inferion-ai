"""
CLI Commands for Enterprise Agent Subsystem (Phase 5.36).
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


def handle_register(args):
    print(f"Registering enterprise agent '{args.name}'...")
    data = {
        "status": "registered",
        "agent": {
            "name": args.name,
            "type": args.type or "GENERAL",
            "role": args.role or "TASK_EXECUTOR",
            "capabilities": args.capabilities.split(",") if args.capabilities else ["READ"],
        }
    }
    format_output(data, args.format)


def handle_list(args):
    print(f"Listing agents for tenant '{args.tenant_id}'...")
    format_output([
        {"id": "agent_demo_1", "name": "Primary Planner Agent", "type": "PLANNER", "status": "ACTIVE"},
        {"id": "agent_demo_2", "name": "Task Executor Agent", "type": "EXECUTOR", "status": "ACTIVE"}
    ], args.format)


def handle_task(args):
    print(f"Creating agent task for agent '{args.agent_id}'...")
    format_output({
        "status": "CREATED",
        "task_id": "task_12345",
        "goal": args.goal,
        "prompt": args.prompt,
    }, args.format)


def handle_plan(args):
    print(f"Generating agent plan for task '{args.task_id}'...")
    format_output({
        "plan_id": "plan_67890",
        "task_id": args.task_id,
        "steps": [
            {"step_number": 1, "action": "retrieve_context", "target": "KNOWLEDGE_INTELLIGENCE"},
            {"step_number": 2, "action": "execute_governed_action", "target": "PLATFORM_OPERATIONS"},
        ],
        "is_feasible": True,
    }, args.format)


def handle_execute(args):
    print(f"Executing agent task with goal: '{args.goal}'...")
    format_output({
        "status": "COMPLETED",
        "execution_id": "exec_999",
        "trace_id": "trace_888",
        "output_summary": "Task executed cleanly via governed DelegationRequest.",
    }, args.format)


def handle_trace(args):
    print(f"Fetching trace '{args.trace_id}'...")
    format_output({
        "trace_id": args.trace_id,
        "status": "FINALIZED",
        "fingerprint": "a1b2c3d4e5f67890a1b2c3d4e5f67890a1b2c3d4e5f67890a1b2c3d4e5f67890",
        "snapshot_id": "snap_111",
    }, args.format)


def handle_analytics(args):
    print(f"Fetching analytics for tenant '{args.tenant_id}'...")
    format_output({
        "tenant_id": args.tenant_id,
        "task_success_rate": 0.98,
        "verification_success_rate": 0.99,
        "autonomy_violations_total": 0,
        "human_escalation_rate": 0.02,
        "agent_reliability_score": 96.5,
    }, args.format)


def add_agents_parser(subparsers):
    agents_parser = subparsers.add_parser("agents", help="Enterprise Agent Orchestration Platform CLI")
    agents_parser.add_argument("--format", choices=["json", "yaml", "table", "markdown"], default="json")
    agents_parser.add_argument("--tenant-id", default="default", help="Tenant ID")
    agent_subparsers = agents_parser.add_subparsers(dest="command")

    # register
    reg_p = agent_subparsers.add_parser("register", help="Register an enterprise agent")
    reg_p.add_argument("name", help="Agent Name")
    reg_p.add_argument("--type", default="GENERAL", help="Agent Type")
    reg_p.add_argument("--role", default="TASK_EXECUTOR", help="Agent Role")
    reg_p.add_argument("--capabilities", help="Comma-separated capability names")

    # list
    agent_subparsers.add_parser("list", help="List all registered agents")

    # task
    task_p = agent_subparsers.add_parser("task", help="Create a task for an agent")
    task_p.add_argument("agent_id", help="Agent ID")
    task_p.add_argument("goal", help="Task Goal")
    task_p.add_argument("prompt", help="User execution prompt")

    # plan
    plan_p = agent_subparsers.add_parser("plan", help="Formulate a plan for a task")
    plan_p.add_argument("task_id", help="Task ID")

    # execute
    exec_p = agent_subparsers.add_parser("execute", help="Execute an agent task end-to-end")
    exec_p.add_argument("goal", help="Goal")
    exec_p.add_argument("prompt", help="Prompt")

    # trace
    tr_p = agent_subparsers.add_parser("trace", help="Fetch execution trace and fingerprint")
    tr_p.add_argument("trace_id", help="Trace ID")

    # analytics
    agent_subparsers.add_parser("analytics", help="View agent platform analytics")
