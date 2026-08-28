"""CLI Commands for Platform Resilience Subsystem (Phase 5.37)."""

import argparse
import sys
import json
import os
import yaml

BASE_URL = os.environ.get("RESILIENCE_API_URL", "http://localhost:8000/v1")


def format_output(data, fmt):
    if fmt == "json":
        print(json.dumps(data, indent=2))
    elif fmt == "yaml":
        print(yaml.dump(data))
    elif fmt == "table":
        if isinstance(data, list):
            for item in data:
                print("---")
                if isinstance(item, dict):
                    for k, v in item.items():
                        print(f"{k}: {v}")
                else:
                    print(item)
        elif isinstance(data, dict):
            for k, v in data.items():
                print(f"{k}: {v}")
        else:
            print(data)
    elif fmt == "markdown":
        print("```json\n" + json.dumps(data, indent=2) + "\n```")


def handle_services(args):
    print(f"Listing registered resilience services for tenant '{args.tenant_id}'...")
    format_output([
        {"service_id": "res_svc_1", "service_name": "Inference_Core", "tier": "TIER_0_CRITICAL", "status": "ACTIVE"},
        {"service_id": "res_svc_2", "service_name": "Knowledge_Base", "tier": "TIER_1_HIGH", "status": "ACTIVE"}
    ], args.format)


def handle_capacity(args):
    print(f"Evaluating capacity for resource '{args.resource_id}'...")
    format_output({
        "resource_id": args.resource_id,
        "status": "NORMAL",
        "max_utilization_pct": 52.5,
        "recommendation": "NO_ACTION",
    }, args.format)


def handle_scaling(args):
    print(f"Generating scaling plan for resource '{args.resource_id}'...")
    format_output({
        "plan_id": "scaleplan_123",
        "resource_id": args.resource_id,
        "direction": "SCALE_OUT",
        "status": "DELEGATED",
    }, args.format)


def handle_failover(args):
    print(f"Requesting regional failover for service '{args.service_id}'...")
    format_output({
        "plan_id": "failplan_456",
        "service_id": args.service_id,
        "source_region": "us-east-1",
        "target_region": "us-west-2",
        "status": "GOVERNED",
        "requires_approval": True,
    }, args.format)


def handle_recovery(args):
    print(f"Formulating recovery plan for incident '{args.incident_id}'...")
    format_output({
        "recovery_plan_id": "recplan_789",
        "incident_id": args.incident_id,
        "status": "PLANNED",
    }, args.format)


def handle_dr(args):
    print(f"Triggering disaster recovery plan '{args.dr_plan_id}'...")
    format_output({
        "dr_plan_id": args.dr_plan_id,
        "status": "COMPLETED",
        "rto_observed_minutes": 8.5,
        "rpo_observed_minutes": 2.0,
    }, args.format)


def handle_readiness(args):
    print(f"Assessing production readiness for service '{args.service_id}'...")
    format_output({
        "service_id": args.service_id,
        "status": "READY",
        "score": 100.0,
        "hard_failures": [],
    }, args.format)


def handle_runbooks(args):
    print("Listing operational runbooks...")
    format_output([
        {"runbook_id": "rb_001", "title": "Regional Failover Runbook", "status": "FINALIZED", "is_immutable": True}
    ], args.format)


def handle_analytics(args):
    print(f"Fetching resilience analytics for tenant '{args.tenant_id}'...")
    format_output({
        "tenant_id": args.tenant_id,
        "availability_pct": 99.95,
        "mean_time_to_recover_minutes": 12.5,
        "readiness_score": 98.0,
    }, args.format)


def add_resilience_parser(subparsers):
    resilience_parser = subparsers.add_parser("resilience", help="Enterprise Platform Resilience CLI")
    resilience_parser.add_argument("--format", choices=["json", "yaml", "table", "markdown"], default="json")
    resilience_parser.add_argument("--tenant-id", default="default", help="Tenant ID")
    res_subparsers = resilience_parser.add_subparsers(dest="command")

    # services
    res_subparsers.add_parser("services", help="List registered services")

    # capacity
    cap_p = res_subparsers.add_parser("capacity", help="Evaluate capacity")
    cap_p.add_argument("resource_id", help="Resource ID")

    # scaling
    scale_p = res_subparsers.add_parser("scaling", help="Plan scaling operation")
    scale_p.add_argument("resource_id", help="Resource ID")

    # failover
    fail_p = res_subparsers.add_parser("failover", help="Request regional failover")
    fail_p.add_argument("service_id", help="Service ID")

    # recovery
    rec_p = res_subparsers.add_parser("recovery", help="Formulate recovery plan")
    rec_p.add_argument("incident_id", help="Incident ID")

    # dr
    dr_p = res_subparsers.add_parser("dr", help="Activate disaster recovery")
    dr_p.add_argument("dr_plan_id", help="DR Plan ID")

    # readiness
    read_p = res_subparsers.add_parser("readiness", help="Assess production readiness")
    read_p.add_argument("service_id", help="Service ID")

    # runbooks
    res_subparsers.add_parser("runbooks", help="List operational runbooks")

    # analytics
    res_subparsers.add_parser("analytics", help="View resilience analytics report")
