"""Mandatory E2E Integration Flow Tests for Enterprise AI Agent Orchestration Platform (Phase 5.36)."""

import pytest

from app.agent_orchestration.agents import AgentRole, AgentType
from app.agent_orchestration.autonomy import AgentAutonomyLevel, AutonomyBoundary
from app.agent_orchestration.capabilities import CapabilityScope
from app.agent_orchestration.collaboration import AgentParticipant, CollaborationType
from app.agent_orchestration.exceptions import (
    AgentBudgetExceededException,
    AgentCapabilityViolationException,
    AgentRuntimeLimitExceededException,
    AgentToolAccessDeniedException,
    CrossTenantAgentAccessException,
    HighRiskAgentActionRequiresApprovalException,
    ImmutableAgentExecutionException,
)
from app.agent_orchestration.failures import AgentFailureSeverity, AgentFailureType
from app.agent_orchestration.manager import AgentOrchestrationManager


@pytest.fixture
def manager():
    return AgentOrchestrationManager()


def test_flow1_agent_registration_and_capability_validation(manager):
    """Flow 1: Agent registration and capability validation."""
    tenant_id = "tenant_a"
    cap = manager.capability_manager.register_capability(
        tenant_id=tenant_id,
        name="DeployAppCapability",
        scopes={CapabilityScope.READ, CapabilityScope.ANALYZE, CapabilityScope.EXECUTE_WITH_APPROVAL},
    )

    agent = manager.agent_manager.register_agent(
        tenant_id=tenant_id,
        name="Deployment Agent",
        agent_type=AgentType.EXECUTOR,
        role=AgentRole.TASK_EXECUTOR,
        capabilities=[cap.capability_id],
    )

    assert agent.name == "Deployment Agent"
    assert cap.capability_id in agent.capabilities

    valid = manager.capability_manager.validate_agent_capabilities(
        agent_capabilities=agent.capabilities,
        tenant_id=tenant_id,
        required_scope=CapabilityScope.READ,
    )
    assert valid is True


def test_flow2_unauthorized_capability_attempt_blocked(manager):
    """Flow 2: Unauthorized capability attempt -> BLOCKED."""
    tenant_id = "tenant_a"
    cap = manager.capability_manager.register_capability(
        tenant_id=tenant_id,
        name="ReadOnlyCap",
        scopes={CapabilityScope.READ},
    )

    agent = manager.agent_manager.register_agent(
        tenant_id=tenant_id,
        name="Read Agent",
        agent_type=AgentType.ANALYST,
        capabilities=[cap.capability_id],
    )

    with pytest.raises(AgentCapabilityViolationException):
        manager.capability_manager.validate_agent_capabilities(
            agent_capabilities=agent.capabilities,
            tenant_id=tenant_id,
            required_scope=CapabilityScope.EXECUTE_WITH_APPROVAL,
        )


def test_flow3_agent_autonomy_boundary_exceeded_blocked(manager):
    """Flow 3: Agent autonomy boundary exceeded -> BLOCKED."""
    tenant_id = "tenant_a"
    policy = manager.autonomy_manager.set_autonomy_policy(
        tenant_id=tenant_id,
        agent_id="agent_strict",
        autonomy_level=AgentAutonomyLevel.SUPERVISED,
        boundary=AutonomyBoundary(spending_limit_dollars=50.0, max_steps=10),
    )

    eval_res = manager.autonomy_manager.evaluate_action_autonomy(
        policy=policy,
        proposed_action="deploy_large_cluster",
        target_system="PLATFORM_OPERATIONS",
        cost_dollars=200.0,  # Exceeds $50.0
    )

    assert eval_res.is_allowed is False
    assert len(eval_res.violations) > 0
    assert eval_res.violations[0].violation_type == "SPENDING_LIMIT_EXCEEDED"


def test_flow4_task_planning_using_governed_context(manager):
    """Flow 4: Task planning using governed context."""
    tenant_id = "tenant_a"
    agent = manager.agent_manager.register_agent(tenant_id=tenant_id, name="Planner Agent")

    manager.context_manager.assemble_context(
        tenant_id=tenant_id,
        agent_id=agent.agent_id,
        task_id="task_plan_demo",
        query="optimize database indexing",
    )

    plan = manager.planning_engine.create_plan(
        tenant_id=tenant_id,
        task_id="task_plan_demo",
        agent_id=agent.agent_id,
        goal="Optimize DB indexing",
    )

    assert plan.plan_id is not None
    assert len(plan.steps) > 0
    assert plan.evaluation.is_feasible is True


def test_flow5_tool_access_denied_due_to_policy(manager):
    """Flow 5: Tool access denied due to policy."""
    tenant_id = "tenant_a"
    tool = manager.tool_governance_manager.register_tool(
        tenant_id=tenant_id,
        name="SecretKeyVaultTool",
        data_classification="RESTRICTED",
    )

    with pytest.raises(AgentToolAccessDeniedException):
        manager.tool_governance_manager.authorize_tool_invocation(
            tool_id=tool.tool_id,
            agent_id="agent_123",
            tenant_id=tenant_id,
            task_id="task_456",
            agent_capabilities=["READ"],
            data_classification_allowed=["PUBLIC", "INTERNAL"],  # RESTRICTED not allowed
        )


