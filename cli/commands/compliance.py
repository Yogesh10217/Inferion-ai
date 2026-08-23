"""CLI Command Group for Enterprise AI Compliance Platform."""

import sys
import json
import click

from app.compliance_platform.manager import CompliancePlatformManager
from app.compliance_platform.frameworks import FrameworkType
from app.compliance_platform.assurance import AssuranceConclusion

mgr = CompliancePlatformManager()


@click.group(name="compliance")
def compliance_cli():
    """Manage Enterprise AI Compliance, Controls, Audit & Assurance."""
    pass


@compliance_cli.group(name="frameworks")
def frameworks_cli():
    """Manage compliance frameworks."""
    pass


@frameworks_cli.command(name="list")
@click.option("--tenant-id", default="global", help="Tenant ID.")
def list_frameworks(tenant_id: str):
    """List adopted compliance frameworks."""
    frameworks = mgr.framework_manager.list_frameworks(tenant_id)
    click.echo(json.dumps([f.model_dump() for f in frameworks], indent=2, default=str))


@frameworks_cli.command(name="adopt")
@click.option("--tenant-id", default="global", help="Tenant ID.")
@click.option("--type", "fw_type", default="SOC_2", help="Framework type.")
@click.option("--name", default="SOC 2 Framework", help="Framework name.")
def adopt_framework(tenant_id: str, fw_type: str, name: str):
    """Adopt a compliance framework."""
    fw = mgr.framework_manager.adopt_framework(tenant_id, FrameworkType(fw_type), name, "Adopted via CLI")
    click.echo(json.dumps(fw.model_dump(), indent=2, default=str))


@compliance_cli.group(name="controls")
def controls_cli():
    """Manage compliance controls."""
    pass


@controls_cli.command(name="list")
@click.option("--tenant-id", default="global", help="Tenant ID.")
def list_controls(tenant_id: str):
    """List compliance controls."""
    ctrls = mgr.control_manager.list_controls(tenant_id)
    click.echo(json.dumps([c.model_dump() for c in ctrls], indent=2, default=str))


@compliance_cli.command(name="assess")
@click.option("--tenant-id", default="global", help="Tenant ID.")
@click.option("--framework-id", required=True, help="Framework ID.")
@click.option("--subject-id", default="global", help="Subject ID.")
def run_assessment(tenant_id: str, framework_id: str, subject_id: str):
    """Run compliance assessment."""
    ass = mgr.assessment_manager.run_assessment(tenant_id, framework_id, subject_id)
    click.echo(json.dumps(ass.model_dump(), indent=2, default=str))


@compliance_cli.command(name="findings")
@click.option("--tenant-id", default="global", help="Tenant ID.")
def list_findings(tenant_id: str):
    """List open compliance findings."""
    findings = mgr.finding_manager.list_findings(tenant_id)
    click.echo(json.dumps([f.model_dump() for f in findings], indent=2, default=str))


@compliance_cli.command(name="posture")
@click.option("--tenant-id", default="global", help="Tenant ID.")
def get_posture(tenant_id: str):
    """Get enterprise compliance posture score."""
    posture = mgr.posture_manager.get_posture(tenant_id)
    click.echo(json.dumps(posture.model_dump(), indent=2, default=str))


@compliance_cli.command(name="assurance")
@click.option("--tenant-id", default="global", help="Tenant ID.")
@click.option("--framework-id", default="fw_global", help="Framework ID.")
def generate_assurance(tenant_id: str, framework_id: str):
    """Generate immutable compliance assurance report."""
    rep = mgr.assurance_manager.generate_assurance_report(tenant_id, framework_id, AssuranceConclusion.ASSURED)
    click.echo(json.dumps(rep.model_dump(), indent=2, default=str))


@compliance_cli.command(name="audit-package")
@click.option("--tenant-id", default="global", help="Tenant ID.")
@click.option("--framework-id", default="fw_global", help="Framework ID.")
def create_audit_package(tenant_id: str, framework_id: str):
    """Create immutable audit readiness package."""
    pkg = mgr.audit_manager.create_audit_package(tenant_id, framework_id, "bundle_001", "report_001")
    click.echo(json.dumps(pkg.model_dump(), indent=2, default=str))
