"""CLI Command Group for Enterprise AI Portfolio Platform."""

import sys
import json
import click

from app.portfolio_platform.manager import PortfolioPlatformManager
from app.portfolio_platform.strategy import StrategyHorizon
from app.portfolio_platform.investment import InvestmentRisk

mgr = PortfolioPlatformManager()


@click.group(name="portfolio")
def portfolio_cli():
    """Manage Enterprise AI Portfolio, Strategy, Value & Investment Governance."""
    pass


@portfolio_cli.group(name="strategies")
def strategies_cli():
    """Manage enterprise strategies."""
    pass


@strategies_cli.command(name="list")
@click.option("--tenant-id", default="global", help="Tenant ID.")
def list_strategies(tenant_id: str):
    """List enterprise strategies."""
    strats = mgr.strategy_manager.list_strategies(tenant_id)
    click.echo(json.dumps([s.model_dump() for s in strats], indent=2, default=str))


@portfolio_cli.group(name="initiatives")
def initiatives_cli():
    """Manage AI initiatives."""
    pass


@initiatives_cli.command(name="list")
@click.option("--tenant-id", default="global", help="Tenant ID.")
def list_initiatives(tenant_id: str):
    """List AI initiatives."""
    inits = mgr.initiative_manager.list_initiatives(tenant_id)
    click.echo(json.dumps([i.model_dump() for i in inits], indent=2, default=str))


@portfolio_cli.command(name="prioritize")
@click.option("--tenant-id", default="global", help="Tenant ID.")
def prioritize_portfolio(tenant_id: str):
    """Prioritize portfolio initiatives."""
    inits = mgr.initiative_manager.list_initiatives(tenant_id)
    bcs = [mgr.business_case_manager.get_by_initiative(i.initiative_id, tenant_id) for i in inits]
    valid_bcs = [b for b in bcs if b is not None]

    res = mgr.prioritization_engine.score_initiatives(tenant_id, inits, valid_bcs)
    click.echo(json.dumps(res.model_dump(), indent=2, default=str))


@portfolio_cli.command(name="optimize")
@click.option("--tenant-id", default="global", help="Tenant ID.")
def optimize_portfolio(tenant_id: str):
    """Multi-objective portfolio optimization."""
    inits = mgr.initiative_manager.list_initiatives(tenant_id)
    bcs = [mgr.business_case_manager.get_by_initiative(i.initiative_id, tenant_id) for i in inits]
    valid_bcs = [b for b in bcs if b is not None]

    prio = mgr.prioritization_engine.score_initiatives(tenant_id, inits, valid_bcs)
    opt = mgr.optimization_engine.optimize_portfolio(tenant_id, prio, valid_bcs)
    click.echo(json.dumps(opt.model_dump(), indent=2, default=str))


@portfolio_cli.group(name="investments")
def investments_cli():
    """Manage investment proposals."""
    pass


@investments_cli.command(name="list")
@click.option("--tenant-id", default="global", help="Tenant ID.")
def list_investments(tenant_id: str):
    """List portfolio investments."""
    report = mgr.analytics_engine.generate_report(tenant_id)
    click.echo(json.dumps(report.model_dump(), indent=2, default=str))


@portfolio_cli.command(name="funding")
@click.option("--tenant-id", default="global", help="Tenant ID.")
def get_funding(tenant_id: str):
    """Get budget envelope and funding allocations."""
    env = mgr.funding_manager.get_budget_envelope(tenant_id)
    allocs = mgr.funding_manager.list_allocations(tenant_id)
    click.echo(json.dumps({"envelope": env.model_dump(), "allocations": [a.model_dump() for a in allocs]}, indent=2, default=str))


@portfolio_cli.command(name="analytics")
@click.option("--tenant-id", default="global", help="Tenant ID.")
def get_analytics(tenant_id: str):
    """Get portfolio analytics report."""
    report = mgr.analytics_engine.generate_report(tenant_id)
    click.echo(json.dumps(report.model_dump(), indent=2, default=str))
