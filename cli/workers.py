"""
CLI Workers Command Entrypoint
"""

import argparse
import sys
from cli.commands.workers import add_workers_parser, handle_create, handle_list, handle_goal, handle_terminate


def main():
    parser = argparse.ArgumentParser(prog="llm-engine workers")
    subparsers = parser.add_subparsers(dest="command")

    add_workers_parser(parser.add_subparsers(dest="subcommand"))
    args = parser.parse_args()

    handlers = {
        "create": handle_create,
        "list": handle_list,
        "goal": handle_goal,
        "terminate": handle_terminate,
    }

    if args.command in handlers:
        handlers[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
