"""CLI Commands for Enterprise AI Observability, Monitoring & AIOps Platform."""

import argparse
import json
import os
import sys
import yaml
import urllib.request
import urllib.error

BASE_URL = os.environ.get("OBSERVABILITY_API_URL", "http://localhost:8000/v1")


def format_output(data, fmt):
    """Format CLI dictionary/list outputs into requested format."""
    if fmt == "json":
        print(json.dumps(data, indent=2))
    elif fmt == "yaml":
        print(yaml.dump(data, sort_keys=False))
    elif fmt == "table":
        if isinstance(data, list):
            for i, item in enumerate(data, 1):
                print(f"--- Record {i} ---")
                if isinstance(item, dict):
                    for k, v in item.items():
                        print(f"  {k:<20}: {v}")
                else:
                    print(f"  {item}")
        elif isinstance(data, dict):
            for k, v in data.items():
                print(f"{k:<25}: {v}")
        else:
            print(data)
    elif fmt == "markdown":
        print("```json\n" + json.dumps(data, indent=2) + "\n```")


def api_get(endpoint: str) -> dict:
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"error": f"API request to {url} failed: {e}"}


def api_post(endpoint: str, payload: dict) -> dict:
    url = f"{BASE_URL}{endpoint}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"error": f"API POST to {url} failed: {e}"}


def handle_traces(args):
    data = api_get("/observability/traces")
    format_output(data, args.format)


def handle_trace(args):
    data = api_get(f"/observability/traces/{args.trace_id}")
    format_output(data, args.format)


def handle_execution(args):
    data = api_get(f"/observability/executions/{args.execution_id}")
    format_output(data, args.format)


def handle_replay(args):
    data = api_post(f"/observability/executions/{args.execution_id}/replay", {"force_external_effects": args.force_external_effects})
    format_output(data, args.format)


def handle_costs(args):
    endpoint = "/observability/costs"
    if args.execution_id:
        endpoint += f"?execution_id={args.execution_id}"
    data = api_get(endpoint)
    format_output(data, args.format)


def handle_performance(args):
    endpoint = "/observability/performance"
    if args.component:
        endpoint += f"?component={args.component}"
    data = api_get(endpoint)
    format_output(data, args.format)


def handle_failures(args):
    data = api_get(f"/observability/failures?execution_id={args.execution_id}")
    format_output(data, args.format)


def handle_anomalies(args):
    data = api_get(f"/observability/anomalies?limit={args.limit}")
    format_output(data, args.format)


def handle_alerts(args):
    data = api_get("/observability/alerts")
    format_output(data, args.format)


def handle_slos(args):
    data = api_get("/observability/slos")
    format_output(data, args.format)


def handle_evaluate(args):
    data = api_get("/observability/evaluations")
    format_output(data, args.format)


def add_observability_parser(subparsers):
    obs_parser = subparsers.add_parser("observability", help="Enterprise AI Observability, Monitoring & AIOps platform CLI")
    obs_parser.add_argument("--format", choices=["json", "yaml", "table", "markdown"], default="json")
    obs_sub = obs_parser.add_subparsers(dest="command")

    # traces
    obs_sub.add_parser("traces", help="List active traces summary")

    # trace
    tr_p = obs_sub.add_parser("trace", help="Get detailed spans for a trace ID")
    tr_p.add_argument("trace_id", help="Trace ID")

    # execution
    ex_p = obs_sub.add_parser("execution", help="Get execution details by ID")
    ex_p.add_argument("execution_id", help="Execution ID")

    # replay
    rp_p = obs_sub.add_parser("replay", help="Replay an execution")
    rp_p.add_argument("execution_id", help="Execution ID")
    rp_p.add_argument("--force-external-effects", action="store_true", help="Enable high-risk external side effects during replay")

    # costs
    c_p = obs_sub.add_parser("costs", help="Get cost attribution metrics")
    c_p.add_argument("--execution-id", help="Execution ID filter")

    # performance
    p_p = obs_sub.add_parser("performance", help="Get latency percentiles and performance metrics")
    p_p.add_argument("--component", help="Component name filter")

    # failures
    f_p = obs_sub.add_parser("failures", help="Analyze root cause of execution failure")
    f_p.add_argument("execution_id", help="Execution ID")

    # anomalies
    a_p = obs_sub.add_parser("anomalies", help="Get recent statistical anomaly events")
    a_p.add_argument("--limit", type=int, default=50, help="Limit number of anomalies returned")

    # alerts
    obs_sub.add_parser("alerts", help="Get active system alerts")

    # slos
    obs_sub.add_parser("slos", help="Get Service Level Objectives (SLOs) status")

    # evaluate
    obs_sub.add_parser("evaluate", help="Get AI quality and evaluation metrics")
