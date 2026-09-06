"""CLI Commands for Data Intelligence Platform (Phase 5.43)."""

import click
from typing import Optional
from app.data_intelligence.manager import DataIntelligenceManager

_mgr = DataIntelligenceManager()


@click.group(name="data")
def data_cli():
    """CLI for Enterprise AI Data Intelligence Platform."""
    pass


@data_cli.command(name="datasets")
@click.option("--tenant-id", default="global", help="Tenant Identifier")
def list_datasets(tenant_id: str):
    """List dataset references for tenant."""
    datasets = _mgr.dataset_manager.list_datasets(tenant_id)
    click.echo(f"Found {len(datasets)} dataset references for tenant '{tenant_id}':")
    for d in datasets:
        click.echo(f" - [{d.dataset_id}] {d.name} ({d.dataset_type.value}, Status: {d.status.value})")


@data_cli.command(name="quality")
@click.option("--dataset-id", required=True, help="Dataset ID")
@click.option("--tenant-id", default="global", help="Tenant Identifier")
def evaluate_quality(dataset_id: str, tenant_id: str):
    """Evaluate quality for dataset."""
    res = _mgr.quality_manager.evaluate_quality(dataset_id, tenant_id)
    click.echo(f"Quality result for dataset '{dataset_id}': Score = {res.overall_quality_score:.4f} (Status: {res.status.value})")


@data_cli.command(name="anomalies")
@click.option("--tenant-id", default="global", help="Tenant Identifier")
def list_anomalies(tenant_id: str):
    """List data anomalies for tenant."""
    anomalies = _mgr.anomaly_manager.list_anomalies(tenant_id)
    click.echo(f"Found {len(anomalies)} anomalies for tenant '{tenant_id}':")
    for a in anomalies:
        click.echo(f" - [{a.anomaly_id}] {a.anomaly_type.value}: Expected {a.evidence.expected_value}, Actual {a.evidence.actual_value} (Severity: {a.severity.value})")


@data_cli.command(name="drift")
@click.option("--dataset-id", required=True, help="Dataset ID")
@click.option("--tenant-id", default="global", help="Tenant Identifier")
def evaluate_drift(dataset_id: str, tenant_id: str):
    """Evaluate drift for dataset."""
    ass = _mgr.drift_manager.evaluate_drift_assessment(dataset_id, tenant_id)
    click.echo(f"Drift assessment for dataset '{dataset_id}': Detected={ass.overall_drift_detected}, MaxScore={ass.max_drift_score:.2f}")


@data_cli.command(name="lineage")
@click.option("--tenant-id", default="global", help="Tenant Identifier")
def get_lineage(tenant_id: str):
    """Get data lineage for tenant."""
    lin = _mgr.lineage_manager.get_lineage(tenant_id)
    click.echo(f"Lineage graph for tenant '{tenant_id}': {len(lin.nodes)} nodes, {len(lin.relationships)} relationships.")


@data_cli.command(name="incidents")
@click.option("--tenant-id", default="global", help="Tenant Identifier")
def list_incidents(tenant_id: str):
    """List data incidents for tenant."""
    incidents = _mgr.incident_manager.list_incidents(tenant_id)
    click.echo(f"Found {len(incidents)} data incidents for tenant '{tenant_id}':")
    for i in incidents:
        click.echo(f" - [{i.incident_id}] {i.title} (Severity: {i.severity.value}, Status: {i.status.value})")


@data_cli.command(name="remediation")
@click.option("--tenant-id", default="global", help="Tenant Identifier")
def list_remediations(tenant_id: str):
    """List remediation plans for tenant."""
    plans = [p for p in _mgr.remediation_manager._plans.values() if p.tenant_id == tenant_id]
    click.echo(f"Found {len(plans)} remediation plans for tenant '{tenant_id}':")
    for p in plans:
        click.echo(f" - [{p.plan_id}] Status: {p.status.value}, Actions: {len(p.actions)}")


@data_cli.command(name="trust")
@click.option("--dataset-id", required=True, help="Dataset ID")
@click.option("--tenant-id", default="global", help="Tenant Identifier")
def evaluate_trust(dataset_id: str, tenant_id: str):
    """Evaluate dataset trust score."""
    trust = _mgr.trust_engine.evaluate_trust(dataset_id, tenant_id)
    click.echo(f"Dataset trust for '{dataset_id}': Score={trust.score:.1f}, Band={trust.band.value}")


@data_cli.command(name="analytics")
@click.option("--tenant-id", default="global", help="Tenant Identifier")
def get_analytics(tenant_id: str):
    """Get data intelligence analytics report."""
    rpt = _mgr.analytics_engine.generate_report(tenant_id)
    click.echo(f"Analytics report for tenant '{tenant_id}': {len(rpt.metrics)} metrics, {len(rpt.insights)} insights.")
