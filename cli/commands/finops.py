"""CLI Commands for FinOps Intelligence Platform (Phase 5.42)."""

import click
from typing import Optional
from app.finops_intelligence.manager import FinOpsIntelligenceManager

_mgr = FinOpsIntelligenceManager()


@click.group(name="finops")
def finops_cli():
    """CLI for Enterprise AI FinOps Intelligence Platform."""
    pass


@finops_cli.command(name="costs")
@click.option("--tenant-id", default="global", help="Tenant Identifier")
def list_costs(tenant_id: str):
    """List recorded costs for tenant."""
    costs = _mgr.cost_repo.list(tenant_id)
    click.echo(f"Found {len(costs)} cost records for tenant '{tenant_id}':")
    for c in costs:
        click.echo(f" - [{c.record_id}] {c.category.value}: ${c.amount_usd:.2f}")


@finops_cli.command(name="usage")
@click.option("--tenant-id", default="global", help="Tenant Identifier")
def get_usage(tenant_id: str):
    """Get usage telemetry summary for tenant."""
    asm = _mgr.usage_manager.evaluate_usage(tenant_id)
    click.echo(f"Usage summary for tenant '{tenant_id}':")
    click.echo(f" - Total Tokens: {asm.total_tokens}")
    click.echo(f" - Total API Calls: {asm.total_api_calls}")
    click.echo(f" - Total Execution Time (ms): {asm.total_execution_ms}")


@finops_cli.command(name="budgets")
@click.option("--tenant-id", default="global", help="Tenant Identifier")
def list_budgets(tenant_id: str):
    """List active budgets for tenant."""
    budgets = _mgr.budget_repo.list(tenant_id)
    click.echo(f"Found {len(budgets)} budgets for tenant '{tenant_id}':")
    for b in budgets:
        click.echo(f" - [{b.budget_id}] {b.name}: ${b.current_spend_usd:.2f} / ${b.amount_usd:.2f} (Status: {b.status.value})")


@finops_cli.command(name="forecast")
@click.option("--tenant-id", default="global", help="Tenant Identifier")
def get_forecast(tenant_id: str):
    """Generate spending forecast for tenant."""
    fcst = _mgr.forecast_manager.generate_forecast(tenant_id, [500.0, 600.0, 750.0])
    click.echo(f"Forecast for tenant '{tenant_id}': ${fcst.projected_spend_usd:.2f} ({fcst.confidence.value} confidence)")


@finops_cli.command(name="anomalies")
@click.option("--tenant-id", default="global", help="Tenant Identifier")
def list_anomalies(tenant_id: str):
    """List financial cost anomalies for tenant."""
    anomalies = _mgr.anomaly_manager.list_anomalies(tenant_id)
    click.echo(f"Found {len(anomalies)} cost anomalies for tenant '{tenant_id}':")
    for a in anomalies:
        click.echo(f" - [{a.anomaly_id}] {a.anomaly_type.value}: Expected ${a.expected_amount_usd:.2f}, Actual ${a.actual_amount_usd:.2f} (+{a.deviation_pct:.1f}%)")


@finops_cli.command(name="optimize")
@click.option("--tenant-id", default="global", help="Tenant Identifier")
def list_optimizations(tenant_id: str):
    """List optimization recommendations for tenant."""
    recs = _mgr.optimization_repo.list(tenant_id)
    click.echo(f"Found {len(recs)} optimization recommendations for tenant '{tenant_id}':")
    for r in recs:
        click.echo(f" - [{r.optimization_id}] {r.optimization_type.value}: Save ${r.estimated_monthly_savings_usd:.2f}/mo (Status: {r.status.value})")


@finops_cli.command(name="analytics")
@click.option("--tenant-id", default="global", help="Tenant Identifier")
def get_analytics(tenant_id: str):
    """Get financial analytics report for tenant."""
    rpt = _mgr.analytics_engine.generate_report(tenant_id)
    click.echo(f"Analytics report for tenant '{tenant_id}': {len(rpt.metrics)} metrics, {len(rpt.insights)} insights.")
