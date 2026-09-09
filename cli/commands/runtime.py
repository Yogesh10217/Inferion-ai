"""CLI Commands for Enterprise AI Runtime Intelligence (Phase 5.54)."""

import click
import json
from app.runtime_intelligence.manager import RuntimeIntelligenceManager

mgr = RuntimeIntelligenceManager()

@click.group(name="runtime")
def runtime_cli():
    """Enterprise AI Runtime Intelligence Platform CLI Commands."""
    pass

@runtime_cli.command(name="observe")
@click.option("--tenant-id", required=True, help="Tenant ID")
@click.option("--subsystem", required=True, help="Subsystem name")
@click.option("--metric", required=True, help="Metric name")
@click.option("--value", required=True, type=float, help="Metric value")
def observe_cmd(tenant_id: str, subsystem: str, metric: str, value: float):
    """Ingest a runtime observation signal."""
    obs = mgr.ingest_observation(tenant_id, subsystem, metric, value)
    click.echo(f"Runtime Observation Ingested: {obs.observation_id} (Subsystem: {obs.subsystem}, Metric: {obs.metric_name}={obs.value})")

@runtime_cli.command(name="health")
@click.option("--tenant-id", required=True, help="Tenant ID")
@click.option("--subsystem", required=True, help="Subsystem name")
def health_cmd(tenant_id: str, subsystem: str):
    """Evaluate subsystem runtime health score and status."""
    ha = mgr.evaluate_health(tenant_id, subsystem)
    click.echo(f"Runtime Health Evaluated: {ha.assessment_id} (Status: {ha.overall_health.value}, Score: {ha.overall_score})")

@runtime_cli.command(name="resilience")
@click.option("--tenant-id", required=True, help="Tenant ID")
@click.option("--subsystem", required=True, help="Subsystem name")
def resilience_cmd(tenant_id: str, subsystem: str):
    """Evaluate subsystem resilience score and status."""
    ra = mgr.evaluate_resilience(tenant_id, subsystem)
    click.echo(f"Runtime Resilience Evaluated: {ra.assessment_id} (Score: {ra.resilience_score}, Status: {ra.status.value})")

@runtime_cli.command(name="snapshot")
@click.option("--tenant-id", required=True, help="Tenant ID")
def snapshot_cmd(tenant_id: str):
    """Capture immutable runtime snapshot."""
    snap = mgr.capture_snapshot(tenant_id)
    click.echo(f"Runtime Snapshot Captured: {snap.snapshot_id} (Records: {snap.records_count}, Hash: {snap.integrity_hash[:16]}...)")

if __name__ == "__main__":
    runtime_cli()
