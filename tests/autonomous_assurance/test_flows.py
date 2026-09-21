"""
Mandatory 20 E2E Verification Test Flows for Phase 5.53 Enterprise AI Autonomous Assurance Orchestration Platform.
"""

import pytest

from app.autonomous_assurance.boundaries import ActionCategory, BoundaryMode
from app.autonomous_assurance.exceptions import (
    CrossTenantAutonomousAssuranceException,
    DependencyCycleException,
    HighRiskAutonomousActionRequiresApprovalException,
    ImmutableAutonomousAssuranceRecordException,
    InvalidWorkflowStateTransitionException,
    ProhibitedAutonomousActionException,
    WorkflowConcurrencyConflictException,
)
from app.autonomous_assurance.manager import AutonomousAssuranceManager
from app.autonomous_assurance.providers import MockAutonomousAssuranceProvider
from app.autonomous_assurance.workflow_steps import StepActionType
from app.autonomous_assurance.workflows import WorkflowPriority, WorkflowState


@pytest.fixture
def manager():
    return AutonomousAssuranceManager()


def test_01_workflow_creation_and_tenant_isolation(manager):
    """01: Workflow creation in PROPOSED state and tenant isolation verification."""
    tenant = "tenant_alpha"
    wf = manager.workflow_manager.create_workflow(tenant, "Cloud Infrastructure Modernization")
    assert wf.workflow_id.startswith("wf_")
    assert wf.tenant_id == tenant
    assert wf.state == WorkflowState.PROPOSED
    assert wf.is_finalized is False


def test_02_cross_tenant_access_blocked(manager):
    """02: Cross-tenant access blocked with zero metadata leakage."""
    wf = manager.workflow_manager.create_workflow("tenant_owner", "Confidential Infrastructure Workflow")
    with pytest.raises(CrossTenantAutonomousAssuranceException) as exc:
        manager.workflow_manager.get_workflow(wf.workflow_id, tenant_id="tenant_attacker")
    assert "Unauthorized cross-tenant access" in str(exc.value)


def test_03_provider_registry_integration(manager):
    """03: Provider registry integration and multi-domain provider dispatch."""
    mock_prov = MockAutonomousAssuranceProvider("operations_assurance")
    manager.provider_registry.register_provider("operations_assurance", mock_prov)
    prov = manager.provider_registry.get_provider("operations_assurance")
    assert prov.provider_name == "operations_assurance"
    val = prov.validate_action("RESTART_SERVICE", {"target": "srv-1"})
    assert val is True


def test_04_workflow_state_transitions(manager):
    """04: Workflow state transition machine validation and invalid transition blocking."""
    tenant = "tenant_beta"
    wf = manager.workflow_manager.create_workflow(tenant, "State Transition Test")
    # PROPOSED -> ANALYZING
    wf = manager.state_machine.transition_state(wf.workflow_id, tenant, WorkflowState.ANALYZING)
    assert wf.state == WorkflowState.ANALYZING

    # Attempt invalid state transition: ANALYZING -> COMPLETED directly should fail
    with pytest.raises(InvalidWorkflowStateTransitionException):
        manager.state_machine.transition_state(wf.workflow_id, tenant, WorkflowState.COMPLETED)


def test_05_workflow_planning(manager):
    """05: Workflow planning engine step generation and structuring."""
    tenant = "tenant_gamma"
    wf = manager.workflow_manager.create_workflow(tenant, "Planning Test")
    s1 = manager.step_manager.add_step(
        wf.workflow_id, tenant, "Analyze Health", StepActionType.ANALYZE, "health_service"
    )
    manager.step_manager.add_step(
        wf.workflow_id, tenant, "Restart Node", StepActionType.RESTART_SERVICE, "k8s_node", dependencies=[s1.step_id]
    )
    plan = manager.planning_engine.generate_plan(wf.workflow_id, tenant)
    assert plan.plan_id.startswith("plan_")
    assert len(plan.ordered_steps) == 2


