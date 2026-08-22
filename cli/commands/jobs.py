"""CLI Commands for Distributed Job Management."""

import argparse
from typing import Dict, Any
from app.jobs.job_queue import JobQueue

queue = JobQueue()


def format_output(data: Any, fmt: str = "json") -> None:
    import json
    if fmt == "json":
        print(json.dumps(data, indent=2, default=str))
    else:
        print(str(data))


def add_jobs_parser(subparsers: argparse._SubParsersAction) -> None:
    jobs_parser = subparsers.add_parser("jobs", help="Distributed Jobs management")
    jobs_sub = jobs_parser.add_subparsers(dest="command")

    list_p = jobs_sub.add_parser("list", help="List background jobs")
    list_p.add_argument("--format", default="json", choices=["json", "text"])

    get_p = jobs_sub.add_parser("get", help="Get job details")
    get_p.add_argument("--id", required=True, help="Job ID")
    get_p.add_argument("--format", default="json", choices=["json", "text"])


def handle_jobs_command(args: argparse.Namespace) -> None:
    if args.command == "list":
        jobs = list(queue._jobs.values())
        format_output({"jobs": [j.model_dump() for j in jobs]}, args.format)
    elif args.command == "get":
        j = queue.get_status(args.id)
        format_output({"job": j.model_dump() if j else None}, args.format)
