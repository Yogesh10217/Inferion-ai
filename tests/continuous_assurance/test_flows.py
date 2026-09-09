"""Mandatory 20 End-to-End Test Flows for Continuous Assurance (Phase 5.54)."""

import pytest
from app.continuous_assurance.manager import ContinuousAssuranceManager
from app.continuous_assurance.exceptions import (
    CrossTenantContinuousAssuranceException,
    HighRiskContinuousAssuranceActionRequiresApprovalException,
    ImmutableContinuousAssuranceRecordException,
    FeedbackLoopException,
    InvalidContinuousAssuranceStateTransitionException,
)
from app.continuous_assurance.models import (
    AssuranceLifecycleState,
    ControlEffectivenessStatus,
    DriftType,
    VerificationStatus,
)


@pytest.fixture
def manager():
    return ContinuousAssuranceManager()


def test_flow_01_observation_ingestion_tenant_isolation(manager):
    """Flow 01: Runtime observation ingestion and tenant isolation."""
    tenant1 = "tenant_alpha"
    tenant2 = "tenant_beta"

    obs1 = manager.record_observation(tenant1, "security", "SECURITY_EVENT", {"ip": "10.0.0.1"})
    obs2 = manager.record_observation(tenant2, "operations", "OPERATIONAL_EVENT", {"cpu": 95})

    assert obs1.tenant_id == tenant1
    assert obs2.tenant_id == tenant2

    fetched = manager.get_observation(tenant1, obs1.observation_id)
    assert fetched.observation_id == obs1.observation_id


def test_flow_02_cross_tenant_access_blocked(manager):
    """Flow 02: Cross-tenant access blocked with zero metadata leakage."""
    obs = manager.record_observation("tenant_a", "security", "SECURITY_EVENT", {"secret": "12345"})

    with pytest.raises(CrossTenantContinuousAssuranceException) as exc_info:
        manager.get_observation("tenant_b", obs.observation_id)

    # Expose zero metadata or identifier in exception message
    assert "tenant_a" not in str(exc_info.value)
    assert obs.observation_id not in str(exc_info.value)


def test_flow_03_observation_normalization(manager):
    """Flow 03: Cross-domain runtime observation normalization."""
    obs = manager.record_observation("tenant_norm", "identity", "IDENTITY_EVENT", {"token": "secret_abc", "user": "admin"})
    normalized = manager.obs_normalizer.normalize(obs)

    assert normalized.tenant_id == "tenant_norm"
    assert normalized.source_domain == "identity"
    # Ensure sensitive data sanitizer redacted the token
    assert normalized.clean_payload.get("token") == "[REDACTED]"


def test_flow_04_continuous_assurance_assessment(manager):
    """Flow 04: Continuous assurance assessment generation."""
    tenant = "tenant_assess"
    ass = manager.evaluate_tenant_assurance(tenant)

    assert ass.tenant_id == tenant
    assert 0.0 <= ass.score.overall_score <= 1.0
    assert ass.state in (AssuranceLifecycleState.STABLE, AssuranceLifecycleState.DEGRADED)


def test_flow_05_assurance_lifecycle_transitions(manager):
    """Flow 05: Assurance lifecycle state transitions."""
    from app.continuous_assurance.assurance_lifecycle import AssuranceLifecycleMachine

    # Valid transition
    AssuranceLifecycleMachine.validate_transition(AssuranceLifecycleState.INITIALIZING, AssuranceLifecycleState.MONITORING)

    # Invalid transition raises InvalidContinuousAssuranceStateTransitionException
    with pytest.raises(InvalidContinuousAssuranceStateTransitionException):
        AssuranceLifecycleMachine.validate_transition(AssuranceLifecycleState.INITIALIZING, AssuranceLifecycleState.RESTORED)


def test_flow_06_control_effectiveness_evaluation(manager):
    """Flow 06: Control effectiveness evaluation."""
    tenant = "tenant_ctrl"
    ctrl = manager.evaluate_control(tenant, "ctrl_access_policy", {"pass_rate": 0.95})

    assert ctrl.control_id == "ctrl_access_policy"
    assert ctrl.status == ControlEffectivenessStatus.EFFECTIVE
    assert ctrl.score == 0.95


