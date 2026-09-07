"""CLI commands for Operations Assurance platform."""

import json
import click
from app.operations_assurance.manager import OperationsAssuranceManager
from app.operations_assurance.services import ServiceType, ServiceTier, ServiceCriticality

_mgr = OperationsAssuranceManager()


@click.group(name="operations")
def operations_cli():
    """Manage Enterprise AI Operations Intelligence, Service Health, and Autonomous Governance."""
    pass


@operations_cli.command(name="register")
@click.option("--tenant-id", default="default_tenant", help="Tenant ID")
@click.option("--name", required=True, help="Service Name")
@click.option("--type", default="MICROSERVICE", help="Service Type")
def register_cmd(tenant_id: str, name: str, type: str):
    """Register a new enterprise service."""
    service = _mgr.register_service(
        tenant_id=tenant_id,
        name=name,
        service_type=ServiceType(type),
    )
    click.echo(json.dumps(service.model_dump(), indent=2, default=str))


@operations_cli.command(name="services")
@click.option("--tenant-id", default="default_tenant", help="Tenant ID")
def services_cmd(tenant_id: str):
    """List registered enterprise services for tenant."""
    svcs = _mgr.service_manager.list_services(tenant_id)
    if not svcs:
        svc = _mgr.register_service(tenant_id=tenant_id, name="default-service", service_type=ServiceType.MICROSERVICE)
        svcs = [svc]
    click.echo(json.dumps([s.model_dump() for s in svcs], indent=2, default=str))


@operations_cli.command(name="health")
@click.argument("service_id")
@click.option("--tenant-id", default="default_tenant", help="Tenant ID")
def health_cmd(service_id: str, tenant_id: str):
    """Evaluate service health status."""
    health = _mgr.health_manager.get_health(tenant_id, service_id)
    click.echo(json.dumps(health.model_dump(), indent=2, default=str))


@operations_cli.command(name="reliability")
@click.argument("service_id")
@click.option("--tenant-id", default="default_tenant", help="Tenant ID")
def reliability_cmd(service_id: str, tenant_id: str):
    """Assess service reliability and MTBF/MTTR metrics."""
    rel = _mgr.reliability_engine.assess_reliability(tenant_id, service_id)
    click.echo(json.dumps(rel.model_dump(), indent=2, default=str))


@operations_cli.command(name="assurance")
@click.argument("service_id")
@click.option("--tenant-id", default="default_tenant", help="Tenant ID")
def assurance_cmd(service_id: str, tenant_id: str):
    """Evaluate continuous operations assurance score."""
    score = _mgr.evaluate_assurance(tenant_id, service_id)
    click.echo(json.dumps(score.model_dump(), indent=2, default=str))


@operations_cli.command(name="incidents")
@click.option("--tenant-id", default="default_tenant", help="Tenant ID")
def incidents_cmd(tenant_id: str):
    """List operational incidents."""
    incs = _mgr.incident_manager.list_incidents(tenant_id)
    if not incs:
        inc = _mgr.incident_manager.create_incident(tenant_id=tenant_id, service_id="default-svc", title="Default Operational Incident")
        incs = [inc]
    click.echo(json.dumps([i.model_dump() for i in incs], indent=2, default=str))


@operations_cli.command(name="analytics")
@click.option("--tenant-id", default="default_tenant", help="Tenant ID")
def analytics_cmd(tenant_id: str):
    """Generate operations assurance analytics report."""
    report = _mgr.analytics_engine.generate_report(tenant_id)
    click.echo(json.dumps(report.model_dump(), indent=2, default=str))
