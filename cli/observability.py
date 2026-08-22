"""CLI Observability Command Entrypoint."""

import argparse
import sys
from cli.commands.observability import (
    add_observability_parser,
    handle_traces,
    handle_trace,
    handle_execution,
    handle_replay,
    handle_costs,
    handle_performance,
    handle_failures,
    handle_anomalies,
    handle_alerts,
    handle_slos,
    handle_evaluate,
)


def main():
    parser = argparse.ArgumentParser(prog="llm-engine observability")
    subparsers = parser.add_subparsers(dest="command")

    add_observability_parser(subparsers)
    args = parser.parse_args()

    handlers = {
        "traces": handle_traces,
        "trace": handle_trace,
        "execution": handle_execution,
        "replay": handle_replay,
        "costs": handle_costs,
        "performance": handle_performance,
        "failures": handle_failures,
        "anomalies": handle_anomalies,
        "alerts": handle_alerts,
        "slos": handle_slos,
        "evaluate": handle_evaluate,
    }

    if hasattr(args, "command") and args.command in handlers:
        handlers[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
