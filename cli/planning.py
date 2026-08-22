"""
CLI Planning Command Entrypoint
"""

import argparse
import sys
from cli.commands.planning import (
    add_planning_parser,
    handle_create,
    handle_list,
    handle_simulate,
    handle_execute,
    handle_reflect,
    handle_optimize,
    handle_history,
    handle_metrics,
    handle_billing,
)


def main():
    parser = argparse.ArgumentParser(prog="llm-engine planning")
    subparsers = parser.add_subparsers(dest="command")

    add_planning_parser(parser.add_subparsers(dest="subcommand"))
    args = parser.parse_args()

    handlers = {
        "create": handle_create,
        "list": handle_list,
        "simulate": handle_simulate,
        "execute": handle_execute,
        "reflect": handle_reflect,
        "optimize": handle_optimize,
        "history": handle_history,
        "metrics": handle_metrics,
        "billing": handle_billing,
    }

    if args.command in handlers:
        handlers[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
