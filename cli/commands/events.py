"""CLI Commands for Event Intelligence Platform (Phase 5.34)."""

import argparse
import json
from typing import Dict, Any
from app.event_intelligence.manager import EventIntelligenceManager

event_manager = EventIntelligenceManager()


def format_output(data: Any, fmt: str = "json") -> None:
    if fmt == "json":
        print(json.dumps(data, indent=2, default=str))
    else:
        print(str(data))


def add_events_parser(subparsers: argparse._SubParsersAction) -> None:
    evt_parser = subparsers.add_parser("events", help="Enterprise AI Event Intelligence & Response")
    evt_sub = evt_parser.add_subparsers(dest="command")

    create_p = evt_sub.add_parser("create", help="Create enterprise event")
    create_p.add_argument("--tenant-id", required=True, help="Tenant ID")
    create_p.add_argument("--source-name", default="CLI", help="Source name")
    create_p.add_argument("--event-type", default="CUSTOM_EVENT", help="Event type")
    create_p.add_argument("--severity", default="MEDIUM", help="Severity")
    create_p.add_argument("--format", default="json")

    list_p = evt_sub.add_parser("list", help="List enterprise events")
    list_p.add_argument("--tenant-id", required=True, help="Tenant ID")
    list_p.add_argument("--format", default="json")

    corr_p = evt_sub.add_parser("correlate", help="List event correlation groups")
    corr_p.add_argument("--tenant-id", required=True, help="Tenant ID")
    corr_p.add_argument("--format", default="json")

    inv_p = evt_sub.add_parser("investigate", help="Initiate investigation")
    inv_p.add_argument("--tenant-id", required=True, help="Tenant ID")
    inv_p.add_argument("--event-id", required=True, help="Event ID")
    inv_p.add_argument("--format", default="json")

    resp_p = evt_sub.add_parser("respond", help="Create response plan")
    resp_p.add_argument("--tenant-id", required=True, help="Tenant ID")
    resp_p.add_argument("--event-id", required=True, help="Event ID")
    resp_p.add_argument("--format", default="json")

    res_p = evt_sub.add_parser("resolve", help="Resolve event")
    res_p.add_argument("--tenant-id", required=True, help="Tenant ID")
    res_p.add_argument("--event-id", required=True, help="Event ID")
    res_p.add_argument("--format", default="json")

    pat_p = evt_sub.add_parser("patterns", help="Detect cross-event patterns")
    pat_p.add_argument("--tenant-id", required=True, help="Tenant ID")
    pat_p.add_argument("--format", default="json")

    analytics_p = evt_sub.add_parser("analytics", help="Get event analytics")
    analytics_p.add_argument("--tenant-id", required=True, help="Tenant ID")
    analytics_p.add_argument("--format", default="json")


def handle_events_command(args: argparse.Namespace) -> None:
    if args.command == "create":
        src = event_manager.source_manager.register_source(args.tenant_id, args.source_name)
        evt = event_manager.event_manager.create_event(args.tenant_id, src.source_id, src.name)
        format_output(evt.model_dump(), args.format)
    elif args.command == "list":
        events = event_manager.event_manager.list_events(args.tenant_id)
        format_output({"events": [e.model_dump() for e in events]}, args.format)
    elif args.command == "correlate":
        groups = event_manager.correlation_manager.list_groups(args.tenant_id)
        format_output({"correlation_groups": [g.model_dump() for g in groups]}, args.format)
    elif args.command == "investigate":
        inv = event_manager.investigation_manager.initiate_investigation(args.tenant_id, args.event_id)
        format_output(inv.model_dump(), args.format)
    elif args.command == "respond":
        from app.event_intelligence.response import EventResponseAction, ResponseTarget
        act = EventResponseAction(target=ResponseTarget.RELIABILITY_PLATFORM, action_type="INVESTIGATE_INCIDENT")
        plan = event_manager.response_manager.create_response_plan(args.tenant_id, args.event_id, [act])
        format_output(plan.model_dump(), args.format)
    elif args.command == "resolve":
        from app.event_intelligence.resolution import EventResolutionStatus
        res = event_manager.resolution_manager.create_resolution(args.tenant_id, args.event_id)
        res = event_manager.resolution_manager.transition_resolution(res.resolution_id, args.tenant_id, EventResolutionStatus.INVESTIGATING)
        res = event_manager.resolution_manager.transition_resolution(res.resolution_id, args.tenant_id, EventResolutionStatus.RESPONSE_PLANNED)
        res = event_manager.resolution_manager.transition_resolution(res.resolution_id, args.tenant_id, EventResolutionStatus.DELEGATED)
        res = event_manager.resolution_manager.transition_resolution(res.resolution_id, args.tenant_id, EventResolutionStatus.VERIFYING)
        final_res = event_manager.resolution_manager.transition_resolution(res.resolution_id, args.tenant_id, EventResolutionStatus.RESOLVED)
        format_output(final_res.model_dump(), args.format)
    elif args.command == "patterns":
        events = event_manager.event_manager.list_events(args.tenant_id)
        pats = event_manager.pattern_detector.detect_patterns(args.tenant_id, events)
        format_output({"patterns": [p.model_dump() for p in pats]}, args.format)
    elif args.command == "analytics":
        report = event_manager.analytics_engine.generate_report(tenant_id=args.tenant_id)
        format_output(report.model_dump(), args.format)
