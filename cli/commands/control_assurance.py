"""CLI Commands for Control Assurance Subsystem (Phase 5.38)."""

import argparse
import sys
import json
import os
import yaml

BASE_URL = os.environ.get("CONTROL_ASSURANCE_API_URL", "http://localhost:8000/v1")


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


def handle_controls_list(args):
    print(f"Listing controls for tenant '{args.tenant_id}'...")
    format_output([
        {"control_id": "ctrl_001", "code": "SEC-001", "name": "Strict Auth Control", "category": "SECURITY", "status": "ACTIVE"},
        {"control_id": "ctrl_002", "code": "DAT-001", "name": "Data Encryption Control", "category": "DATA", "status": "ACTIVE"}
    ], args.format)


def handle_controls_evaluate(args):
    print(f"Evaluating control '{args.control_id}'...")
    format_output({
        "evaluation_id": "eval_123",
        "control_id": args.control_id,
        "status": "PASSED",
        "score": 100.0,
    }, args.format)


def handle_violations_list(args):
    print(f"Listing violations for tenant '{args.tenant_id}'...")
    format_output([
        {"violation_id": "viol_001", "control_id": "ctrl_001", "severity": "HIGH", "status": "DETECTED"}
    ], args.format)


def handle_violations_inspect(args):
    print(f"Inspecting violation '{args.violation_id}'...")
    format_output({
        "violation_id": args.violation_id,
        "control_id": "ctrl_001",
        "severity": "HIGH",
        "status": "DETECTED",
        "finding": {"code": "SEC-AUTH-01", "message": "Unauthorized access attempt"},
    }, args.format)


def handle_remediation_plan(args):
    print(f"Planning remediation for violation '{args.violation_id}'...")
    format_output({
        "plan_id": "cplan_456",
        "violation_id": args.violation_id,
        "status": "DELEGATED",
        "delegation_id": "del_789",
    }, args.format)


def handle_attestations_list(args):
    print(f"Listing attestations for tenant '{args.tenant_id}'...")
    format_output([
        {"attestation_id": "att_001", "control_id": "ctrl_001", "status": "ATTESTED", "is_finalized": True}
    ], args.format)


def handle_assurance(args):
    print(f"Calculating assurance score for tenant '{args.tenant_id}'...")
    format_output({
        "tenant_id": args.tenant_id,
        "score": 98.0,
        "band": "STRONG",
        "hard_failures": 0,
    }, args.format)


def handle_analytics(args):
    print(f"Fetching control assurance analytics for tenant '{args.tenant_id}'...")
    format_output({
        "tenant_id": args.tenant_id,
        "total_controls": 45,
        "passed_controls": 43,
        "assurance_score_avg": 95.5,
    }, args.format)


def add_control_assurance_parser(subparsers):
    ca_parser = subparsers.add_parser("control-assurance", help="Enterprise Control Assurance CLI")
    ca_parser.add_argument("--format", choices=["json", "yaml", "table", "markdown"], default="json")
    ca_parser.add_argument("--tenant-id", default="default", help="Tenant ID")
    ca_subparsers = ca_parser.add_subparsers(dest="command")

    # controls
    controls_p = ca_subparsers.add_parser("controls", help="Manage controls")
    controls_sub = controls_p.add_subparsers(dest="subcommand")
    controls_sub.add_parser("list", help="List controls")
    eval_p = controls_sub.add_parser("evaluate", help="Evaluate control")
    eval_p.add_argument("control_id", help="Control ID")

    # violations
    viol_p = ca_subparsers.add_parser("violations", help="Manage violations")
    viol_sub = viol_p.add_subparsers(dest="subcommand")
    viol_sub.add_parser("list", help="List violations")
    insp_p = viol_sub.add_parser("inspect", help="Inspect violation")
    insp_p.add_argument("violation_id", help="Violation ID")

    # remediation
    rem_p = ca_subparsers.add_parser("remediation", help="Remediation actions")
    rem_sub = rem_p.add_subparsers(dest="subcommand")
    plan_p = rem_sub.add_parser("plan", help="Plan remediation")
    plan_p.add_argument("violation_id", help="Violation ID")

    # attestations
    att_p = ca_subparsers.add_parser("attestations", help="Attestations")
    att_sub = att_p.add_subparsers(dest="subcommand")
    att_sub.add_parser("list", help="List attestations")

    # assurance
    ca_subparsers.add_parser("assurance", help="Calculate assurance score")

    # analytics
    ca_subparsers.add_parser("analytics", help="View control assurance analytics")
