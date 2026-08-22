"""Mandatory End-to-End Integration Flow Tests for Phase 5.18 Enterprise Orchestration Platform."""

import pytest
from app.orchestration.manager import OrchestrationManager
from app.orchestration.workflow import WorkflowStep, WorkflowExecutionStatus
from app.orchestration.human_tasks import TaskStatus
from app.orchestration.case_management import CaseType, CaseStatus
from app.orchestration.routing import RoutingStrategy
from app.orchestration.agent_orchestration import AgentTask
from app.orchestration.compensation import SagaStep, SagaStepStatus
from app.orchestration.governance import GovernanceAction
from app.identity.exceptions import AgentBoundaryViolationException


def test_flow_1_enterprise_human_plus_ai_workflow():
    """FLOW 1 — Enterprise Human + AI Workflow."""
    mgr = OrchestrationManager()

    # 1. Define workflow
    steps = [
        WorkflowStep(step_id="ai_analyze", name="AI Analysis", step_type="AGENT"),
        WorkflowStep(step_id="human_approval", name="Manager Approval", step_type="APPROVAL"),
        WorkflowStep(step_id="worker_execute", name="Worker Deployment", step_type="WORKER"),
    ]
    wf_def = mgr.definition_manager.create_definition("E2E Human-AI Flow", steps=steps, tenant_id="t_f1")

    # 2. Start Execution
    exec_obj = mgr.execution_engine.start_execution(wf_def, inputs={"target": "prod"}, tenant_id="t_f1")
    assert exec_obj.status == WorkflowExecutionStatus.RUNNING

    # 3. Create Human Task for approval step
    task = mgr.human_task_manager.create_task("Approve AI Analysis", assigned_user_id="user_manager", assigned_role="manager", tenant_id="t_f1", execution_id=exec_obj.execution_id)
    assert task.status == TaskStatus.ASSIGNED


    # 4. Human approves
    mgr.human_task_manager.complete_task(task.task_id, outputs={"decision": "APPROVED"})

    # 5. Complete workflow execution
    comp_exec = mgr.execution_engine.complete_execution(exec_obj.execution_id, final_outputs={"status": "DEPLOYED"})
    assert comp_exec.status == WorkflowExecutionStatus.COMPLETED


def test_flow_2_durable_recovery():
    """FLOW 2 — Durable Recovery: Checkpointing & Idempotent re-execution prevention."""
    mgr = OrchestrationManager()
    wf_def = mgr.definition_manager.create_definition("Durable Flow", steps=[WorkflowStep(step_id="s1", name="S1")], tenant_id="t_f2")

    # 1. Step completes & Checkpoint stored
    exec_obj = mgr.execution_engine.start_execution(wf_def, tenant_id="t_f2", idempotency_key="idemp_key_f2")
    mgr.execution_engine.save_checkpoint(exec_obj.execution_id, "s1", {"data": "step1_ok"}, tenant_id="t_f2")

    # 2. System restart simulation & Re-execution attempt with same idempotency_key
    exec_recovered = mgr.execution_engine.start_execution(wf_def, tenant_id="t_f2", idempotency_key="idemp_key_f2")

    # Verify existing execution returned without repeating step 1!
    assert exec_recovered.execution_id == exec_obj.execution_id


def test_flow_3_agent_delegated_authorization():
    """FLOW 3 — Agent Delegated Authorization: Scoped delegation boundary enforcement."""
    mgr = OrchestrationManager()

    # User delegates scoped authority
    del_auth = mgr.agent_orchestration_manager.agent_identity_manager.create_delegated_authorization(
        user_identity_id="user_f3",
        agent_id="agent_f3",
        delegated_scopes=["read", "analyze"],
        tenant_id="t_f3",
    )

    # Agent executes allowed action -> Success
    task_ok = AgentTask(agent_id="agent_f3", action="analyze_report", tenant_id="t_f3", delegation_id=del_auth.delegation_id)
    res_ok = mgr.agent_orchestration_manager.execute_agent_task(task_ok, requested_scope="analyze")
    assert res_ok["status"] == "SUCCESS"

    # Agent attempts privileged action outside boundary -> Exception!
    task_bad = AgentTask(agent_id="agent_f3", action="override_security", tenant_id="t_f3", delegation_id=del_auth.delegation_id)
    with pytest.raises(AgentBoundaryViolationException):
        mgr.agent_orchestration_manager.execute_agent_task(task_bad, requested_scope="admin")


