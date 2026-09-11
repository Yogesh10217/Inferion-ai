"""
CLI Commands for Platform Hardening, Integration Audits & Certification.
"""

import click
import json
from app.platform_hardening.manager import PlatformHardeningManager


@click.group(name="hardening")
def platform_hardening_cli():
    """Platform Hardening, Deep Audit, Production Hardening & Certification CLI."""
    pass


@platform_hardening_cli.command(name="audit")
@click.option("--tenant-id", default="system", help="Tenant ID scope")
def run_audit(tenant_id: str):
    """Run platform-wide deep integration audit & code scan."""
    mgr = PlatformHardeningManager()
    res = mgr.run_platform_audit(tenant_id=tenant_id)
    click.echo(f"Audit Completed: {res.audit_id}")
    click.echo(f"Status: {res.status.value}")
    click.echo(f"Readiness Score: {res.readiness_score}/100")
    click.echo(f"Release Decision: {res.release_gate.decision.value}")
    click.echo(f"Certification: {res.certification.status.value}")
    click.echo(f"Total Findings: {len(res.findings)}")


@platform_hardening_cli.command(name="health")
@click.option("--tenant-id", default="system", help="Tenant ID scope")
def get_health(tenant_id: str):
    """Get overall platform health summary."""
    mgr = PlatformHardeningManager()
    summary = mgr.get_platform_health_summary(tenant_id=tenant_id)
    click.echo(f"Tenant: {summary.tenant_id}")
    click.echo(f"Integration Health: {summary.integration_health.value}")
    click.echo(f"Certification: {summary.certification_status.value}")
    click.echo(f"Readiness: {summary.readiness_score}/100")


@platform_hardening_cli.command(name="stubs")
@click.option("--tenant-id", default="system", help="Tenant ID scope")
def scan_stubs(tenant_id: str):
    """Scan production code paths for unclassified stubs."""
    mgr = PlatformHardeningManager()
    res = mgr.stub_detection.scan_stubs(tenant_id=tenant_id)
    click.echo(f"Total Scanned Files: {res.total_files_scanned}")
    click.echo(f"Unclassified Production Stubs: {res.unclassified_stubs_count}")


@platform_hardening_cli.command(name="certification")
@click.option("--tenant-id", default="system", help="Tenant ID scope")
def get_certification(tenant_id: str):
    """Get latest platform certification details."""
    mgr = PlatformHardeningManager()
    cert = mgr.cert_repo.get_latest(tenant_id)
    if cert:
        click.echo(f"Certification ID: {cert.certification_id}")
        click.echo(f"Status: {cert.status.value}")
        click.echo(f"SHA-256 Hash: {cert.evidence.sha256_hash}")
    else:
        click.echo("No certification record found for tenant.")


if __name__ == "__main__":
    platform_hardening_cli()
