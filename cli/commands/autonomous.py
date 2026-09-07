"""CLI Commands for Phase 5.53 Enterprise AI Autonomous Assurance Orchestration Platform."""

import sys
import json
import click
from app.autonomous_assurance.manager import AutonomousAssuranceManager
from app.autonomous_assurance.workflows import WorkflowType, WorkflowPriority


@click.group(name="autonomous")
def autonomous_cli():
    """Manage Enterprise AI Autonomous Assurance Orchestration platform operations."""
    pass


@autonomous_cli.command(name="create")
@click.option("--tenant-id", default="default", help="Tenant ID")
@click.option("--name", required=True, help="Workflow name")
@click.option("--type", "workflow_type", default="CROSS_DOMAIN_ASSURANCE", help="Workflow type")
@click.option("--priority", default="HIGH", help="Priority (LOW, MEDIUM, HIGH, CRITICAL)")
def create_workflow(tenant_id: str, name: str, workflow_type: str, priority: str):
    """Create a new autonomous assurance workflow."""
    mgr = AutonomousAssuranceManager()
    wtype = WorkflowType(workflow_type) if workflow_type in WorkflowType.__members__ else WorkflowType.CROSS_DOMAIN_ASSURANCE
    wprio = WorkflowPriority(priority) if priority in WorkflowPriority.__members__ else WorkflowPriority.HIGH
    wf = mgr.workflow_manager.create_workflow(tenant_id, name, workflow_type=wtype, priority=wprio)
    click.echo(json.dumps(wf.model_dump(), indent=2, default=str))


@autonomous_cli.command(name="flow")
@click.option("--tenant-id", default="default", help="Tenant ID")
@click.option("--name", default="Enterprise AI Autonomous Assurance Modernization", help="Flow name")
def run_flow(tenant_id: str, name: str):
    """Run full end-to-end autonomous assurance orchestration flow."""
    mgr = AutonomousAssuranceManager()
    result = mgr.run_full_autonomous_assurance_flow(tenant_id=tenant_id, name=name)
    click.echo(json.dumps(result, indent=2, default=str))


@autonomous_cli.command(name="explain")
@click.option("--tenant-id", default="default", help="Tenant ID")
@click.option("--workflow-id", required=True, help="Workflow ID")
def explain_workflow(tenant_id: str, workflow_id: str):
    """Retrieve explanation for autonomous assurance workflow decisions and steps."""
    mgr = AutonomousAssuranceManager()
    exp = mgr.explainability_engine.explain_workflow(workflow_id, tenant_id)
    click.echo(json.dumps(exp.model_dump(), indent=2, default=str))


if __name__ == "__main__":
    autonomous_cli()