def test_flow6_high_risk_agent_action_requires_approval(manager):
    """Flow 6: High-risk agent action -> Approval Required."""
    tenant_id = "tenant_a"
    agent = manager.agent_manager.register_agent(tenant_id=tenant_id, name="Risk Agent")

    with pytest.raises(HighRiskAgentActionRequiresApprovalException):
        manager.run_full_agent_task_lifecycle(
            tenant_id=tenant_id,
            goal="Release production build",
            prompt="RELEASE production build",
            agent_id=agent.agent_id,
            is_destructive=True,
        )


def test_flow7_supervisor_worker_collaboration(manager):
    """Flow 7: Supervisor-worker collaboration."""
    tenant_id = "tenant_a"
    sup = manager.agent_manager.register_agent(tenant_id=tenant_id, name="Supervisor", agent_type=AgentType.SUPERVISOR)
    wrk = manager.agent_manager.register_agent(tenant_id=tenant_id, name="Worker", agent_type=AgentType.EXECUTOR)

    sess = manager.collaboration_manager.create_session(
        tenant_id=tenant_id,
        collaboration_type=CollaborationType.SUPERVISOR_WORKER,
        participants=[
            AgentParticipant(agent_id=sup.agent_id, tenant_id=tenant_id, role="SUPERVISOR"),
            AgentParticipant(agent_id=wrk.agent_id, tenant_id=tenant_id, role="WORKER"),
        ],
    )

    msg = manager.collaboration_manager.send_message(
        session_id=sess.session_id,
        tenant_id=tenant_id,
        sender_agent_id=sup.agent_id,
        recipient_agent_id=wrk.agent_id,
        message_type="INSTRUCTION",
        content={"task": "Run system diagnostic"},
    )

    dec = manager.collaboration_manager.finalize_decision(
        session_id=sess.session_id,
        tenant_id=tenant_id,
        selected_action="Run system diagnostic",
    )

    assert msg.message_id is not None
    assert dec.status.value == "COMPLETED"


def test_flow8_cross_tenant_agent_access_blocked(manager):
    """Flow 8: Cross-tenant agent access -> BLOCKED with zero metadata leakage."""
    ag_a = manager.agent_manager.register_agent(tenant_id="tenant_a", name="Tenant A Agent")

    with pytest.raises(CrossTenantAgentAccessException) as exc_info:
        manager.agent_manager.get_agent(ag_a.agent_id, tenant_id="tenant_b")

    # Assert opaque message with zero metadata leakage
    assert "Access denied or resource not found" in str(exc_info.value)
    assert ag_a.name not in str(exc_info.value)
    assert "tenant_a" not in str(exc_info.value)


def test_flow9_delegation_only_enforcement(manager):
    """Flow 9: Delegation-only enforcement."""
    tenant_id = "tenant_a"
    del_req = manager.delegation_manager.create_delegation_request(
        tenant_id=tenant_id,
        target="PLATFORM_OPERATIONS",
        action="provision_resource",
        payload={"memory": "4GB"},
    )

    assert del_req.delegation_id is not None
    res = manager.delegation_manager.simulate_delegated_execution(del_req.delegation_id, tenant_id)
    assert res.status.value == "COMPLETED"


def test_flow10_runtime_max_step_safeguard(manager):
    """Flow 10: Runtime max-step safeguard stops looping execution."""
    tenant_id = "tenant_a"
    sess = manager.runtime_manager.create_session(tenant_id=tenant_id, agent_id="ag1", execution_id="ex1")

    with pytest.raises(AgentRuntimeLimitExceededException):
        # Simulate infinite loop repeating identical action 4 times
        for _ in range(5):
            manager.runtime_manager.record_step(sess.session_id, tenant_id, action_name="stuck_action")


def test_flow11_runtime_budget_exceeded(manager):
    """Flow 11: Runtime budget exceeded -> BLOCKED."""
    tenant_id = "tenant_a"
    sess = manager.runtime_manager.create_session(tenant_id=tenant_id, agent_id="ag1", execution_id="ex1")

    with pytest.raises(AgentBudgetExceededException):
        manager.runtime_manager.record_step(sess.session_id, tenant_id, action_name="costly_action", cost=500.0)


def test_flow12_execution_verification_failure_and_recovery(manager):
    """Flow 12: Execution verification failure -> Recovery or escalation."""
    tenant_id = "tenant_a"
    rec_plan = manager.recovery_manager.formulate_recovery(
        tenant_id=tenant_id,
        execution_id="exec_failed",
        task_id="task_failed",
        failure_reason="Execution output verification failed",
        is_unsafe_for_auto_recovery=True,
    )

    assert rec_plan.strategy.value == "ESCALATE_HUMAN"
    assert rec_plan.status.value == "ESCALATED"


