"""CLI Commands for Enterprise AI Reliability Platform (Phase 5.31)."""

import click
import json
from app.reliability_platform.manager import ReliabilityPlatformManager


@click.group(name="reliability")
def reliability_cli():
    """Enterprise AI Reliability Platform CLI Commands."""
    pass


@reliability_cli.command(name="register-service")
@click.option("--tenant-id", required=True, help="Tenant ID")
@click.option("--name", required=True, help="Service Name")
@click.option("--tier", default="TIER_1_HIGH", help="Service Tier")
def register_service(tenant_id: str, name: str, tier: str):
    """Register a service for reliability tracking."""
    mgr = ReliabilityPlatformManager()
    svc = mgr.service_manager.register_service(tenant_id=tenant_id, name=name, tier=tier)
    click.echo(json.dumps(svc.model_dump(), indent=2, default=str))


@reliability_cli.command(name="create-slo")
@click.option("--tenant-id", required=True, help="Tenant ID")
@click.option("--service-id", required=True, help="Service ID")
@click.option("--name", required=True, help="SLO Target Name")
@click.option("--target-pct", default=99.9, help="SLO Target Percentage")
def create_slo(tenant_id: str, service_id: str, name: str, target_pct: float):
    """Create an SLO definition."""
    mgr = ReliabilityPlatformManager()
    slo = mgr.slo_manager.create_slo(tenant_id=tenant_id, service_id=service_id, name=name, target_percentage=target_pct)
    click.echo(json.dumps(slo.model_dump(), indent=2, default=str))


@reliability_cli.command(name="report")
@click.option("--tenant-id", required=True, help="Tenant ID")
def get_report(tenant_id: str):
    """Generate reliability intelligence report."""
    mgr = ReliabilityPlatformManager()
    rep = mgr.analytics_engine.generate_report(tenant_id=tenant_id)
    click.echo(json.dumps(rep.model_dump(), indent=2, default=str))


if __name__ == "__main__":
    reliability_cli()
