"""
Standalone CLI Entry Point for Memory Subsystem
"""

import argparse
import sys
from cli.commands.memory import (
    add_memory_parser, handle_create, handle_list, handle_get, handle_search,
    handle_compress, handle_summarize, handle_archive, handle_profile, handle_analytics
)


def execute_command(args):
    handlers = {
        "create": handle_create,
        "list": handle_list,
        "get": handle_get,
        "search": handle_search,
        "compress": handle_compress,
        "summarize": handle_summarize,
        "archive": handle_archive,
        "profile": handle_profile,
        "analytics": handle_analytics,
    }
    if args.command in handlers:
        try:
            handlers[args.command](args)
        except Exception as e:
            print(f"Error executing command '{args.command}': {e}")
            sys.exit(1)
    else:
        print(f"Unknown memory command: {args.command}")


def main():
    parser = argparse.ArgumentParser(prog="llm-engine")
    subparsers = parser.add_subparsers(dest="subcommand")
    add_memory_parser(subparsers)

    args = parser.parse_args()
    if args.subcommand == "memory":
        if args.command:
            execute_command(args)
        else:
            parser.parse_args(["memory", "--help"])


if __name__ == "__main__":
    main()
