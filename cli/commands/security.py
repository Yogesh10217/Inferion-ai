"""CLI commands for Security Assurance platform."""

import json
import click
from app.security_assurance.manager import SecurityAssuranceManager
from app.security_assurance.assets import SecurityAssetType, SecurityCriticality

_mgr = SecurityAssuranceManager()


@click.group(name="security")
def security_cli():
    """Manage Enterprise AI Security Intelligence, Threat Detection, and Security Assurance."""
    pass


@security_cli.command(name="register")
@click.option("--tenant-id", default="default_tenant", help="Tenant ID")
@click.option("--name", required=True, help="Asset Name")
@click.option("--type", default="AI_MODEL", help="Asset Type")
def register_cmd(tenant_id: str, name: str, type: str):
    """Register a security-monitored asset."""
    asset = _mgr.register_asset(
        tenant_id=tenant_id,
        name=name,
        asset_type=SecurityAssetType(type),
    )
    click.echo(json.dumps(asset.model_dump(), indent=2, default=str))


@security_cli.command(name="assets")
@click.option("--tenant-id", default="default_tenant", help="Tenant ID")
def assets_cmd(tenant_id: str):
    """List monitored security assets for tenant."""
    assets = _mgr.asset_inventory.list_assets(tenant_id)
    if not assets:
        asset = _mgr.register_asset(tenant_id=tenant_id, name="default-model", asset_type=SecurityAssetType.AI_MODEL)
        assets = [asset]
    click.echo(json.dumps([a.model_dump() for a in assets], indent=2, default=str))


@security_cli.command(name="posture")
@click.option("--tenant-id", default="default_tenant", help="Tenant ID")
def posture_cmd(tenant_id: str):
    """Evaluate enterprise security posture grade and score."""
    posture = _mgr.evaluate_posture(tenant_id)
    click.echo(json.dumps(posture.model_dump(), indent=2, default=str))


@security_cli.command(name="threats")
@click.option("--tenant-id", default="default_tenant", help="Tenant ID")
def threats_cmd(tenant_id: str):
    """List active threats for tenant."""
    threats = _mgr.threat_store.list_threats(tenant_id)
    click.echo(json.dumps([t.model_dump() for t in threats], indent=2, default=str))


@security_cli.command(name="incidents")
@click.option("--tenant-id", default="default_tenant", help="Tenant ID")
def incidents_cmd(tenant_id: str):
    """List security incidents for tenant."""
    incs = _mgr.incident_manager.list_incidents(tenant_id)
    click.echo(json.dumps([i.model_dump() for i in incs], indent=2, default=str))


@security_cli.command(name="assurance")
@click.option("--tenant-id", default="default_tenant", help="Tenant ID")
def assurance_cmd(tenant_id: str):
    """Evaluate overall security assurance score."""
    score = _mgr.evaluate_assurance(tenant_id)
    click.echo(json.dumps(score.model_dump(), indent=2, default=str))


@security_cli.command(name="analytics")
@click.option("--tenant-id", default="default_tenant", help="Tenant ID")
def analytics_cmd(tenant_id: str):
    """Generate security analytics report."""
    report = _mgr.analytics_engine.generate_report(tenant_id)
    click.echo(json.dumps(report.model_dump(), indent=2, default=str))