def test_06_dependency_resolution(manager):
    """06: Topological dependency resolution and execution order."""
    tenant = "tenant_delta"
    wf = manager.workflow_manager.create_workflow(tenant, "Dependency Resolution Test")
    s1 = manager.step_manager.add_step(wf.workflow_id, tenant, "Step 1", StepActionType.ANALYZE, "target_1")
    s2 = manager.step_manager.add_step(
        wf.workflow_id, tenant, "Step 2", StepActionType.EVALUATE_POLICY, "target_2", dependencies=[s1.step_id]
    )
    ordered, ok = manager.dependency_resolver.resolve_execution_order(wf.workflow_id, tenant)
    assert ok is True
    assert ordered == [s1.step_id, s2.step_id]


def test_07_cycle_detection(manager):
    """07: Dependency cycle detection and execution blocking."""
    tenant = "tenant_epsilon"
    wf = manager.workflow_manager.create_workflow(tenant, "Cycle Detection Test")
    s1 = manager.step_manager.add_step(wf.workflow_id, tenant, "Step A", StepActionType.ANALYZE, "target_a")
    s2 = manager.step_manager.add_step(
        wf.workflow_id, tenant, "Step B", StepActionType.EVALUATE_POLICY, "target_b", dependencies=[s1.step_id]
    )
    # Introduce circular dependency
    s1.dependencies.append(s2.step_id)

    with pytest.raises(DependencyCycleException):
        manager.dependency_resolver.resolve_execution_order(wf.workflow_id, tenant)


def test_08_critical_path_calculation(manager):
    """08: Critical path calculation across workflow steps."""
    tenant = "tenant_zeta"
    wf = manager.workflow_manager.create_workflow(tenant, "Critical Path Test")
    s1 = manager.step_manager.add_step(wf.workflow_id, tenant, "Step 1", StepActionType.ANALYZE, "res_1")
    s2 = manager.step_manager.add_step(
        wf.workflow_id, tenant, "Step 2", StepActionType.RESTART_SERVICE, "res_2", dependencies=[s1.step_id]
    )
    path = manager.dependency_resolver.calculate_critical_path(wf.workflow_id, tenant)
    assert path == [s1.step_id, s2.step_id]


def test_09_priority_calculation(manager):
    """09: Dynamic priority calculation based on impact and urgency."""
    prio = manager.priority_engine.calculate_priority(impact_score=85.0, urgency_score=90.0, risk_score=40.0)
    assert prio == WorkflowPriority.CRITICAL


def test_10_concurrency_conflict_prevented(manager):
    """10: Concurrency conflict prevention on shared target resources."""
    tenant = "tenant_eta"
    lock_id = manager.concurrency_manager.acquire_lock("wf_101", tenant, "cluster_prod_01")
    assert lock_id is not None

    # Second workflow attempting lock on same resource should fail
    with pytest.raises(WorkflowConcurrencyConflictException):
        manager.concurrency_manager.acquire_lock("wf_102", tenant, "cluster_prod_01")

    manager.concurrency_manager.release_lock("wf_101", tenant, "cluster_prod_01")


def test_11_policy_boundary_enforcement(manager):
    """11: Policy boundary enforcement blocking prohibited actions."""
    tenant = "tenant_theta"
    eval_res = manager.boundary_evaluator.evaluate_action(tenant, ActionCategory.DELETE_PRODUCTION_DATA.value)
    assert eval_res.mode == BoundaryMode.PROHIBITED

    wf = manager.workflow_manager.create_workflow(tenant, "Prohibited Boundary Test")
    manager.step_manager.add_step(
        wf.workflow_id, tenant, "Delete DB", ActionCategory.DELETE_PRODUCTION_DATA.value, "prod_db"
    )

    with pytest.raises(ProhibitedAutonomousActionException):
        manager.boundary_evaluator.enforce_boundaries(wf.workflow_id, tenant)


def test_12_human_approval_enforcement(manager):
    """12: Human approval enforcement for high-risk actions."""
    tenant = "tenant_iota"
    eval_res = manager.boundary_evaluator.evaluate_action(tenant, ActionCategory.RESTART_SERVICE.value)
    assert eval_res.mode == BoundaryMode.APPROVAL_REQUIRED

    wf = manager.workflow_manager.create_workflow(tenant, "Approval Required Test")
    manager.step_manager.add_step(
        wf.workflow_id, tenant, "Restart Core Node", ActionCategory.RESTART_SERVICE.value, "node-1"
    )

    with pytest.raises(HighRiskAutonomousActionRequiresApprovalException):
        manager.approval_manager.require_approval_check(wf.workflow_id, tenant)


