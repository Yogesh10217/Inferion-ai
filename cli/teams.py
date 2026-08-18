"""
CLI Team Command Module Entrypoint
"""

import argparse
import sys
from cli.commands.teams import (
    add_teams_parser,
    handle_create,
    handle_list,
    handle_run,
    handle_pause,
    handle_resume,
    handle_cancel,
    handle_history,
    handle_metrics,
    handle_billing,
)


def main():
    parser = argparse.ArgumentParser(prog="llm-engine teams")
    subparsers = parser.add_subparsers(dest="command")

    add_teams_parser(parser.add_subparsers(dest="subcommand"))
    args = parser.parse_args()

    handlers = {
        "create": handle_create,
        "list": handle_list,
        "run": handle_run,
        "pause": handle_pause,
        "resume": handle_resume,
        "cancel": handle_cancel,
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
