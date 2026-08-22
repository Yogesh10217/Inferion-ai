"""CLI Commands for Reliability & Circuit Breakers."""

import argparse
from typing import Dict, Any
from app.reliability.health import SystemHealthManager

health_manager = SystemHealthManager()


def format_output(data: Any, fmt: str = "json") -> None:
    import json
    if fmt == "json":
        print(json.dumps(data, indent=2, default=str))
    else:
        print(str(data))


def add_reliability_parser(subparsers: argparse._SubParsersAction) -> None:
    rel_parser = subparsers.add_parser("reliability", help="Reliability & Health management")
    rel_sub = rel_parser.add_subparsers(dest="command")

    health_p = rel_sub.add_parser("health", help="Get system health")
    health_p.add_argument("--format", default="json", choices=["json", "text"])


def handle_reliability_command(args: argparse.Namespace) -> None:
    if args.command == "health":
        import asyncio
        res = asyncio.run(health_manager.check_liveness())
        format_output({"health": res}, args.format)
