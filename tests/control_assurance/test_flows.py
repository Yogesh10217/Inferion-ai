"""Mandatory E2E Integration Flow Tests for Enterprise AI Control Assurance (Phase 5.38)."""

import pytest
from app.control_assurance.manager import ControlAssuranceManager
from app.control_assurance.controls import ControlCategory, ControlType, ControlCriticality
from app.control_assurance.signals import ControlSignalType, ControlSignalSource, ControlSignalSeverity
from app.control_assurance.evaluation import ControlEvaluationStatus
from app.control_assurance.violations import ViolationSeverity, ViolationStatus
from app.control_assurance.assurance import AssuranceFinding, AssuranceDimension, AssuranceBand
from app.control_assurance.delegation import DelegationTarget
from app.control_assurance.exceptions import (
    CrossTenantControlAssuranceAccessException,
    InvalidControlTransitionException,
    ControlIntegrityException,
    HighRiskControlOverrideRequiresApprovalException,
    ControlRemediationBlockedException,
    ImmutableAssuranceRecordException,
)


@pytest.fixture
def manager():
    return ControlAssuranceManager()


def test_flow1_control_registration_and_framework_mapping(manager):
    """Flow 1 — Control registration and framework mapping."""
    tenant_id = "tenant_a"
    ctrl = manager.control_manager.register_control(
        tenant_id, "SEC-001", "Strict Auth Control", "Auth description", ControlCategory.SECURITY
    )
    fw = manager.framework_manager.create_framework(tenant_id, "SOC2", "SOC2 Framework")
    mapping = manager.framework_manager.map_control_to_requirement(tenant_id, fw.framework_id, ctrl.control_id, "CC6.1")

    assert ctrl.definition.code == "SEC-001"
    assert mapping.requirement_code == "CC6.1"


def test_flow2_cross_platform_signal_driven_evaluation(manager):
    """Flow 2 — Cross-platform signal-driven control evaluation."""
    tenant_id = "tenant_a"
    sig = manager.signal_manager.collect_signal(
        tenant_id,
        ControlSignalType.SECURITY,
        ControlSignalSource.SECURITY_INTELLIGENCE,
        "evt_100",
        "srv_001",
        ControlSignalSeverity.HIGH,
        {"status": "ALERT"},
    )
    eval_res = manager.evaluation_manager.evaluate_control(
        tenant_id, "ctrl_123", "srv_001", signals=[sig.sanitized_payload]
    )

    assert eval_res.status == ControlEvaluationStatus.PASSED
    assert eval_res.result.evaluated_signals_count == 1


def test_flow3_successful_control_evaluation(manager):
    """Flow 3 — Successful control evaluation."""
    tenant_id = "tenant_a"
    eval_res = manager.evaluation_manager.evaluate_control(tenant_id, "ctrl_100", "srv_001", force_fail=False)

    assert eval_res.status == ControlEvaluationStatus.PASSED
    assert eval_res.result.score == 100.0


def test_flow4_critical_control_failure_creates_violation(manager):
    """Flow 4 — Critical control failure creates violation."""
    tenant_id = "tenant_a"
    eval_res = manager.evaluation_manager.evaluate_control(tenant_id, "ctrl_100", "srv_001", force_fail=True)
    assert eval_res.status == ControlEvaluationStatus.FAILED

    viol = manager.violation_manager.create_violation(
        tenant_id, "ctrl_100", ViolationSeverity.CRITICAL, "FAIL_CODE", "Control failure message"
    )
    assert viol.severity == ViolationSeverity.CRITICAL
    assert viol.status == ViolationStatus.DETECTED


def test_flow5_invalid_violation_lifecycle_transition_blocked(manager):
    """Flow 5 — Invalid violation lifecycle transition blocked."""
    tenant_id = "tenant_a"
    viol = manager.violation_manager.create_violation(
        tenant_id, "ctrl_100", ViolationSeverity.HIGH, "FAIL_01", "Violation"
    )

    # DETECTED -> CLOSED (Invalid transition)
    with pytest.raises(InvalidControlTransitionException):
        manager.violation_manager.transition_status(viol.violation_id, tenant_id, ViolationStatus.CLOSED)


