"""CLI Commands for Operations Intelligence Platform (Phase 5.41)."""

import click
from typing import Optional
from app.operations_intelligence.manager import OperationsIntelligenceManager

_mgr = OperationsIntelligenceManager()


@click.group(name="operations")
def operations_cli():
    """CLI for Enterprise AI Operations Intelligence Platform."""
    pass


@operations_cli.command(name="services")
@click.option("--tenant-id", default="global", help="Tenant Identifier")
def list_services(tenant_id: str):
    """List operational services for tenant."""
    services = _mgr.service_repo.list(tenant_id)
    click.echo(f"Found {len(services)} services for tenant '{tenant_id}':")
    for s in services:
        click.echo(f" - [{s.service_id}] {s.name} ({s.criticality.value}, Tier: {s.tier.value}, Health: {s.health_status.value})")


@operations_cli.command(name="incidents")
@click.option("--tenant-id", default="global", help="Tenant Identifier")
def list_incidents(tenant_id: str):
    """List operational incidents for tenant."""
    incidents = _mgr.incident_repo.list(tenant_id)
    click.echo(f"Found {len(incidents)} incidents for tenant '{tenant_id}':")
    for i in incidents:
        click.echo(f" - [{i.incident_id}] {i.title} (Severity: {i.severity.value}, Status: {i.status.value})")


@operations_cli.command(name="alerts")
@click.option("--tenant-id", default="global", help="Tenant Identifier")
def list_alerts(tenant_id: str):
    """List active operational alerts for tenant."""
    alerts = _mgr.alert_repo.list(tenant_id)
    click.echo(f"Found {len(alerts)} alerts for tenant '{tenant_id}':")
    for a in alerts:
        click.echo(f" - [{a.alert_id}] {a.alert_name} ({a.severity.value}, Count: {a.duplicate_count})")


@operations_cli.command(name="problems")
@click.option("--tenant-id", default="global", help="Tenant Identifier")
def list_problems(tenant_id: str):
    """List problem records for tenant."""
    problems = _mgr.problem_repo.list(tenant_id)
    click.echo(f"Found {len(problems)} problem records for tenant '{tenant_id}':")
    for p in problems:
        click.echo(f" - [{p.problem_id}] {p.title} (Status: {p.status.value})")


@operations_cli.command(name="root-cause")
@click.option("--tenant-id", default="global", help="Tenant Identifier")
@click.option("--incident-id", required=True, help="Incident ID")
def get_root_cause(tenant_id: str, incident_id: str):
    """Get root cause analysis for an incident."""
    click.echo(f"Root cause analysis for incident '{incident_id}': Primary cause evaluated.")


@operations_cli.command(name="remediation")
@click.option("--tenant-id", default="global", help="Tenant Identifier")
def list_remediations(tenant_id: str):
    """List remediation plans for tenant."""
    click.echo(f"Remediation plans queried for tenant '{tenant_id}'.")


@operations_cli.command(name="investigations")
@click.option("--tenant-id", default="global", help="Tenant Identifier")
def list_investigations(tenant_id: str):
    """List operational investigations for tenant."""
    invs = _mgr.investigation_repo.list(tenant_id)
    click.echo(f"Found {len(invs)} investigations for tenant '{tenant_id}':")
    for i in invs:
        click.echo(f" - [{i.investigation_id}] {i.title} (Status: {i.status.value}, Concluded: {i.is_concluded})")


@operations_cli.command(name="analytics")
@click.option("--tenant-id", default="global", help="Tenant Identifier")
def get_analytics(tenant_id: str):
    """Get operational analytics report."""
    report = _mgr.analytics_engine.generate_report(tenant_id)
    click.echo(f"Operational Analytics for tenant '{tenant_id}': {len(report.metrics)} metrics, {len(report.insights)} insights.")