def test_flow13_agent_failure_creates_signals(manager):
    """Flow 13: Agent failure creates reliability/event intelligence signal."""
    tenant_id = "tenant_a"
    fail = manager.failure_analyzer.record_failure(
        tenant_id=tenant_id,
        agent_id="ag_failed",
        task_id="task_failed",
        failure_type=AgentFailureType.POLICY_VIOLATION,
        error_message="Policy breached during execution",
        severity=AgentFailureSeverity.HIGH,
    )

    assert fail.failure_id is not None
    assert fail.reliability_signal_emitted is True
    assert fail.event_emitted is True


def test_flow14_immutable_finalized_execution_trace(manager):
    """Flow 14: Immutable finalized execution trace."""
    tenant_id = "tenant_a"
    trace = manager.trace_manager.start_trace(tenant_id=tenant_id, agent_id="ag1", task_id="task1")

    manager.trace_manager.record_step(
        trace.trace_id, tenant_id, action_type="STEP_1", outcome_summary="Step 1 complete"
    )
    final = manager.trace_manager.finalize_trace(trace.trace_id, tenant_id)

    assert final.fingerprint != ""
    assert final.snapshot_id is not None

    with pytest.raises(ImmutableAgentExecutionException):
        manager.trace_manager.record_step(
            trace.trace_id, tenant_id, action_type="STEP_2", outcome_summary="Illegal step"
        )


def test_flow15_trust_assessment_compatibility(manager):
    """Flow 15: Trust assessment compatibility."""
    tenant_id = "tenant_a"
    trust = manager.trust_engine.calculate_agent_trust(
        tenant_id=tenant_id,
        agent_id="agent_trusted",
        success_count=20,
        failure_count=0,
    )

    assert trust.score >= 90.0
    assert trust.band.value == "HIGH_TRUST"
    assert trust.subject_type == "ENTERPRISE_AGENT"


def test_flow16_sensitive_data_redaction_in_traces(manager):
    """Flow 16: Sensitive data redaction in traces and logs."""
    tenant_id = "tenant_a"
    trace = manager.trace_manager.start_trace(tenant_id=tenant_id, agent_id="ag1", task_id="task1")

    raw_event = {"username": "admin", "api_key": "secret_token_12345", "password": "supersecretpassword"}
    manager.trace_manager.record_step(
        trace_id=trace.trace_id,
        tenant_id=tenant_id,
        action_type="LOG_EVENT",
        raw_event_details=raw_event,
    )

    ev = trace.events[0]
    assert ev.details_sanitized["api_key"] == "[REDACTED]"
    assert ev.details_sanitized["password"] == "[REDACTED]"
    assert ev.details_sanitized["username"] == "admin"


def test_flow17_fallback_agent_routing(manager):
    """Flow 17: Fallback agent routing after primary failure."""
    tenant_id = "tenant_a"
    rec_plan = manager.recovery_manager.formulate_recovery(
        tenant_id=tenant_id,
        execution_id="exec_123",
        task_id="task_123",
        failure_reason="Primary agent failed",
        fallback_agent_id="agent_fallback_backup",
    )

    assert rec_plan.strategy.value == "FALLBACK_AGENT"
    assert rec_plan.actions[0].target_agent_id == "agent_fallback_backup"


def test_flow18_human_escalation_when_recovery_unsafe(manager):
    """Flow 18: Human escalation when recovery is unsafe."""
    tenant_id = "tenant_a"
    rec_plan = manager.recovery_manager.formulate_recovery(
        tenant_id=tenant_id,
        execution_id="exec_critical",
        task_id="task_critical",
        failure_reason="Data inconsistency detected during destructive recovery",
        is_unsafe_for_auto_recovery=True,
    )

    assert rec_plan.strategy.value == "ESCALATE_HUMAN"
    assert rec_plan.status.value == "ESCALATED"


def test_flow19_agent_learning_does_not_auto_expand_autonomy(manager):
    """Flow 19: Agent learning recommendation does not automatically increase autonomy."""
    tenant_id = "tenant_a"
    record = manager.learning_manager.record_execution_learning(
        tenant_id=tenant_id,
        agent_id="ag1",
        execution_id="exec1",
        is_successful=True,
        cost_dollars=0.01,
    )

    assert len(record.recommendations) > 0
    rec = [r for r in record.recommendations if r.affects_autonomy][0]
    assert rec.requires_governance is True
    assert rec.status == "PENDING_GOVERNANCE_REVIEW"


def test_flow20_full_enterprise_multi_agent_lifecycle(manager):
    """Flow 20: Full enterprise multi-agent lifecycle."""
    tenant_id = "tenant_enterprise"

    res = manager.run_full_agent_task_lifecycle(
        tenant_id=tenant_id,
        goal="Run comprehensive platform health audit",
        prompt="Analyze system components and report health metrics",
    )

    assert res["status"] == "COMPLETED"
    assert res["fingerprint"] != ""
    assert res["snapshot_id"] is not None

    summary = manager.get_platform_summary(tenant_id)
    assert summary["status"] == "OPERATIONAL"
    assert summary["metrics"]["ai_agents_tasks_total"] > 0