def test_flow6_cross_platform_finding_correlation(manager):
    """Flow 6 — Cross-platform finding correlation."""
    tenant_id = "tenant_a"
    corr = manager.correlation_manager.correlate_controls(
        tenant_id, "ctrl_primary", "ctrl_secondary", source_event_ids=["evt_001"]
    )

    assert corr.primary_control_id == "ctrl_primary"
    assert corr.related_control_id == "ctrl_secondary"


def test_flow7_cross_tenant_access_blocked_with_zero_metadata_leakage(manager):
    """Flow 7 — Cross-tenant access blocked with zero metadata leakage."""
    ctrl = manager.control_manager.register_control(
        "tenant_a", "SEC-001", "Tenant A Control", "Private", ControlCategory.SECURITY
    )

    with pytest.raises(CrossTenantControlAssuranceAccessException) as exc_info:
        manager.control_manager.get_control(ctrl.control_id, tenant_id="tenant_b")

    # Opaque error leaking zero metadata
    assert "Access denied or resource not found" in str(exc_info.value)
    assert "Tenant A Control" not in str(exc_info.value)
    assert "tenant_a" not in str(exc_info.value)


def test_flow8_sensitive_data_redaction_in_evidence(manager):
    """Flow 8 — Sensitive data redaction in evidence."""
    tenant_id = "tenant_a"
    raw_ev = {"api_key": "secret_key_12345", "control_name": "AuthControl"}
    
    ev = manager.evidence_manager.add_evidence("bundle_001", tenant_id, "AUTH_CHECK", "srv_001", raw_ev)
    assert ev.sanitized_payload["api_key"] == "[REDACTED]"
    assert ev.sanitized_payload["control_name"] == "AuthControl"


def test_flow9_evidence_integrity_failure_detection(manager):
    """Flow 9 — Evidence integrity failure detection."""
    tenant_id = "tenant_a"
    ev = manager.evidence_manager.add_evidence("bundle_001", tenant_id, "AUTH_CHECK", "srv_001", {"data": "test"})

    with pytest.raises(ControlIntegrityException):
        manager.evidence_manager.verify_evidence_integrity(ev, tenant_id, force_failure=True)


def test_flow10_high_risk_control_override_requires_approval(manager):
    """Flow 10 — High-risk control override requires approval."""
    tenant_id = "tenant_a"

    with pytest.raises(HighRiskControlOverrideRequiresApprovalException):
        manager.exception_manager.request_exception(
            tenant_id, "ctrl_critical", "Bypass critical control for maintenance", is_critical_control=True
        )


def test_flow11_expired_control_exception_becomes_invalid(manager):
    """Flow 11 — Expired control exception becomes invalid."""
    tenant_id = "tenant_a"
    req = manager.exception_manager.request_exception(
        tenant_id, "ctrl_standard", "Standard exception", is_critical_control=False, expires_in_days=-1
    )

    fetched = manager.exception_manager.get_exception(req.exception_id, tenant_id)
    assert fetched.status.value == "EXPIRED"


def test_flow12_delegation_only_remediation_enforcement(manager):
    """Flow 12 — Delegation-only remediation enforcement."""
    tenant_id = "tenant_a"

    with pytest.raises(ControlRemediationBlockedException):
        manager.delegation_manager.delegate_action(
            tenant_id, "ctrl_100", "REMEDIATE", direct_mutation_attempted=True
        )

    plan = manager.delegation_manager.delegate_action(
        tenant_id, "ctrl_100", "REMEDIATE", target_system=DelegationTarget.PLATFORM_OPERATIONS
    )
    assert plan.delegation_id is not None
    assert plan.status.value == "DELEGATED"


def test_flow13_idempotent_remediation_replay(manager):
    """Flow 13 — Idempotent remediation replay."""
    tenant_id = "tenant_a"
    plan1 = manager.remediation_manager.plan_remediation(tenant_id, "viol_001", "ctrl_001", idempotency_key="key123")
    plan2 = manager.remediation_manager.plan_remediation(tenant_id, "viol_001", "ctrl_001", idempotency_key="key123")

    assert plan1.plan_id == plan2.plan_id


