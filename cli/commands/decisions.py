"""CLI Commands for Phase 5.52 Enterprise AI Decision Intelligence Platform."""

import sys
import json
import click
from app.decision_intelligence.manager import DecisionIntelligenceManager
from app.decision_intelligence.decisions import DecisionLifecycleState, DecisionType


@click.group(name="decisions")
def decisions_cli():
    """Manage Enterprise AI Decision Intelligence platform operations."""
    pass


@decisions_cli.command(name="create")
@click.option("--tenant-id", default="default", help="Tenant ID")
@click.option("--title", required=True, help="Decision title")
@click.option("--type", "decision_type", default="CROSS_DOMAIN", help="Decision type")
def create_decision(tenant_id: str, title: str, decision_type: str):
    """Create a new decision request."""
    mgr = DecisionIntelligenceManager()
    dtype = DecisionType(decision_type) if decision_type in DecisionType.__members__ else DecisionType.CROSS_DOMAIN
    dec = mgr.decision_manager.create_decision(tenant_id, title, dtype)
    click.echo(json.dumps(dec.model_dump(), indent=2, default=str))


@decisions_cli.command(name="flow")
@click.option("--tenant-id", default="default", help="Tenant ID")
@click.option("--title", default="Enterprise Architecture Modernization", help="Flow title")
def run_flow(tenant_id: str, title: str):
    """Run full end-to-end decision intelligence flow."""
    mgr = DecisionIntelligenceManager()
    result = mgr.run_full_decision_flow(tenant_id=tenant_id, title=title)
    click.echo(json.dumps(result, indent=2, default=str))


@decisions_cli.command(name="reproducibility")
@click.option("--tenant-id", default="default", help="Tenant ID")
@click.option("--decision-id", required=True, help="Decision ID")
def get_reproducibility(tenant_id: str, decision_id: str):
    """Retrieve decision reproducibility record and verify integrity."""
    mgr = DecisionIntelligenceManager()
    rec = mgr.reproducibility_engine.get_reproducibility_record(decision_id, tenant_id)
    is_valid = mgr.reproducibility_engine.verify_reproducibility(decision_id, tenant_id)
    out = rec.model_dump()
    out["integrity_valid"] = is_valid
    click.echo(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    decisions_cli()