def test_flow_4_high_risk_workflow_action():
    """FLOW 4 — High-Risk Workflow Action: Pre-execution risk evaluation & approval gating."""
    mgr = OrchestrationManager()

    risk_assessment = mgr.workflow_governance_engine.evaluate_workflow_execution(
        workflow_id="wf_prod_deploy",
        tenant_id="t_f4",
        action_name="production_deploy",
        risk_score=85.0,
    )

    assert risk_assessment.governance_action == GovernanceAction.REQUIRE_APPROVAL
    assert risk_assessment.approval_request_id is not None


def test_flow_5_distributed_compensation():
    """FLOW 5 — Distributed Compensation: Saga reverse-order rollback on failure."""
    mgr = OrchestrationManager()

    steps = [
        SagaStep(step_id="s1", action_name="create_resource", compensation_action="delete_resource"),
        SagaStep(step_id="s2", action_name="grant_data_access", compensation_action="revoke_data_access"),
        SagaStep(step_id="s3", action_name="deploy_config", compensation_action="rollback_config"),
    ]
    saga = mgr.compensation_manager.create_saga("exec_f5", steps, tenant_id="t_f5")
    mgr.compensation_manager.mark_step_executed(saga.saga_id, "s1")
    mgr.compensation_manager.mark_step_executed(saga.saga_id, "s2")

    # Step 3 fails -> Trigger Saga Compensation
    comp_saga = mgr.compensation_manager.execute_compensation(saga.saga_id)
    assert comp_saga.is_compensated is True
    assert comp_saga.steps[0].status == SagaStepStatus.COMPENSATED  # s1 compensated
    assert comp_saga.steps[1].status == SagaStepStatus.COMPENSATED  # s2 compensated


def test_flow_6_long_running_case():
    """FLOW 6 — Long-Running Case: Customer Onboarding case lifecycle & SLA escalation."""
    mgr = OrchestrationManager()

    case = mgr.case_manager.create_case("ACME Onboarding", case_type=CaseType.CUSTOMER_ONBOARDING, tenant_id="t_f6")
    assert case.status == CaseStatus.NEW

    task = mgr.human_task_manager.create_task("Verify KYC Documents", assigned_user_id="officer_1", tenant_id="t_f6", case_id=case.case_id)

    # SLA delayed -> Escalate task
    esc_task = mgr.human_task_manager.escalate_task(task.task_id, escalation_reason="KYC deadline missed")
    assert esc_task.status == TaskStatus.ESCALATED

    # Case updated
    upd_case = mgr.case_manager.update_status(case.case_id, CaseStatus.RESOLVED, reason="KYC verified after escalation")
    assert upd_case.status == CaseStatus.RESOLVED


def test_flow_7_cross_tenant_isolation():
    """FLOW 7 — Cross-Tenant Isolation: Tenant A workflow & case data inaccessible to Tenant B."""
    mgr = OrchestrationManager()

    # Tenant A Setup
    wf_A = mgr.definition_manager.create_definition("WF A", steps=[WorkflowStep(step_id="s1", name="S1")], tenant_id="Tenant_A")
    exec_A = mgr.execution_engine.start_execution(wf_A, tenant_id="Tenant_A")
    case_A = mgr.case_manager.create_case("Case A", tenant_id="Tenant_A")

    # Tenant B Setup
    wf_B = mgr.definition_manager.create_definition("WF B", steps=[WorkflowStep(step_id="s1", name="S1")], tenant_id="Tenant_B")
    exec_B = mgr.execution_engine.start_execution(wf_B, tenant_id="Tenant_B")
    case_B = mgr.case_manager.create_case("Case B", tenant_id="Tenant_B")

    # Verify zero cross-tenant leakage
    assert len(mgr.definition_manager.list_definitions("Tenant_A")) == 1
    assert len(mgr.definition_manager.list_definitions("Tenant_B")) == 1
    assert len(mgr.execution_engine.list_executions("Tenant_A")) == 1
    assert len(mgr.case_manager.list_cases("Tenant_A")) == 1


def test_flow_8_budget_aware_routing():
    """FLOW 8 — Budget-Aware Routing: FinOps cost limits route expensive tasks to cheaper workers."""
    mgr = OrchestrationManager()

    # Max budget < $0.50 -> Route to cheaper standard worker
    dec_cheap = mgr.execution_router.route_task("batch_translation", strategy=RoutingStrategy.COST_AWARE, max_budget=0.30)
    assert dec_cheap.target_type == "WORKER"
    assert dec_cheap.selected_target == "worker_cheaper_standard"

    # Max budget >= $1.00 -> Route to premium agent team
    dec_prem = mgr.execution_router.route_task("batch_translation", strategy=RoutingStrategy.COST_AWARE, max_budget=1.50)
    assert dec_prem.target_type == "TEAM"
    assert dec_prem.selected_target == "agent_premium_team"
