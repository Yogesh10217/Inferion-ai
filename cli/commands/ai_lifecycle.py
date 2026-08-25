"""CLI Commands for AI Lifecycle Platform (Phase 5.33)."""

import argparse
import json
from typing import Dict, Any
from app.ai_lifecycle_platform.manager import AILifecyclePlatformManager

lifecycle_manager = AILifecyclePlatformManager()


def format_output(data: Any, fmt: str = "json") -> None:
    if fmt == "json":
        print(json.dumps(data, indent=2, default=str))
    else:
        print(str(data))


def add_ai_lifecycle_parser(subparsers: argparse._SubParsersAction) -> None:
    lc_parser = subparsers.add_parser("ai-lifecycle", help="Enterprise AI Lifecycle Platform Management")
    lc_sub = lc_parser.add_subparsers(dest="command")

    assets_p = lc_sub.add_parser("assets", help="List AI assets")
    assets_p.add_argument("subaction", choices=["list"], default="list")
    assets_p.add_argument("--tenant-id", required=True, help="Tenant ID")
    assets_p.add_argument("--format", default="json")

    models_p = lc_sub.add_parser("models", help="List AI models")
    models_p.add_argument("subaction", choices=["list"], default="list")
    models_p.add_argument("--tenant-id", required=True, help="Tenant ID")
    models_p.add_argument("--format", default="json")

    agents_p = lc_sub.add_parser("agents", help="List AI agents")
    agents_p.add_argument("subaction", choices=["list"], default="list")
    agents_p.add_argument("--tenant-id", required=True, help="Tenant ID")
    agents_p.add_argument("--format", default="json")

    eval_p = lc_sub.add_parser("evaluate", help="Run evaluation")
    eval_p.add_argument("--tenant-id", required=True, help="Tenant ID")
    eval_p.add_argument("--asset-id", required=True, help="Target asset ID")
    eval_p.add_argument("--suite-id", default="default_suite", help="Suite ID")
    eval_p.add_argument("--format", default="json")

    prom_p = lc_sub.add_parser("promote", help="Request promotion")
    prom_p.add_argument("--tenant-id", required=True, help="Tenant ID")
    prom_p.add_argument("--asset-id", required=True, help="Asset ID")
    prom_p.add_argument("--target", default="STAGING", help="Target environment")
    prom_p.add_argument("--format", default="json")

    rel_p = lc_sub.add_parser("releases", help="Create or view releases")
    rel_p.add_argument("--tenant-id", required=True, help="Tenant ID")
    rel_p.add_argument("--format", default="json")

    drift_p = lc_sub.add_parser("drift", help="Detect drift")
    drift_p.add_argument("--tenant-id", required=True, help="Tenant ID")
    drift_p.add_argument("--asset-id", required=True, help="Asset ID")
    drift_p.add_argument("--format", default="json")

    rb_p = lc_sub.add_parser("rollback", help="Request rollback")
    rb_p.add_argument("--tenant-id", required=True, help="Tenant ID")
    rb_p.add_argument("--asset-id", required=True, help="Asset ID")
    rb_p.add_argument("--target-version", default="1.0.0", help="Target version")
    rb_p.add_argument("--format", default="json")

    ret_p = lc_sub.add_parser("retire", help="Request retirement")
    ret_p.add_argument("--tenant-id", required=True, help="Tenant ID")
    ret_p.add_argument("--asset-id", required=True, help="Asset ID")
    ret_p.add_argument("--format", default="json")

    analytics_p = lc_sub.add_parser("analytics", help="Get lifecycle analytics")
    analytics_p.add_argument("--tenant-id", required=True, help="Tenant ID")
    analytics_p.add_argument("--format", default="json")


def handle_ai_lifecycle_command(args: argparse.Namespace) -> None:
    if args.command == "assets":
        assets = lifecycle_manager.asset_manager.list_assets(tenant_id=args.tenant_id)
        format_output({"assets": [a.model_dump() for a in assets]}, args.format)
    elif args.command == "models":
        models = lifecycle_manager.model_manager.list_models(tenant_id=args.tenant_id)
        format_output({"models": [m.model_dump() for m in models]}, args.format)
    elif args.command == "agents":
        agents = lifecycle_manager.agent_manager.list_agents(tenant_id=args.tenant_id)
        format_output({"agents": [a.model_dump() for a in agents]}, args.format)
    elif args.command == "evaluate":
        run = lifecycle_manager.evaluation_manager.run_evaluation(args.tenant_id, args.asset_id, args.suite_id)
        format_output(run.model_dump(), args.format)
    elif args.command == "promote":
        prom = lifecycle_manager.promotion_manager.request_promotion(args.tenant_id, args.asset_id, args.target)
        format_output(prom.model_dump(), args.format)
    elif args.command == "drift":
        drift = lifecycle_manager.drift_manager.detect_drift(args.tenant_id, args.asset_id)
        format_output(drift.model_dump(), args.format)
    elif args.command == "rollback":
        rb = lifecycle_manager.rollback_manager.request_rollback(args.tenant_id, args.asset_id, args.target_version)
        format_output(rb.model_dump(), args.format)
    elif args.command == "retire":
        ret = lifecycle_manager.retirement_manager.request_retirement(args.tenant_id, args.asset_id)
        format_output(ret.model_dump(), args.format)
    elif args.command == "analytics":
        report = lifecycle_manager.analytics_engine.generate_report(tenant_id=args.tenant_id)
        format_output(report.model_dump(), args.format)
