"""CLI Command Group for Enterprise AI Decision Intelligence Platform."""

import sys
import json
import click

from app.decision_intelligence.manager import DecisionIntelligenceManager
from app.decision_intelligence.context import DecisionContextType
from app.decision_intelligence.scenarios import ScenarioType

mgr = DecisionIntelligenceManager()


@click.group(name="decisions")
def decisions_cli():
    """Manage Enterprise AI Decision Intelligence, Scenario Planning & Governance."""
    pass


@decisions_cli.command(name="context")
@click.option("--tenant-id", default="global", help="Tenant ID.")
@click.option("--title", default="AI Context", help="Context title.")
def create_context(tenant_id: str, title: str):
    """Assemble decision context."""
    ctx = mgr.context_builder.assemble_context(tenant_id, title, "Assembled context via CLI.")
    res = mgr.context_manager.create_context(ctx)
    click.echo(json.dumps(res.model_dump(), indent=2, default=str))


@decisions_cli.command(name="analyze")
@click.option("--tenant-id", default="global", help="Tenant ID.")
@click.option("--title", default="CLI Decision Analysis", help="Decision title.")
def analyze_decision(tenant_id: str, title: str):
    """Run full end-to-end decision flow analysis."""
    flow = mgr.run_full_decision_flow(tenant_id=tenant_id, title=title)
    click.echo(json.dumps(flow, indent=2, default=str))


@decisions_cli.command(name="recommend")
@click.option("--tenant-id", default="global", help="Tenant ID.")
def generate_recommendation(tenant_id: str):
    """Generate decision recommendation."""
    flow = mgr.run_full_decision_flow(tenant_id=tenant_id, title="CLI Recommendation")
    click.echo(json.dumps(flow["recommendation"], indent=2, default=str))


@decisions_cli.command(name="scenario")
@click.option("--tenant-id", default="global", help="Tenant ID.")
@click.option("--title", default="Cost-Optimized Scenario", help="Scenario title.")
def simulate_scenario(tenant_id: str, title: str):
    """Simulate non-mutating decision scenario."""
    ctx = mgr.context_builder.assemble_context(tenant_id, title, "Desc")
    scen = mgr.scenario_manager.create_scenario(tenant_id, ctx.context_id, title, ScenarioType.COST_OPTIMIZED)
    sim = mgr.scenario_manager.simulate_scenario(scen.scenario_id, tenant_id)
    click.echo(json.dumps(sim.model_dump(), indent=2, default=str))


@decisions_cli.command(name="analytics")
@click.option("--tenant-id", default="global", help="Tenant ID.")
def get_analytics(tenant_id: str):
    """Get decision analytics report."""
    report = mgr.analytics_engine.generate_report(tenant_id)
    click.echo(json.dumps(report.model_dump(), indent=2, default=str))
