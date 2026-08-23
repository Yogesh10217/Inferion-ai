"""CLI Commands for Enterprise Intelligence Platform."""

import click
import json
from app.intelligence_platform.manager import EnterpriseIntelligenceManager
from app.intelligence_platform.signals import SignalSource, SignalType
from app.intelligence_platform.forecasting import ForecastType, ForecastHorizon
from app.intelligence_platform.simulation import SimulationScenario, SimulationInput
from app.intelligence_platform.recommendations import RecommendationType

mgr = EnterpriseIntelligenceManager()


@click.group(name="intelligence")
def intelligence_cli():
    """Manage Enterprise AI Intelligence, Decisions, Recommendations, and Simulations."""
    pass


@intelligence_cli.command(name="signal")
@click.option("--source", required=True, help="Signal Source")
@click.option("--type", required=True, help="Signal Type")
@click.option("--message", required=True, help="Message text")
@click.option("--tenant-id", default="global", help="Tenant ID")
def send_signal(source, type, message, tenant_id):
    """Ingest intelligence signal."""
    sig = mgr.signal_manager.ingest_signal(
        tenant_id=tenant_id,
        source=SignalSource(source),
        signal_type=SignalType(type),
        message=message,
    )
    click.echo(f"Ingested intelligence signal '{sig.signal_id}'")


@intelligence_cli.command(name="analyze")
@click.option("--resource-id", default="res_1", help="Target Resource ID")
@click.option("--tenant-id", default="global", help="Tenant ID")
def run_analyze(resource_id, tenant_id):
    """Analyze context and generate insight."""
    signals = mgr.signal_manager.list_signals(tenant_id, resource_id=resource_id)
    ctx = mgr.context_builder.assemble_context(tenant_id, primary_resource_id=resource_id, signals=signals)
    ins = mgr.insight_manager.generate_insight_from_context(
        tenant_id=tenant_id,
        insight_type="OPERATIONAL",
        observation=f"Resource '{resource_id}' evaluated.",
        recommended_next_step="Maintain parameters",
        context=ctx,
    )
    click.echo(json.dumps(ins.model_dump(mode="json"), indent=2))


@intelligence_cli.command(name="insights")
@click.option("--tenant-id", default="global", help="Tenant ID")
def list_insights(tenant_id):
    """List intelligence insights."""
    insights = mgr.insight_manager.list_insights(tenant_id)
    click.echo(json.dumps([i.model_dump(mode="json") for i in insights], indent=2))


@intelligence_cli.command(name="forecast")
@click.option("--resource-id", required=True, help="Target resource ID")
@click.option("--type", default="INCIDENT_RISK_FORECAST", help="Forecast type")
@click.option("--tenant-id", default="global", help="Tenant ID")
def run_forecast(resource_id, type, tenant_id):
    """Generate predictive forecast."""
    signals = mgr.signal_manager.list_signals(tenant_id, resource_id=resource_id)
    ctx = mgr.context_builder.assemble_context(tenant_id, primary_resource_id=resource_id, signals=signals)
    fc = mgr.forecast_engine.forecast(tenant_id, resource_id, ForecastType(type), ctx)
    click.echo(json.dumps(fc.model_dump(mode="json"), indent=2))


@intelligence_cli.command(name="simulate")
@click.option("--resource-id", required=True, help="Target resource ID")
@click.option("--scenario", default="WHAT_IF", help="Scenario type")
@click.option("--action", default="ROLLBACK", help="Action type")
@click.option("--tenant-id", default="global", help="Tenant ID")
def run_simulate(resource_id, scenario, action, tenant_id):
    """Run non-production scenario simulation."""
    signals = mgr.signal_manager.list_signals(tenant_id, resource_id=resource_id)
    ctx = mgr.context_builder.assemble_context(tenant_id, primary_resource_id=resource_id, signals=signals)
    sim_in = SimulationInput(scenario_name=scenario, target_resource_id=resource_id, action_type=action)
    sim = mgr.simulation_engine.simulate(tenant_id, SimulationScenario(scenario), sim_in, ctx)
    click.echo(json.dumps(sim.model_dump(mode="json"), indent=2))


@intelligence_cli.command(name="recommend")
@click.option("--resource-id", required=True, help="Target resource ID")
@click.option("--type", default="ROLLBACK_DEPLOYMENT", help="Recommendation type")
@click.option("--title", default="Recommend Rollback", help="Title")
@click.option("--tenant-id", default="global", help="Tenant ID")
def run_recommend(resource_id, type, title, tenant_id):
    """Generate actionable recommendation."""
    rec = mgr.recommendation_manager.create_recommendation(
        tenant_id=tenant_id,
        recommendation_type=RecommendationType(type),
        title=title,
        action_description="Actionable recommendation description",
        target_resource_id=resource_id,
        expected_impact="Risk reduction",
    )
    click.echo(f"Created recommendation '{rec.recommendation_id}' ({rec.status.value})")


@intelligence_cli.command(name="decisions")
@click.option("--tenant-id", default="global", help="Tenant ID")
def list_decisions(tenant_id):
    """List intelligence decisions."""
    decisions = mgr.decision_manager.list_decisions(tenant_id)
    click.echo(json.dumps([d.model_dump(mode="json") for d in decisions], indent=2))