def test_flow_07_control_validation(manager):
    """Flow 07: Control validation."""
    tenant = "tenant_val"
    ctrl = manager.evaluate_control(tenant, "ctrl_val_01", {"pass_rate": 0.85})
    res = manager.ctrl_validator.validate_control(ctrl)

    assert res["is_valid"] is True
    assert res["coverage_complete"] is True


def test_flow_08_policy_drift_detection(manager):
    """Flow 08: Policy drift detection."""
    tenant = "tenant_policy"
    expected = {"max_session_hours": 8, "mfa_required": True}
    runtime = {"max_session_hours": 24, "mfa_required": True}

    drift = manager.policy_drift_analyzer.analyze_policy_drift(tenant, expected, runtime)
    assert drift.drift_type == DriftType.POLICY
    assert "max_session_hours" in drift.difference_summary


def test_flow_09_risk_drift_detection(manager):
    """Flow 09: Risk drift detection."""
    tenant = "tenant_risk"
    drift = manager.risk_drift_analyzer.analyze_risk_drift(tenant, baseline_risk=0.10, current_risk=0.45)

    assert drift.drift_type == DriftType.RISK
    assert "Critical risk drift" in drift.difference_summary or "Elevated risk drift" in drift.difference_summary


def test_flow_10_trust_drift_detection(manager):
    """Flow 10: Trust drift detection."""
    tenant = "tenant_trust"
    drift = manager.trust_drift_analyzer.analyze_trust_drift(tenant, expected_trust=0.95, observed_trust=0.70)

    assert drift.drift_type == DriftType.TRUST
    assert "trust degradation" in drift.difference_summary.lower()


def test_flow_11_runtime_behavior_anomaly_detection(manager):
    """Flow 11: Runtime behavior anomaly detection."""
    tenant = "tenant_behavior"
    expected = {"api_rate": 100, "auth_method": "OAUTH2"}
    observed = {"api_rate": 5000, "auth_method": "NONE"}

    res = manager.behavior_analyzer.analyze_behavior(tenant, expected, observed)
    assert res["is_anomalous"] is True
    assert res["deviation_count"] == 2


def test_flow_12_versioned_baseline_comparison(manager):
    """Flow 12: Versioned baseline comparison."""
    tenant = "tenant_base"
    b1 = manager.baseline_engine.create_baseline(tenant, {"security": 0.95})
    b2 = manager.baseline_engine.create_baseline(tenant, {"security": 0.98})

    assert b1.version == 1
    assert b2.version == 2
    latest = manager.baseline_engine.get_latest_baseline(tenant)
    assert latest.version == 2


def test_flow_13_continuous_verification(manager):
    """Flow 13: Continuous verification."""
    tenant = "tenant_ver"
    hash_exp = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    v_success = manager.verify_resource(tenant, "res_01", hash_exp, hash_exp)
    assert v_success.status == VerificationStatus.VERIFIED

    v_fail = manager.verify_resource(tenant, "res_01", hash_exp, "invalid_hash")
    assert v_fail.status == VerificationStatus.FAILED


def test_flow_14_feedback_loop_bounded_execution(manager):
    """Flow 14: Feedback loop bounded execution (verify max iteration enforcement)."""
    tenant = "tenant_loop"
    cycle_key = "test_feedback_loop"

    for i in range(5):
        manager.feedback_engine.process_feedback_cycle(tenant, cycle_key)

    with pytest.raises(FeedbackLoopException):
        manager.feedback_engine.process_feedback_cycle(tenant, cycle_key)


def test_flow_15_adaptive_recommendation_advisory_only(manager):
    """Flow 15: Adaptive recommendation is advisory only (auto_execute = False)."""
    tenant = "tenant_rec"
    rec = manager.create_recommendation(tenant, "ctrl_mfa", "Enforce step-up MFA")

    assert rec.auto_execute is False


def test_flow_16_high_risk_action_requires_approval(manager):
    """Flow 16: High-risk action requires human approval."""
    tenant = "tenant_gov"

    res = manager.evaluate_governance(tenant, "restart_service", risk_level="HIGH")
    assert res["requires_approval"] is True
    assert res["outcome"] == "REQUIRE_APPROVAL"

    # Enforcing check without approval raises exception
    with pytest.raises(HighRiskContinuousAssuranceActionRequiresApprovalException):
        manager.governance_engine.enforce_approval_check(tenant, "restart_service", is_approved=False)


