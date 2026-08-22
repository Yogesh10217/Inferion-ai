"""
CLI Autonomy Command Entrypoint
"""

import argparse
import sys
from cli.commands.autonomy import add_autonomy_parser, handle_run, handle_pause, handle_resume, handle_stop


def main():
    parser = argparse.ArgumentParser(prog="llm-engine autonomy")
    subparsers = parser.add_subparsers(dest="command")

    add_autonomy_parser(parser.add_subparsers(dest="subcommand"))
    args = parser.parse_args()

    handlers = {
        "run": handle_run,
        "pause": handle_pause,
        "resume": handle_resume,
        "stop": handle_stop,
    }

    if args.command in handlers:
        handlers[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
