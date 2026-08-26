"""CLI Commands for Knowledge Intelligence Platform (Phase 5.35)."""

import argparse
import json
from typing import Dict, Any
from app.knowledge_intelligence.manager import KnowledgeIntelligenceManager

knowledge_manager = KnowledgeIntelligenceManager()


def format_output(data: Any, fmt: str = "json") -> None:
    if fmt == "json":
        print(json.dumps(data, indent=2, default=str))
    else:
        print(str(data))


def add_knowledge_parser(subparsers: argparse._SubParsersAction) -> None:
    k_parser = subparsers.add_parser("knowledge", help="Enterprise AI Knowledge Intelligence Platform")
    k_sub = k_parser.add_subparsers(dest="command")

    reg_p = k_sub.add_parser("register", help="Register knowledge item")
    reg_p.add_argument("--tenant-id", required=True, help="Tenant ID")
    reg_p.add_argument("--title", required=True, help="Knowledge title")
    reg_p.add_argument("--type", default="DOCUMENT", help="Knowledge type")
    reg_p.add_argument("--format", default="json")

    ret_p = k_sub.add_parser("retrieve", help="Retrieve knowledge context")
    ret_p.add_argument("--tenant-id", required=True, help="Tenant ID")
    ret_p.add_argument("--query", required=True, help="Retrieval query")
    ret_p.add_argument("--format", default="json")

    prov_p = k_sub.add_parser("provenance", help="Get provenance chain")
    prov_p.add_argument("--tenant-id", required=True, help="Tenant ID")
    prov_p.add_argument("--target-id", required=True, help="Target ID")
    prov_p.add_argument("--format", default="json")

    graph_p = k_sub.add_parser("graph", help="Traverse knowledge graph")
    graph_p.add_argument("--tenant-id", required=True, help="Tenant ID")
    graph_p.add_argument("--start-node-id", required=True, help="Start node ID")
    graph_p.add_argument("--depth", type=int, default=2, help="Depth")
    graph_p.add_argument("--format", default="json")

    con_p = k_sub.add_parser("contradictions", help="List contradictions")
    con_p.add_argument("--tenant-id", required=True, help="Tenant ID")
    con_p.add_argument("--format", default="json")

    rec_p = k_sub.add_parser("recommend", help="Create recommendation")
    rec_p.add_argument("--tenant-id", required=True, help="Tenant ID")
    rec_p.add_argument("--target-id", required=True, help="Target ID")
    rec_p.add_argument("--title", required=True, help="Recommendation title")
    rec_p.add_argument("--rationale", required=True, help="Rationale")
    rec_p.add_argument("--format", default="json")

    mem_p = k_sub.add_parser("memory", help="Record organizational memory")
    mem_p.add_argument("--tenant-id", required=True, help="Tenant ID")
    mem_p.add_argument("--key", required=True, help="Memory key")
    mem_p.add_argument("--value", required=True, help="Value summary")
    mem_p.add_argument("--format", default="json")

    analytics_p = k_sub.add_parser("analytics", help="Get analytics report")
    analytics_p.add_argument("--tenant-id", required=True, help="Tenant ID")
    analytics_p.add_argument("--format", default="json")


def handle_knowledge_command(args: argparse.Namespace) -> None:
    if args.command == "register":
        item = knowledge_manager.knowledge_manager.register_knowledge(args.tenant_id, args.title)
        format_output(item.model_dump(), args.format)
    elif args.command == "retrieve":
        from app.knowledge_intelligence.retrieval import KnowledgeRetrievalRequest
        req = KnowledgeRetrievalRequest(tenant_id=args.tenant_id, query=args.query)
        candidates = knowledge_manager.knowledge_manager.list_knowledge(args.tenant_id)
        res = knowledge_manager.retrieval_manager.plan_and_retrieve(req, candidates)
        format_output(res.model_dump(), args.format)
    elif args.command == "provenance":
        chain = knowledge_manager.provenance_manager.get_provenance_chain(args.target_id, args.tenant_id)
        format_output(chain.model_dump(), args.format)
    elif args.command == "graph":
        trav = knowledge_manager.graph_manager.traverse(args.tenant_id, args.start_node_id, depth=args.depth)
        format_output(trav.model_dump(), args.format)
    elif args.command == "contradictions":
        cons = knowledge_manager.contradiction_manager.list_contradictions(args.tenant_id)
        format_output({"contradictions": [c.model_dump() for c in cons]}, args.format)
    elif args.command == "recommend":
        rec = knowledge_manager.recommendation_engine.create_recommendation(args.tenant_id, args.target_id, args.title, args.rationale)
        format_output(rec.model_dump(), args.format)
    elif args.command == "memory":
        mem = knowledge_manager.memory_manager.record_memory(args.tenant_id, args.key, args.value)
        format_output(mem.model_dump(), args.format)
    elif args.command == "analytics":
        items = knowledge_manager.knowledge_manager.list_knowledge(args.tenant_id)
        cons = knowledge_manager.contradiction_manager.list_contradictions(args.tenant_id)
        report = knowledge_manager.analytics_engine.generate_report(args.tenant_id, len(items), 0, len(cons))
        format_output(report.model_dump(), args.format)
