"""
Standalone CLI Entry Point for Workflows
"""

import argparse
import sys
from cli.commands.workflows import add_workflows_parser, handle_create, handle_list, handle_run, handle_resume, handle_approve, handle_history, handle_rollback, handle_fork


def execute_command(args):
    handlers = {
        "create": handle_create,
        "list": handle_list,
        "run": handle_run,
        "resume": handle_resume,
        "approve": handle_approve,
        "history": handle_history,
        "rollback": handle_rollback,
        "fork": handle_fork,
    }
    if args.command in handlers:
        try:
            handlers[args.command](args)
        except Exception as e:
            print(f"Error executing command '{args.command}': {e}")
            sys.exit(1)
    else:
        print(f"Unknown workflows command: {args.command}")


def main():
    parser = argparse.ArgumentParser(prog="llm-engine")
    subparsers = parser.add_subparsers(dest="subcommand")
    add_workflows_parser(subparsers)

    args = parser.parse_args()
    if args.subcommand == "workflows":
        if args.command:
            execute_command(args)
        else:
            parser.parse_args(["workflows", "--help"])


if __name__ == "__main__":
    main()
