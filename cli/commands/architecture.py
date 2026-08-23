"""CLI Commands for Enterprise AI Architecture & Digital Twin Platform (Phase 5.26)."""

import click
import json
from app.architecture_platform.manager import ArchitecturePlatformManager
from app.architecture_platform.nodes import ArchitectureNodeType

mgr = ArchitecturePlatformManager()


@click.group(name="architecture")
def architecture_cli():
    """Enterprise AI Architecture & Digital Twin CLI."""
    pass


@architecture_cli.group(name="nodes")
def nodes_group():
    """Manage architecture nodes."""
    pass


@nodes_group.command(name="list")
@click.option("--tenant-id", default="global", help="Tenant ID")
@click.option("--environment", default=None, help="Environment")
def list_nodes(tenant_id: str, environment: str):
    """List architecture nodes."""
    nodes = mgr.node_manager.list_nodes(tenant_id=tenant_id, environment=environment)
    click.echo(json.dumps([n.model_dump() for n in nodes], indent=2, default=str))


@architecture_cli.command(name="topology")
@click.option("--tenant-id", default="global", help="Tenant ID")
@click.option("--environment", default="production", help="Environment")
def get_topology(tenant_id: str, environment: str):
    """View architecture topology graph."""
    top = mgr.topology_manager.build_topology(tenant_id=tenant_id, environment=environment)
    click.echo(json.dumps(top.model_dump(), indent=2, default=str))


@architecture_cli.command(name="snapshot")
@click.option("--tenant-id", default="global", help="Tenant ID")
@click.option("--environment", default="production", help="Environment")
def create_snapshot(tenant_id: str, environment: str):
    """Create immutable topology snapshot."""
    snap = mgr.topology_manager.create_snapshot(tenant_id=tenant_id, environment=environment)
    click.echo(json.dumps(snap.model_dump(), indent=2, default=str))


@architecture_cli.command(name="drift")
@click.option("--tenant-id", default="global", help="Tenant ID")
def list_drift(tenant_id: str):
    """List architecture drift records."""
    drifts = mgr.drift_detector.list_drifts(tenant_id=tenant_id)
    click.echo(json.dumps([d.model_dump() for d in drifts], indent=2, default=str))


@architecture_cli.command(name="impact")
@click.option("--tenant-id", default="global", help="Tenant ID")
@click.option("--target-node-id", required=True, help="Target Node ID")
def analyze_impact(tenant_id: str, target_node_id: str):
    """Analyze change impact and blast radius."""
    impact = mgr.impact_analyzer.analyze_impact(tenant_id=tenant_id, target_node_id=target_node_id)
    click.echo(json.dumps(impact.model_dump(), indent=2, default=str))


@architecture_cli.command(name="trust")
@click.option("--tenant-id", default="global", help="Tenant ID")
def get_trust(tenant_id: str):
    """View tenant Architecture Trust Score."""
    trust = mgr.trust_engine.get_trust_score(tenant_id=tenant_id)
    click.echo(json.dumps(trust.model_dump(), indent=2, default=str))