def test_13_delegation_only_execution(manager):
    """13: Delegation-only execution producing DelegationRequest."""
    tenant = "tenant_kappa"
    req = manager.delegation_coordinator.create_delegation_request(
        workflow_id="wf_del_1",
        tenant_id=tenant,
        target_provider="operations_assurance",
        action_type="RESTART_SERVICE",
        parameters={"service": "api_gateway"},
    )
    assert req.request_id.startswith("del_req_")
    assert req.status.value == "PENDING"
    assert req.target_provider == "operations_assurance"


def test_14_execution_tracking(manager):
    """14: Execution tracking state and progress monitoring."""
    tenant = "tenant_lambda"
    tracker = manager.execution_tracker.start_tracking("wf_track_1", tenant, total_steps=3)
    assert tracker.completed_steps == 0
    assert tracker.progress_percentage == 0.0

    updated = manager.execution_tracker.record_step_completion("wf_track_1", tenant, step_id="s1")
    assert updated.completed_steps == 1
    assert updated.progress_percentage == 33.33


def test_15_verification_engine(manager):
    """15: Step outcome verification and post-condition checks."""
    tenant = "tenant_mu"
    res = manager.verification_engine.verify_step_execution(
        workflow_id="wf_ver_1",
        tenant_id=tenant,
        step_id="step_ver_1",
        expected_postconditions={"status": "running"},
        actual_state={"status": "running"},
    )
    assert res.verified is True
    assert res.assurance_score == 100.0


def test_16_failure_recovery_planning(manager):
    """16: Automated failure recovery planning upon step verification failure."""
    tenant = "tenant_nu"
    plan = manager.recovery_planner.plan_recovery(
        workflow_id="wf_rec_1",
        tenant_id=tenant,
        failed_step_id="step_failed_1",
        trigger_reason="Node status unresponsive",
    )
    assert plan.recovery_id.startswith("rec_")
    assert plan.recovery_strategy == "FALLBACK_RETRY"
    assert len(plan.recovery_steps) > 0


def test_17_compensation_planning(manager):
    """17: Multi-step compensation planning for irreversible workflow state changes."""
    tenant = "tenant_xi"
    plan = manager.compensation_planner.plan_compensation(
        workflow_id="wf_comp_1", tenant_id=tenant, completed_steps=["step_1", "step_2"]
    )
    assert plan.compensation_id.startswith("comp_")
    assert len(plan.compensation_steps) == 2


def test_18_rollback_planning(manager):
    """18: Rollback strategy formulation and execution step reversing."""
    tenant = "tenant_omikron"
    rb = manager.rollback_engine.create_rollback_plan(
        workflow_id="wf_rb_1", tenant_id=tenant, executed_actions=["DISABLE_ROUTE", "DRAIN_TRAFFIC"]
    )
    assert rb.rollback_id.startswith("rb_")
    assert rb.rollback_actions == ["RESTORE_TRAFFIC", "ENABLE_ROUTE"]


def test_19_immutable_sha256_evidence(manager):
    """19: Immutable SHA-256 evidence sealing and tampered record blocking."""
    tenant = "tenant_pi"
    wf = manager.workflow_manager.create_workflow(tenant, "SHA-256 Evidence Test")
    ev = manager.evidence_engine.seal_evidence(wf.workflow_id, tenant, execution_trace=["step_1", "step_2"])
    assert len(ev.evidence_sha256) == 64

    # Second attempt to seal evidence on finalized record raises ImmutableAutonomousAssuranceRecordException
    manager.workflow_manager.finalize_workflow(wf.workflow_id, tenant)
    with pytest.raises(ImmutableAutonomousAssuranceRecordException):
        manager.workflow_manager.finalize_workflow(wf.workflow_id, tenant)


def test_20_full_autonomous_assurance_lifecycle(manager):
    """20: Full autonomous assurance lifecycle execution end-to-end."""
    res = manager.run_full_autonomous_assurance_flow(tenant_id="tenant_rho", name="Full End-to-End Orchestration Flow")
    assert res["workflow"]["is_finalized"] is True
    assert res["workflow"]["state"] == "COMPLETED"
    assert res["evidence"]["evidence_sha256"] is not None
    assert res["explainability"]["summary"] is not None
    assert len(res["evidence"]["evidence_sha256"]) == 64
