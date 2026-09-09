"""CLI Commands for Enterprise AI Capacity Intelligence (Phase 5.56)."""

import click
import json
from app.capacity_intelligence.manager import CapacityIntelligenceManager

mgr = CapacityIntelligenceManager()

@click.group(name="capacity")
def capacity_cli():
    """Enterprise AI Capacity Intelligence Platform CLI Commands."""
    pass

@capacity_cli.command(name="register")
@click.option("--tenant-id", required=True, help="Tenant ID")
@click.option("--resource-id", required=True, help="Resource ID")
@click.option("--name", required=True, help="Resource name")
@click.option("--resource-type", required=True, help="Resource type")
@click.option("--capacity", required=True, type=float, help="Total capacity")
def register_cmd(tenant_id: str, resource_id: str, name: str, resource_type: str, capacity: float):
    """Register capacity resource."""
    res = mgr.register_resource(tenant_id, resource_id, name, resource_type, capacity)
    click.echo(f"Capacity Resource Registered: {res.resource_id} (Name: {res.name}, Capacity: {res.total_capacity})")

@capacity_cli.command(name="assess")
@click.option("--tenant-id", required=True, help="Tenant ID")
@click.option("--resource-id", required=True, help="Resource ID")
def assess_cmd(tenant_id: str, resource_id: str):
    """Assess resource capacity and utilization."""
    ass = mgr.assess_capacity(tenant_id, resource_id)
    click.echo(f"Capacity Assessed: {ass.assessment_id} (Utilization: {ass.utilization_rate*100:.1f}%, Status: {ass.health_status})")

@capacity_cli.command(name="forecast")
@click.option("--tenant-id", required=True, help="Tenant ID")
@click.option("--resource-id", required=True, help="Resource ID")
@click.option("--days", default=30, help="Horizon in days")
def forecast_cmd(tenant_id: str, resource_id: str, days: int):
    """Forecast capacity utilization over horizon."""
    fc = mgr.forecast_capacity(tenant_id, resource_id, days)
    click.echo(f"Capacity Forecast: {fc.forecast_id} (Predicted Utilization: {fc.predicted_utilization*100:.1f}%, Exhaustion Predicted: {fc.exhaustion_predicted})")

@capacity_cli.command(name="snapshot")
@click.option("--tenant-id", required=True, help="Tenant ID")
def snapshot_cmd(tenant_id: str):
    """Capture immutable capacity snapshot."""
    snap = mgr.capture_snapshot(tenant_id)
    click.echo(f"Capacity Snapshot Captured: {snap.snapshot_id} (Records: {snap.records_count}, Hash: {snap.integrity_hash[:16]}...)")

if __name__ == "__main__":
    capacity_cli()