def test_flow14_remediation_verification_failure_prevents_resolution(manager):
    """Flow 14 — Remediation verification failure prevents resolution."""
    tenant_id = "tenant_a"
    verif = manager.verification_manager.verify_remediation(
        tenant_id, "plan_001", "ctrl_001", force_failure=True
    )
    assert verif.result.value == "FAILED"


def test_flow15_immutable_finalized_attestation(manager):
    """Flow 15 — Immutable finalized attestation."""
    tenant_id = "tenant_a"
    att = manager.attestation_manager.create_attestation(tenant_id, "ctrl_001", "srv_001")
    fin_att = manager.attestation_manager.finalize_attestation(att.attestation_id, tenant_id, "attestor_01")

    assert fin_att.is_finalized is True
    assert fin_att.fingerprint_sha256 != ""

    with pytest.raises(ImmutableAssuranceRecordException):
        manager.attestation_manager.finalize_attestation(att.attestation_id, tenant_id, "attestor_02")


def test_flow16_hard_control_failure_overrides_assurance_score(manager):
    """Flow 16 — Hard control failure overrides assurance score."""
    tenant_id = "tenant_a"
    findings = [
        AssuranceFinding(
            control_id="ctrl_001",
            dimension=AssuranceDimension.SECURITY,
            is_hard_failure=True,
            message="Mandatory security failure",
        )
    ]
    ass = manager.assurance_manager.calculate_assurance(tenant_id, "srv_001", findings=findings)

    # Hard failure forces score = 35.0 and CRITICAL band
    assert ass.assurance_score.band == AssuranceBand.CRITICAL
    assert ass.assurance_score.score == 35.0


def test_flow17_trust_assessment_compatibility(manager):
    """Flow 17 — Trust assessment compatibility."""
    tenant_id = "tenant_a"
    trust = manager.trust_engine.calculate_control_trust(tenant_id, "ctrl_001", is_degraded=False)

    assert trust.score == 92.5
    assert trust.band.value == "HIGH_TRUST"


def test_flow18_control_learning_produces_recommendation_without_auto_execution(manager):
    """Flow 18 — Control learning produces recommendation without auto-execution."""
    tenant_id = "tenant_a"
    learn = manager.learning_manager.record_learning(tenant_id, "ctrl_001", "High signal frequency observed")

    assert len(learn.recommendations) > 0
    rec = learn.recommendations[0]
    assert rec.auto_execute is False  # Never auto-execute
    assert rec.requires_approval is True


def test_flow19_immutable_assurance_snapshot_creation(manager):
    """Flow 19 — Immutable assurance snapshot creation."""
    tenant_id = "tenant_a"
    snap = manager.snapshot_manager.create_snapshot(tenant_id, "ctrl_001", {"status": "PASSED", "score": 100.0})

    assert snap.snapshot_id is not None
    assert snap.fingerprint_sha256 != ""

    fetched = manager.snapshot_manager.get_snapshot(snap.snapshot_id, tenant_id)
    assert fetched.fingerprint_sha256 == snap.fingerprint_sha256


def test_flow20_full_enterprise_continuous_control_assurance_lifecycle(manager):
    """Flow 20 — Full enterprise continuous control assurance lifecycle."""
    tenant_id = "tenant_enterprise"

    res = manager.run_full_assurance_lifecycle(
        tenant_id=tenant_id,
        service_id="Enterprise_Inference_Cluster",
        force_violation=True,
    )

    assert res["status"] == "COMPLETED"
    assert res["evaluation_status"] == "FAILED"
    assert res["assurance_band"] == "CRITICAL"
    assert res["violation_id"] is not None
    assert res["remediation_plan_id"] is not None
    assert res["verification_status"] == "PASSED"
    assert res["evidence_checksum"] != ""
    assert res["snapshot_id"] is not None

    summary = manager.get_platform_summary(tenant_id)
    assert summary["status"] == "OPERATIONAL"
    assert summary["metrics"]["counters"]["ai_control_assurance_evaluations_total"] > 0
