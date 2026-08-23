"""Mandatory End-to-End Integration Flows for Phase 5.22.

Tests 10 Mandatory E2E Flows:
Flow 1 — Enterprise AI Copilot
Flow 2 — High-Risk Application Action
Flow 3 — Feature Experiment
Flow 4 — Application Graceful Degradation
Flow 5 — Human Escalation
Flow 6 — Personalized Experience Isolation
Flow 7 — Feedback Improvement Loop
Flow 8 — Cross-Tenant Isolation
Flow 9 — Immutable Production Version Enforcement
Flow 10 — Runtime Cancellation & Timeout Propagation
"""

import pytest
from app.application_platform.manager import ApplicationPlatformManager
from app.application_platform.application import ApplicationType, ApplicationStatus, ApplicationConfiguration
from app.application_platform.composition import ComponentType
from app.application_platform.features import FeatureVariant, FeatureState, ExperimentState
from app.application_platform.personalization import ConsentScope, ConsentStatus
from app.application_platform.human_experience import EscalationReason
from app.application_platform.feedback import FeedbackType
from app.application_platform.resilience import DegradationStrategy
from app.application_platform.exceptions import (
    ApplicationNotFoundException,
    ImmutableVersionException,
    ExecutionCancelledException,
    GovernanceBlockedException,
)
from app.finops.cost_ledger import CostCategory


def test_e2e_flow_1_enterprise_ai_copilot():
    """FLOW 1 — Enterprise AI Copilot execution flow."""
    mgr = ApplicationPlatformManager()
    
    # 1. App resolution
    app = mgr.registry.create_application(
        tenant_id="t_copilot",
        name="Enterprise Support Copilot",
        app_type=ApplicationType.COPILOT,
    )
    ver = mgr.registry.create_version(app.application_id, "t_copilot", "1.0.0")
    mgr.registry.promote_version(ver.version_id, "t_copilot", ApplicationStatus.VALIDATED)
    mgr.registry.promote_version(ver.version_id, "t_copilot", ApplicationStatus.REVIEW)
    mgr.registry.promote_version(ver.version_id, "t_copilot", ApplicationStatus.APPROVED)
    mgr.registry.promote_version(ver.version_id, "t_copilot", ApplicationStatus.DEPLOYED)

    # 2. Execution
    ctx = mgr.runtime_manager.create_execution_context(
        tenant_id="t_copilot",
        application_id=app.application_id,
        application_version_id=ver.version_id,
        identity_id="user_john",
    )

    runtime = mgr.runtime_manager._active_executions[ctx.execution_id]
    exec_record = mgr.runtime_manager.create_execution_context("t_copilot", app.application_id, ver.version_id)
    
    # 3. Billing attribution
    mgr.billing_tracker.record_cost_event(
        tenant_id="t_copilot",
        application_id=app.application_id,
        application_version=ver.version_id,
        execution_id=ctx.execution_id,
        category=CostCategory.MODEL_INFERENCE,
        amount_usd=0.005,
    )

    assert mgr.billing_tracker.get_application_total_cost("t_copilot", app.application_id) == 0.005


def test_e2e_flow_2_high_risk_application_action():
    """FLOW 2 — High-Risk Application Action gated by ApprovalEngine."""
    mgr = ApplicationPlatformManager()

    dep = mgr.deployment_manager.create_deployment(
        application_id="app_privileged",
        version_id="ver_1",
        tenant_id="t_sec",
        environment="PRODUCTION",
        risk_level="HIGH",
    )

    assert dep.status == "AWAITING_APPROVAL"
    assert dep.approval_request_id is not None

    # Cannot execute before approval
    with pytest.raises(Exception):
        mgr.deployment_manager.execute_deployment(dep.deployment_id)

    # Approve
    mgr.deployment_manager.approval_engine.approve(dep.approval_request_id, approver_id="admin")
    executed = mgr.deployment_manager.execute_deployment(dep.deployment_id)

    assert executed.status == "SUCCESSFUL"


def test_e2e_flow_3_feature_experiment():
    """FLOW 3 — Feature Experiment with deterministic hash assignment."""
    mgr = ApplicationPlatformManager()

    variants = [
        FeatureVariant(variant_id="var_a", name="Variant A", weight_percentage=50.0),
        FeatureVariant(variant_id="var_b", name="Variant B", weight_percentage=50.0),
    ]

    mgr.feature_manager.create_experiment(
        tenant_id="t_exp",
        application_id="app_experiment",
        feature_key="ui_layout",
        variants=variants,
    )

    context_usr = {"user_id": "usr_999"}
    res1 = mgr.feature_manager.evaluate_feature("t_exp", "app_experiment", "ui_layout", context_usr)
    res2 = mgr.feature_manager.evaluate_feature("t_exp", "app_experiment", "ui_layout", context_usr)

    assert res1["variant"] == res2["variant"]
    assert res1["experiment_id"] is not None


