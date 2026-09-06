"""CLI commands for Knowledge Assurance platform."""

import json
import click
from app.knowledge_assurance.manager import KnowledgeAssuranceManager

_mgr = KnowledgeAssuranceManager()


def add_knowledge_parser(subparsers):
    parser = subparsers.add_parser("knowledge", help="Manage Knowledge Assurance")
    parser.set_defaults(func=handle_knowledge_command)
    return parser


def handle_knowledge_command(args):
    print("Knowledge command handled.")


@click.group(name="knowledge")
def knowledge_cli():
    """Manage Enterprise AI Knowledge Assurance, Trust, and Context operations."""
    pass


@knowledge_cli.command(name="references")
@click.option("--tenant-id", default="default_tenant", help="Tenant ID")
def references_cmd(tenant_id: str):
    """List knowledge references for a tenant."""
    refs = _mgr.references_manager.list_references(tenant_id)
    click.echo(json.dumps([r.model_dump() for r in refs], indent=2, default=str))


@knowledge_cli.command(name="sources")
@click.option("--tenant-id", default="default_tenant", help="Tenant ID")
def sources_cmd(tenant_id: str):
    """List knowledge sources for a tenant."""
    sources = _mgr.sources_manager.list_sources(tenant_id)
    click.echo(json.dumps([s.model_dump() for s in sources], indent=2, default=str))


@knowledge_cli.command(name="context")
@click.option("--tenant-id", default="default_tenant", help="Tenant ID")
def context_cmd(tenant_id: str):
    """List knowledge contexts for a tenant."""
    ctxs = _mgr.context_manager.list_contexts(tenant_id)
    click.echo(json.dumps([c.model_dump() for c in ctxs], indent=2, default=str))


@knowledge_cli.command(name="trust")
@click.argument("target_resource_id")
@click.option("--tenant-id", default="default_tenant", help="Tenant ID")
def trust_cmd(target_resource_id: str, tenant_id: str):
    """Evaluate knowledge trust score for a resource."""
    trust = _mgr.trust_engine.evaluate_trust(tenant_id, target_resource_id)
    click.echo(json.dumps(trust.model_dump(), indent=2, default=str))


@knowledge_cli.command(name="conflicts")
@click.option("--tenant-id", default="default_tenant", help="Tenant ID")
def conflicts_cmd(tenant_id: str):
    """List knowledge conflicts for a tenant."""
    conflicts = _mgr.conflict_manager.list_conflicts(tenant_id)
    click.echo(json.dumps([c.model_dump() for c in conflicts], indent=2, default=str))


@knowledge_cli.command(name="freshness")
@click.argument("target_resource_id")
@click.option("--tenant-id", default="default_tenant", help="Tenant ID")
def freshness_cmd(target_resource_id: str, tenant_id: str):
    """Evaluate knowledge freshness for a resource."""
    freshness = _mgr.freshness_manager.evaluate_freshness(tenant_id, target_resource_id)
    click.echo(json.dumps(freshness.model_dump(), indent=2, default=str))


@knowledge_cli.command(name="assurance")
@click.argument("target_resource_id")
@click.option("--tenant-id", default="default_tenant", help="Tenant ID")
def assurance_cmd(target_resource_id: str, tenant_id: str):
    """Evaluate holistic knowledge assurance for a resource."""
    ass = _mgr.assurance_manager.assess_knowledge_assurance(tenant_id, target_resource_id)
    click.echo(json.dumps(ass.model_dump(), indent=2, default=str))
