"""
CLI Tool Command Module Entrypoint
"""

import argparse
import sys
from cli.commands.tools import (
    add_tools_parser,
    handle_create,
    handle_list,
    handle_execute,
    handle_validate,
    handle_metrics,
    handle_audit,
)


def main():
    parser = argparse.ArgumentParser(prog="llm-engine tools")
    subparsers = parser.add_subparsers(dest="command")

    # Reuse subparsers handlers
    add_tools_parser(parser.add_subparsers(dest="subcommand"))
    args = parser.parse_args()

    handlers = {
        "create": handle_create,
        "list": handle_list,
        "execute": handle_execute,
        "validate": handle_validate,
        "metrics": handle_metrics,
        "audit": handle_audit,
    }

    if args.command in handlers:
        handlers[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
