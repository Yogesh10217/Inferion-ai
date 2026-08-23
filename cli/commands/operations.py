"""CLI Commands for Platform Operations."""

import click
import json
from app.platform_operations.manager import PlatformOperationsManager
from app.platform_operations.services import ServiceTier
from app.platform_operations.signals import SignalSource, SignalType, SignalSeverity
from app.platform_operations.slo import SLOType
from app.platform_operations.remediation import RemediationStep, RemediationStrategy
from app.governance_platform.risk import RiskLevel

mgr = PlatformOperationsManager()


@click.group(name="operations")
def operations_cli():
    """Manage Enterprise AI Platform Operations, Services, Remediations, SLOs, and Capacity."""
    pass


@operations_cli.group(name="services")
def services_group():
    """Manage operational service catalog."""
    pass


@services_group.command(name="list")
@click.option("--tenant-id", default="global", help="Tenant ID filter")
def list_services(tenant_id):
    """List services in catalog."""
    services = mgr.service_catalog_manager.list_services(tenant_id=tenant_id)
    click.echo(json.dumps([s.model_dump(mode="json") for s in services], indent=2))


@services_group.command(name="create")
@click.option("--name", required=True, help="Service name")
@click.option("--tenant-id", default="global", help="Tenant ID")
@click.option("--tier", default="TIER_1_HIGH", help="Service Tier")
def create_service(name, tenant_id, tier):
    """Register a new service in catalog."""
    svc = mgr.service_catalog_manager.register_service(
        tenant_id=tenant_id,
        name=name,
        service_tier=ServiceTier(tier),
    )
    click.echo(f"Created service '{svc.name}' ({svc.service_id})")


@operations_cli.group(name="signals")
def signals_group():
    """Manage operational signals."""
    pass


@signals_group.command(name="send")
@click.option("--source", required=True, help="Signal Source")
@click.option("--type", required=True, help="Signal Type")
@click.option("--message", required=True, help="Message text")
@click.option("--tenant-id", default="global", help="Tenant ID")
def send_signal(source, type, message, tenant_id):
    """Ingest operational signal."""
    sig = mgr.signal_manager.ingest_signal(
        tenant_id=tenant_id,
        source=SignalSource(source),
        signal_type=SignalType(type),
        message=message,
    )
    click.echo(f"Ingested signal '{sig.signal_id}'")


@operations_cli.group(name="incident")
def incident_group():
    """Incident context and root cause diagnosis."""
    pass


@incident_group.command(name="context")
@click.argument("incident_id")
@click.option("--tenant-id", default="global", help="Tenant ID")
def incident_context(incident_id, tenant_id):
    """Get enriched context for incident."""
    ctx = mgr.incident_intelligence_engine.get_incident_context(incident_id=incident_id, tenant_id=tenant_id)
    click.echo(json.dumps(ctx.model_dump(mode="json"), indent=2))


@incident_group.command(name="diagnose")
@click.argument("incident_id")
@click.option("--tenant-id", default="global", help="Tenant ID")
def incident_diagnose(incident_id, tenant_id):
    """Generate root cause diagnosis for incident."""
    ctx = mgr.incident_intelligence_engine.get_incident_context(incident_id=incident_id, tenant_id=tenant_id)
    diag = mgr.root_cause_analyzer.diagnose_incident(tenant_id=tenant_id, context=ctx)
    click.echo(json.dumps(diag.model_dump(mode="json"), indent=2))


@operations_cli.group(name="remediation")
def remediation_group():
    """Remediation planning, execution, and verification."""
    pass


@remediation_group.command(name="plan")
@click.option("--incident-id", required=True)
@click.option("--service-id", required=True)
@click.option("--strategy", default="ROLLBACK")
@click.option("--tenant-id", default="global")
def plan_remediation(incident_id, service_id, strategy, tenant_id):
    """Plan remediation action."""
    step = RemediationStep(
        strategy=RemediationStrategy(strategy),
        target_resource_id=service_id,
        action_description=f"Automated {strategy} action",
        expected_effect="Restore service health",
        risk_level=RiskLevel.MEDIUM,
    )
    plan = mgr.remediation_planner.create_remediation_plan(
        tenant_id=tenant_id,
        incident_id=incident_id,
        service_id=service_id,
        steps=[step],
    )
    click.echo(f"Created remediation plan '{plan.plan_id}' (Status: {plan.status.value})")


@remediation_group.command(name="execute")
@click.argument("plan_id")
@click.option("--tenant-id", default="global")
def execute_remediation(plan_id, tenant_id):
    """Execute approved remediation plan."""
    plan = mgr.remediation_planner.execute_remediation_plan(plan_id=plan_id, tenant_id=tenant_id)
    click.echo(f"Executed remediation plan '{plan_id}' (Status: {plan.status.value})")


@remediation_group.command(name="verify")
@click.argument("plan_id")
@click.option("--tenant-id", default="global")
def verify_remediation(plan_id, tenant_id):
    """Verify remediation health recovery."""
    verif = mgr.remediation_verifier.verify_remediation(tenant_id=tenant_id, plan_id=plan_id)
    click.echo(f"Verified remediation '{plan_id}': Passed={verif.is_verified}")


@operations_cli.group(name="slo")
def slo_group():
    """Manage SLO definitions."""
    pass


@slo_group.command(name="list")
@click.option("--tenant-id", default="global")
def list_slos(tenant_id):
    """List SLOs."""
    slos = mgr.slo_manager.list_slos(tenant_id=tenant_id)
    click.echo(json.dumps([s.model_dump(mode="json") for s in slos], indent=2))


@slo_group.command(name="create")
@click.option("--service-id", required=True)
@click.option("--name", required=True)
@click.option("--type", default="AVAILABILITY")
@click.option("--target", default=99.9, type=float)
@click.option("--tenant-id", default="global")
def create_slo(service_id, name, type, target, tenant_id):
    """Create a new SLO."""
    slo = mgr.slo_manager.create_slo(
        tenant_id=tenant_id,
        service_id=service_id,
        name=name,
        slo_type=SLOType(type),
        target_threshold=target,
    )
    click.echo(f"Created SLO '{slo.slo_id}'")


@operations_cli.command(name="capacity")
@click.option("--service-id", required=True)
@click.option("--tenant-id", default="global")
def assess_capacity(service_id, tenant_id):
    """Assess capacity for a service."""
    ass = mgr.capacity_manager.get_latest_assessment(service_id=service_id, tenant_id=tenant_id)
    click.echo(json.dumps(ass.model_dump(mode="json"), indent=2))


@operations_cli.command(name="analytics")
@click.option("--tenant-id", default="global")
def get_analytics(tenant_id):
    """Get operational analytics report."""
    rep = mgr.operational_analytics_engine.generate_report(tenant_id=tenant_id)
    click.echo(json.dumps(rep.model_dump(mode="json"), indent=2))