def test_e2e_flow_4_graceful_degradation():
    """FLOW 4 — Application Graceful Degradation."""
    mgr = ApplicationPlatformManager()

    mgr.resilience_manager.register_fallback(
        tenant_id="t_res",
        application_id="app_critical",
        primary_target="claude-3-5-sonnet",
        fallback_target="claude-3-haiku",
        strategy=DegradationStrategy.MODEL_FALLBACK,
    )

    res = mgr.resilience_manager.resolve_target("t_res", "app_critical", "claude-3-5-sonnet", primary_failed=True)
    assert res["is_fallback"] is True
    assert res["target"] == "claude-3-haiku"


def test_e2e_flow_5_human_escalation():
    """FLOW 5 — Human Escalation."""
    mgr = ApplicationPlatformManager()

    esc = mgr.human_experience_manager.trigger_escalation(
        tenant_id="t_esc",
        application_id="app_loan",
        execution_id="exec_77",
        reason=EscalationReason.LOW_CONFIDENCE,
        details="Credit score calculation borderline",
    )

    assert esc.status == "OPEN"

    resolved = mgr.human_experience_manager.resolve_escalation(esc.escalation_id, "Approved after income verification")
    assert resolved.status == "RESOLVED"


def test_e2e_flow_6_personalized_experience_isolation():
    """FLOW 6 — Personalized Experience & Memory Isolation."""
    mgr = ApplicationPlatformManager()

    mgr.personalization_engine.set_profile("t_pers", "user_alice", {"theme": "DARK"})
    mgr.personalization_engine.set_profile("t_pers", "user_bob", {"theme": "LIGHT"})

    mgr.personalization_engine.grant_consent("t_pers", "user_alice", ConsentScope.USER_PROFILE, ConsentStatus.GRANTED)

    ctx_alice = mgr.personalization_engine.construct_experience_context("t_pers", "user_alice", "app_1")
    ctx_bob = mgr.personalization_engine.construct_experience_context("t_pers", "user_bob", "app_1")

    assert ctx_alice.allowed_preferences["theme"] == "DARK"
    assert ctx_bob.allowed_preferences == {}  # Bob has not granted consent


def test_e2e_flow_7_feedback_improvement_loop():
    """FLOW 7 — Feedback Improvement Loop."""
    mgr = ApplicationPlatformManager()

    fb = mgr.feedback_manager.submit_feedback(
        tenant_id="t_fb",
        application_id="app_support",
        execution_id="exec_11",
        feedback_type=FeedbackType.NEGATIVE,
        comment="Incorrect response formatting",
        corrected_output="Response should use bullet points.",
    )

    recs = mgr.feedback_manager.list_recommendations("t_fb", "app_support")
    assert len(recs) == 1
    assert recs[0].requires_approval is True
    assert recs[0].approved_by_governance is False  # No auto-production changes


def test_e2e_flow_8_cross_tenant_isolation():
    """FLOW 8 — Cross-Tenant Isolation."""
    mgr = ApplicationPlatformManager()

    app_tenant_a = mgr.registry.create_application("Tenant_A", "App A")

    # Tenant B access MUST be denied with ZERO leakage
    with pytest.raises(ApplicationNotFoundException):
        mgr.registry.get_application(app_tenant_a.application_id, tenant_id="Tenant_B")


def test_e2e_flow_9_immutable_production_version_enforcement():
    """FLOW 9 — Immutable Production Version Enforcement."""
    mgr = ApplicationPlatformManager()

    app = mgr.registry.create_application("t_imm", "App V1")
    v1 = mgr.registry.create_version(app.application_id, "t_imm", "1.0.0")

    # Promote v1 to DEPLOYED
    mgr.registry.promote_version(v1.version_id, "t_imm", ApplicationStatus.VALIDATED)
    mgr.registry.promote_version(v1.version_id, "t_imm", ApplicationStatus.REVIEW)
    mgr.registry.promote_version(v1.version_id, "t_imm", ApplicationStatus.APPROVED)
    mgr.registry.promote_version(v1.version_id, "t_imm", ApplicationStatus.DEPLOYED)

    # Attempting to modify v1 configuration MUST be rejected
    with pytest.raises(ImmutableVersionException):
        mgr.registry.update_version_configuration(v1.version_id, "t_imm", ApplicationConfiguration(environment="MUTATED"))

    # Correct workflow: Clone / Create v2
    v2 = mgr.registry.create_version(app.application_id, "t_imm", "2.0.0")
    assert v2.version == "2.0.0"
    assert v2.status == ApplicationStatus.DRAFT


def test_e2e_flow_10_runtime_cancellation_propagation():
    """FLOW 10 — Runtime Cancellation & Timeout Propagation."""
    mgr = ApplicationPlatformManager()

    ctx = mgr.runtime_manager.create_execution_context("t_canc", "app_long", "ver_1")

    # Propagate cancellation
    cancelled = mgr.runtime_manager.cancel_execution(ctx.execution_id, reason="Client timeout threshold reached")
    assert cancelled is True

    from app.application_platform.runtime import ApplicationRuntime
    runtime = ApplicationRuntime("app_long", "t_canc")
    exec_record = runtime.execute_pipeline(ctx, {"prompt": "Run computation"})

    assert exec_record.state == "CANCELLED"
    assert "Client timeout threshold reached" in exec_record.error
