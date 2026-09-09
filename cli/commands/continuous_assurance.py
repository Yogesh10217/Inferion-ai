"""CLI commands for Continuous Assurance (Phase 5.54)."""

import click
import json
from app.continuous_assurance.manager import ContinuousAssuranceManager

mgr = ContinuousAssuranceManager()

@click.group(name="assurance")
def assurance_group():
    """Continuous Assurance Platform commands."""
    pass

@assurance_group.command(name="observe")
@click.option("--tenant-id", required=True, help="Tenant ID")
@click.option("--domain", required=True, help="Source domain")
@click.option("--type", required=True, help="Observation type")
@click.option("--payload", default="{}", help="JSON payload string")
def observe_cmd(tenant_id: str, domain: str, type: str, payload: str):
    """Record a runtime observation."""
    p_dict = json.loads(payload)
    obs = mgr.record_observation(tenant_id, domain, type, p_dict)
    click.echo(f"Observation created: {obs.observation_id} (Status: {obs.status.value})")

@assurance_group.command(name="assess")
@click.option("--tenant-id", required=True, help="Tenant ID")
def assess_cmd(tenant_id: str):
    """Trigger a continuous assurance evaluation."""
    ass = mgr.evaluate_tenant_assurance(tenant_id)
    click.echo(f"Assessment evaluated: {ass.assessment_id} (Score: {ass.score.overall_score}, State: {ass.state.value})")

@assurance_group.command(name="current")
@click.option("--tenant-id", required=True, help="Tenant ID")
def current_cmd(tenant_id: str):
    """Get the latest continuous assurance assessment."""
    ass = mgr.get_latest_assessment(tenant_id)
    if not ass:
        ass = mgr.evaluate_tenant_assurance(tenant_id)
    click.echo(f"Current Assessment: {ass.assessment_id} (Score: {ass.score.overall_score}, State: {ass.state.value})")

@assurance_group.command(name="drift")
@click.option("--tenant-id", required=True, help="Tenant ID")
@click.option("--type", required=True, help="Drift type")
def drift_cmd(tenant_id: str, type: str):
    """Analyze drift between expected and observed state."""
    drift = mgr.analyze_drift(tenant_id, type, {"key": "expected"}, {"key": "observed"})
    click.echo(f"Drift Analyzed: {drift.drift_id} (Summary: {drift.difference_summary})")

@assurance_group.command(name="controls")
@click.option("--tenant-id", required=True, help="Tenant ID")
@click.option("--control-id", required=True, help="Control ID")
def controls_cmd(tenant_id: str, control_id: str):
    """Evaluate control effectiveness."""
    ctrl = mgr.evaluate_control(tenant_id, control_id)
    click.echo(f"Control Evaluated: {ctrl.assessment_id} (Status: {ctrl.status.value})")

@assurance_group.command(name="verify")
@click.option("--tenant-id", required=True, help="Tenant ID")
@click.option("--resource-id", required=True, help="Resource ID")
@click.option("--expected-hash", required=True, help="Expected hash")
@click.option("--actual-hash", required=True, help="Actual hash")
def verify_cmd(tenant_id: str, resource_id: str, expected_hash: str, actual_hash: str):
    """Verify runtime resource integrity."""
    ver = mgr.verify_resource(tenant_id, resource_id, expected_hash, actual_hash)
    click.echo(f"Verification Result: {ver.verification_id} (Status: {ver.status.value})")

@assurance_group.command(name="recommendations")
@click.option("--tenant-id", required=True, help="Tenant ID")
def recommendations_cmd(tenant_id: str):
    """List advisory recommendations."""
    recs = mgr.rec_engine.list_recommendations(tenant_id)
    click.echo(f"Recommendations for '{tenant_id}': {len(recs)} items")

@assurance_group.command(name="analytics")
@click.option("--tenant-id", required=True, help="Tenant ID")
def analytics_cmd(tenant_id: str):
    """View analytics report."""
    report = mgr.analytics.generate_report(tenant_id)
    click.echo(json.dumps(report, indent=2))
