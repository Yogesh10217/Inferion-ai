"""CLI commands for Decision Governance platform."""

import click
import json
from app.decision_governance.manager import DecisionGovernanceManager
from app.decision_governance.decisions import DecisionType, DecisionPriority

_mgr = DecisionGovernanceManager()


@click.group(name="decisions")
def decisions_cli():
    """Manage Enterprise AI Decision Governance operations."""
    pass


@decisions_cli.command(name="list")
@click.option("--tenant-id", default="default_tenant", help="Tenant ID")
def list_decisions_cmd(tenant_id: str):
    """List decisions for a tenant."""
    decisions = _mgr.list_decisions(tenant_id)
    click.echo(json.dumps([d.model_dump() for d in decisions], indent=2, default=str))


@decisions_cli.command(name="get")
@click.argument("decision_id")
@click.option("--tenant-id", default="default_tenant", help="Tenant ID")
def get_decision_cmd(decision_id: str, tenant_id: str):
    """Get decision details by ID."""
    try:
        decision = _mgr.get_decision(decision_id, tenant_id)
        click.echo(json.dumps(decision.model_dump(), indent=2, default=str))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@decisions_cli.command(name="create")
@click.option("--title", required=True, help="Decision title")
@click.option("--decision-type", default="OPERATIONAL", help="Decision type")
@click.option("--description", default="", help="Description")
@click.option("--tenant-id", default="default_tenant", help="Tenant ID")
def create_decision_cmd(title: str, decision_type: str, description: str, tenant_id: str):
    """Create a new decision."""
    dtype = DecisionType(decision_type)
    d = _mgr.create_decision(tenant_id=tenant_id, title=title, decision_type=dtype, description=description)
    click.echo(json.dumps(d.model_dump(), indent=2, default=str))


@decisions_cli.command(name="recommend")
@click.argument("decision_id")
@click.option("--title", required=True, help="Recommendation title")
@click.option("--tenant-id", default="default_tenant", help="Tenant ID")
def recommend_cmd(decision_id: str, title: str, tenant_id: str):
    """Generate recommendation for decision."""
    rec = _mgr.recommendations.create_recommendation(
        tenant_id=tenant_id,
        decision_id=decision_id,
        title=title,
        description="CLI Generated Recommendation",
        rationale="Recommended based on rule synthesis",
    )
    click.echo(json.dumps(rec.model_dump(), indent=2, default=str))


@decisions_cli.command(name="plan")
@click.argument("decision_id")
@click.option("--tenant-id", default="default_tenant", help="Tenant ID")
def plan_cmd(decision_id: str, tenant_id: str):
    """Generate multi-step plan for decision."""
    from app.decision_governance.planning import DecisionPlanStep

    step = DecisionPlanStep(sequence_order=1, name="InitStep", action_type="PREPARE", target_domain="operations")
    plan = _mgr.planning.create_plan(tenant_id=tenant_id, decision_id=decision_id, name="CLI Decision Plan", steps=[step])
    click.echo(json.dumps(plan.model_dump(), indent=2, default=str))


@decisions_cli.command(name="simulate")
@click.argument("decision_id")
@click.option("--tenant-id", default="default_tenant", help="Tenant ID")
def simulate_cmd(decision_id: str, tenant_id: str):
    """Run decision simulation."""
    from app.decision_governance.simulation import SimulationInput

    inp = SimulationInput(decision_id=decision_id, iterations=50)
    sim = _mgr.simulation.run_simulation(tenant_id=tenant_id, decision_id=decision_id, name="CLI Simulation", input_params=inp)
    click.echo(json.dumps(sim.model_dump(), indent=2, default=str))


@decisions_cli.command(name="scenarios")
@click.argument("decision_id")
@click.option("--tenant-id", default="default_tenant", help="Tenant ID")
def scenarios_cmd(decision_id: str, tenant_id: str):
    """Create baseline decision scenario."""
    sc = _mgr.scenarios.create_scenario(tenant_id=tenant_id, decision_id=decision_id, name="Baseline Scenario")
    click.echo(json.dumps(sc.model_dump(), indent=2, default=str))


@decisions_cli.command(name="alternatives")
@click.argument("decision_id")
@click.option("--tenant-id", default="default_tenant", help="Tenant ID")
def alternatives_cmd(decision_id: str, tenant_id: str):
    """Evaluate decision alternatives."""
    alt = _mgr.alternatives.create_alternative(tenant_id=tenant_id, decision_id=decision_id, name="Alternative A", description="Min change option")
    click.echo(json.dumps(alt.model_dump(), indent=2, default=str))


@decisions_cli.command(name="conflicts")
@click.argument("decision_id")
@click.option("--tenant-id", default="default_tenant", help="Tenant ID")
def conflicts_cmd(decision_id: str, tenant_id: str):
    """Detect decision conflicts."""
    c = _mgr.conflicts.list_conflicts_for_decision(decision_id, tenant_id)
    click.echo(json.dumps([conf.model_dump() for conf in c], indent=2, default=str))


@decisions_cli.command(name="explain")
@click.argument("decision_id")
@click.option("--tenant-id", default="default_tenant", help="Tenant ID")
def explain_cmd(decision_id: str, tenant_id: str):
    """Explain decision rationale."""
    exp = _mgr.explainability.generate_explanation(
        tenant_id=tenant_id,
        decision_id=decision_id,
        why_summary="CLI Explanation",
        expected_outcome="Positive outcome",
    )
    click.echo(json.dumps(exp.model_dump(), indent=2, default=str))


@decisions_cli.command(name="approve")
@click.argument("decision_id")
@click.option("--tenant-id", default="default_tenant", help="Tenant ID")
def approve_cmd(decision_id: str, tenant_id: str):
    """Approve decision."""
    d = _mgr.approve_decision(decision_id, tenant_id)
    click.echo(json.dumps(d.model_dump(), indent=2, default=str))


@decisions_cli.command(name="delegate")
@click.argument("decision_id")
@click.option("--tenant-id", default="default_tenant", help="Tenant ID")
def delegate_cmd(decision_id: str, tenant_id: str):
    """Delegate decision actions."""
    from app.decision_governance.delegation import DecisionDelegationAction

    act = DecisionDelegationAction(target_type="SERVICE", target_id="srv-1", action_name="EXECUTE")
    plan = _mgr.delegate_decision(decision_id, tenant_id, [act])
    click.echo(json.dumps(plan.model_dump(), indent=2, default=str))


@decisions_cli.command(name="verify")
@click.argument("decision_id")
@click.option("--tenant-id", default="default_tenant", help="Tenant ID")
def verify_cmd(decision_id: str, tenant_id: str):
    """Verify decision outcome."""
    d = _mgr.verify_and_finalize(decision_id, tenant_id)
    click.echo(json.dumps(d.model_dump(), indent=2, default=str))


@decisions_cli.command(name="analytics")
@click.option("--tenant-id", default="default_tenant", help="Tenant ID")
def analytics_cmd(tenant_id: str):
    """Generate analytics report."""
    decisions = _mgr.list_decisions(tenant_id)
    rep = _mgr.analytics.generate_analytics_report(tenant_id, decisions)
    click.echo(json.dumps(rep.model_dump(), indent=2, default=str))
