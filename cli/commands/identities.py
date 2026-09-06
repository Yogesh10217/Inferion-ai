"""CLI commands for Identity Assurance platform."""

import json
import click
from app.identity_assurance.manager import IdentityAssuranceManager
from app.identity_assurance.identities import IdentityType, IdentityCategory

_mgr = IdentityAssuranceManager()


@click.group(name="identities")
def identities_cli():
    """Manage Enterprise AI Identity Intelligence, Trust, Access Assurance, and Governance."""
    pass


@identities_cli.command(name="register")
@click.option("--tenant-id", default="default_tenant", help="Tenant ID")
@click.option("--name", required=True, help="Identity Name")
@click.option("--type", default="HUMAN", help="Identity Type")
def register_cmd(tenant_id: str, name: str, type: str):
    """Register a new enterprise identity."""
    identity = _mgr.register_identity(
        tenant_id=tenant_id,
        name=name,
        identity_type=IdentityType(type),
        category=IdentityCategory.EMPLOYEE,
    )
    click.echo(json.dumps(identity.model_dump(), indent=2, default=str))


@identities_cli.command(name="analyze")
@click.argument("identity_id")
@click.option("--tenant-id", default="default_tenant", help="Tenant ID")
def analyze_cmd(identity_id: str, tenant_id: str):
    """Analyze identity profile and entitlements."""
    profile = _mgr.profile_manager.get_profile(tenant_id, identity_id)
    click.echo(json.dumps(profile.model_dump(), indent=2, default=str))


@identities_cli.command(name="trust")
@click.argument("identity_id")
@click.option("--tenant-id", default="default_tenant", help="Tenant ID")
def trust_cmd(identity_id: str, tenant_id: str):
    """Evaluate identity trust score."""
    trust = _mgr.trust_engine.assess_trust(tenant_id, identity_id)
    click.echo(json.dumps(trust.model_dump(), indent=2, default=str))


@identities_cli.command(name="privileges")
@click.argument("identity_id")
@click.option("--tenant-id", default="default_tenant", help="Tenant ID")
def privileges_cmd(identity_id: str, tenant_id: str):
    """Evaluate identity privileges and risk."""
    priv = _mgr.privilege_manager.assess_privileges(tenant_id, identity_id)
    click.echo(json.dumps(priv.model_dump(), indent=2, default=str))


@identities_cli.command(name="risk")
@click.argument("identity_id")
@click.option("--tenant-id", default="default_tenant", help="Tenant ID")
def risk_cmd(identity_id: str, tenant_id: str):
    """Assess identity overall risk."""
    risk = _mgr.risk_manager.assess_risk(tenant_id, identity_id)
    click.echo(json.dumps(risk.model_dump(), indent=2, default=str))


@identities_cli.command(name="assurance")
@click.argument("identity_id")
@click.option("--tenant-id", default="default_tenant", help="Tenant ID")
def assurance_cmd(identity_id: str, tenant_id: str):
    """Evaluate continuous identity assurance score."""
    score = _mgr.evaluate_identity_assurance(tenant_id, identity_id)
    click.echo(json.dumps(score.model_dump(), indent=2, default=str))


@identities_cli.command(name="review")
@click.option("--tenant-id", default="default_tenant", help="Tenant ID")
@click.option("--title", default="Privileged Access Review", help="Review title")
def review_cmd(tenant_id: str, title: str):
    """Create a new access review."""
    review = _mgr.access_review_manager.create_review(tenant_id=tenant_id, title=title)
    click.echo(json.dumps(review.model_dump(), indent=2, default=str))


@identities_cli.command(name="investigate")
@click.argument("identity_id")
@click.option("--tenant-id", default="default_tenant", help="Tenant ID")
def investigate_cmd(identity_id: str, tenant_id: str):
    """Create an identity investigation."""
    inv = _mgr.investigation_manager.create_investigation(tenant_id, identity_id)
    click.echo(json.dumps(inv.model_dump(), indent=2, default=str))