def test_flow_17_delegation_only_execution_enforcement(manager):
    """Flow 17: Delegation-only execution enforcement (zero direct external mutation)."""
    tenant = "tenant_del"
    delegation = manager.create_delegation(tenant, "rotate_credential", {"credential_id": "cred_01"})

    assert delegation["request_id"].startswith("del_req_")
    assert delegation["auto_executed"] is False
    assert delegation["action_name"] == "rotate_credential"


def test_flow_18_recovery_assurance_verification(manager):
    """Flow 18: Recovery assurance verification."""
    tenant = "tenant_recovery"
    res = manager.recovery_engine.verify_recovery(tenant, "plan_01", pre_score=0.60, post_score=0.92)

    assert res["is_restored"] is True
    assert res["status"] == "RESTORED"
    assert res["score_improvement"] == 0.32


def test_flow_19_immutable_sha256_evidence_verification(manager):
    """Flow 19: Immutable SHA-256 evidence verification."""
    tenant = "tenant_ev"
    bundle = manager.evidence_manager.create_evidence_bundle(tenant, "ass_01", ["obs_01", "obs_02"])

    assert bundle.is_sealed is True
    assert len(bundle.integrity_hash) == 64

    # Modification attempts raise ImmutableContinuousAssuranceRecordException
    with pytest.raises(ImmutableContinuousAssuranceRecordException):
        manager.evidence_manager.modify_sealed_bundle(bundle.evidence_id)


def test_flow_20_full_continuous_closed_loop_lifecycle(manager):
    """Flow 20: Full enterprise continuous assurance closed-loop lifecycle."""
    tenant = "tenant_enterprise_full"

    # 1. Observation Ingestion & Normalization
    obs = manager.record_observation(tenant, "security", "SECURITY_EVENT", {"ip": "192.168.1.100"}, severity="HIGH")
    normalized = manager.obs_normalizer.normalize(obs)
    assert normalized.confidence > 0.9

    # 2. Assurance Assessment
    ass = manager.evaluate_tenant_assurance(tenant)
    assert ass.state in (AssuranceLifecycleState.STABLE, AssuranceLifecycleState.DEGRADED)

    # 3. Control Evaluation
    ctrl = manager.evaluate_control(tenant, "ctrl_firewall_rule", {"pass_rate": 0.65})
    assert ctrl.status == ControlEffectivenessStatus.DEGRADED

    # 4. Drift & Anomaly Detection
    drift = manager.analyze_drift(tenant, "SECURITY", {"firewall": "STRICT"}, {"firewall": "PERMISSIVE"})
    anomalies = manager.anomaly_detector.detect_anomalies([obs])
    assert len(anomalies) > 0

    # 5. Recommendation Generation
    rec = manager.create_recommendation(tenant, "ctrl_firewall_rule", "Re-apply STRICT firewall posture")
    assert rec.auto_execute is False

    # 6. Governance & Human Approval
    gov = manager.evaluate_governance(tenant, "change_infrastructure", risk_level="HIGH")
    assert gov["requires_approval"] is True

    # 7. Delegation Request Creation
    delegation = manager.create_delegation(tenant, "change_infrastructure", {"rule": "STRICT"})
    assert delegation["request_id"].startswith("del_req_")

    # 8. Post-Remediation Verification & Recovery Assurance
    expected_hash = "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
    ver = manager.verify_resource(tenant, "firewall_rule_01", expected_hash, expected_hash)
    assert ver.status == VerificationStatus.VERIFIED

    rec_res = manager.recovery_assurance_engine.verify_recovery(tenant, "plan_fw_01", pre_score=0.65, post_score=0.95)
    assert rec_res["is_restored"] is True

    # 9. Immutable Evidence & Lineage Graph
    evidence = manager.evidence_manager.create_evidence_bundle(tenant, ass.assessment_id, [obs.observation_id])
    assert evidence.is_sealed is True

    manager.evidence_lineage.add_lineage_link(obs.observation_id, ass.assessment_id)
    manager.evidence_lineage.add_lineage_link(ass.assessment_id, drift.drift_id)
    lineage = manager.evidence_lineage.get_lineage(obs.observation_id)
    assert len(lineage) == 3

    # 10. Feedback Cycle
    fb = manager.feedback_engine.process_feedback_cycle(tenant, "full_lifecycle_loop")
    assert fb["status"] == "FEEDBACK_PROCESSED"
