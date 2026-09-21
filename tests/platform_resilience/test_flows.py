"""Mandatory E2E Integration Flow Tests for Enterprise AI Platform Resilience (Phase 5.37)."""

import pytest

from app.platform_resilience.chaos import ExperimentRisk, ExperimentScenario
from app.platform_resilience.circuit_breakers import CircuitBreakerState
from app.platform_resilience.degradation import DegradationLevel
from app.platform_resilience.dependencies import DependencyCriticality, DependencyType
from app.platform_resilience.disaster_recovery import DisasterRecoveryScenario, DisasterRecoveryStatus
from app.platform_resilience.exceptions import (
    BulkheadCapacityExceededException,
    CrossTenantResilienceAccessException,
    HighRiskRecoveryRequiresApprovalException,
    ImmutableResilienceRecordException,
    InvalidFailoverTransitionException,
    RecoveryVerificationFailedException,
)
from app.platform_resilience.failover import FailoverPlan, FailoverStatus
from app.platform_resilience.manager import PlatformResilienceManager
from app.platform_resilience.readiness import ReadinessDimension, ReadinessRequirement
from app.platform_resilience.runbooks import RunbookStep, RunbookTrigger
from app.platform_resilience.scaling import ScalingDirection


@pytest.fixture
def manager():
    return PlatformResilienceManager()


def test_flow1_dependency_failure_detection(manager):
    """Flow 1 — Dependency Failure Detection."""
    tenant_id = "tenant_a"
    manager.dependency_manager.register_dependency(
        tenant_id, "InferenceService", "AuthService", DependencyType.HARD, DependencyCriticality.CRITICAL
    )

    impact = manager.dependency_manager.evaluate_failure_impact(tenant_id, "AuthService")
    assert "InferenceService" in impact.affected_services
    assert impact.cascade_risk_score > 0.0


def test_flow2_capacity_saturation(manager):
    """Flow 2 — Capacity Saturation."""
    tenant_id = "tenant_a"
    eval_res = manager.capacity_manager.evaluate_capacity(tenant_id, "cluster_01")
    forecast = manager.capacity_manager.forecast_capacity(tenant_id, "cluster_01", hours=24)

    assert eval_res.status.value == "NORMAL"
    assert forecast.timeframe_hours == 24


def test_flow3_backpressure_protection(manager):
    """Flow 3 — Backpressure Protection."""
    tenant_id = "tenant_a"
    bp = manager.backpressure_manager.evaluate_backpressure(tenant_id, "InferenceService", current_queue_depth=1200)
    assert bp.level.value == "CRITICAL"
    assert bp.recommended_action.value == "REJECT"
    assert bp.is_protection_active is True


def test_flow4_load_shedding_priority(manager):
    """Flow 4 — Load Shedding Priority."""
    tenant_id = "tenant_a"
    workloads = [
        {"name": "CriticalInferenceWorkload", "priority": 0},
        {"name": "BatchAnalyticsWorkload", "priority": 3},
        {"name": "ReportingWorkload", "priority": 2},
    ]

    plan = manager.load_shedding_manager.formulate_shedding_plan(tenant_id, "CoreService", workloads)
    assert "BatchAnalyticsWorkload" in plan.shedding_targets
    assert "CriticalInferenceWorkload" in plan.protected_workloads


def test_flow5_circuit_breaker_lifecycle(manager):
    """Flow 5 — Circuit Breaker Lifecycle."""
    tenant_id = "tenant_a"
    cb = manager.circuit_breaker_manager.get_or_create_breaker(tenant_id, "ExternalAPI")

    # Invalid transition CLOSED -> HALF_OPEN should fail
    with pytest.raises(InvalidFailoverTransitionException):
        manager.circuit_breaker_manager.transition_state(cb, CircuitBreakerState.HALF_OPEN, "Invalid direct leap")

    # CLOSED -> OPEN
    for _ in range(5):
        manager.circuit_breaker_manager.record_failure(tenant_id, "ExternalAPI")
    assert cb.state == CircuitBreakerState.OPEN


def test_flow6_bulkhead_isolation(manager):
    """Flow 6 — Bulkhead Isolation."""
    tenant_id = "tenant_a"
    manager.bulkhead_manager.configure_partition(
        tenant_id, "WorkloadA", max_concurrent_calls=2, max_queue_capacity=1
    )
    manager.bulkhead_manager.configure_partition(tenant_id, "WorkloadB", max_concurrent_calls=10)

    # Exhaust WorkloadA
    manager.bulkhead_manager.acquire_capacity(tenant_id, "WorkloadA")
    manager.bulkhead_manager.acquire_capacity(tenant_id, "WorkloadA")
    manager.bulkhead_manager.acquire_capacity(tenant_id, "WorkloadA")  # queued

    with pytest.raises(BulkheadCapacityExceededException):
        manager.bulkhead_manager.acquire_capacity(tenant_id, "WorkloadA")  # queue full

    # WorkloadB remains unaffected
    assert manager.bulkhead_manager.acquire_capacity(tenant_id, "WorkloadB") is True


def test_flow7_graceful_degradation(manager):
    """Flow 7 — Graceful Degradation."""
    tenant_id = "tenant_a"
    plan = manager.degradation_manager.formulate_degradation_plan(
        tenant_id, "InferenceEngine", DegradationLevel.REDUCED
    )

    assert plan.level == DegradationLevel.REDUCED
    assert "Core Data Access" in plan.preserved_capabilities
    assert len(plan.disabled_capabilities) > 0


def test_flow8_scaling_delegation(manager):
    """Flow 8 — Scaling Delegation."""
    tenant_id = "tenant_a"
    plan = manager.scaling_manager.plan_scaling(tenant_id, "EngineCluster", ScalingDirection.SCALE_OUT, delta_units=4)

    assert plan.delegation_id is not None
    assert plan.status.value == "DELEGATED"


def test_flow9_high_risk_failover_approval(manager):
    """Flow 9 — High-Risk Failover Approval."""
    tenant_id = "tenant_a"

    with pytest.raises(HighRiskRecoveryRequiresApprovalException):
        manager.failover_manager.create_failover_request(
            tenant_id, "InferenceService", "us-east-1", "us-west-2", is_high_risk=True
        )


def test_flow10_successful_controlled_failover(manager):
    """Flow 10 — Successful Controlled Failover."""
    tenant_id = "tenant_a"
    plan = FailoverPlan(
        tenant_id=tenant_id, service_id="InferenceService", source_region="us-east-1", target_region="us-west-2"
    )
    manager.failover_manager._plans[plan.plan_id] = plan
    manager.failover_manager.transition_status(plan, FailoverStatus.ASSESSING)
    manager.failover_manager.transition_status(plan, FailoverStatus.GOVERNED)

    completed_plan = manager.failover_manager.approve_and_delegate_failover(plan.plan_id, tenant_id)
    assert completed_plan.status.value == "COMPLETED"
    assert completed_plan.delegation_id is not None


def test_flow11_disaster_recovery_objective(manager):
    """Flow 11 — Disaster Recovery Objective."""
    tenant_id = "tenant_a"
    dr_plan = manager.dr_manager.create_dr_plan(tenant_id, DisasterRecoveryScenario.REGION_OUTAGE)
    activated = manager.dr_manager.activate_dr_plan(dr_plan.dr_plan_id, tenant_id)

    assert activated.status == DisasterRecoveryStatus.COMPLETED
    assert activated.objective.observed_rto_minutes <= activated.objective.rto_minutes
    assert activated.objective.observed_rpo_minutes <= activated.objective.rpo_minutes


def test_flow12_restore_verification_failure(manager):
    """Flow 12 — Restore Verification Failure."""
    tenant_id = "tenant_a"
    plan = manager.restore_manager.plan_restore(tenant_id, "bak_123", "db_001")

    with pytest.raises(RecoveryVerificationFailedException):
        manager.restore_manager.verify_restore(plan.plan_id, tenant_id, force_failure=True)


def test_flow13_cross_tenant_isolation(manager):
    """Flow 13 — Cross-Tenant Isolation."""
    svc = manager.service_manager.register_service("tenant_a", "Tenant A Service")

    with pytest.raises(CrossTenantResilienceAccessException) as exc_info:
        manager.service_manager.get_service(svc.service_id, tenant_id="tenant_b")

    # Opaque error leaking zero metadata
    assert "Access denied or resource not found" in str(exc_info.value)
    assert "Tenant A Service" not in str(exc_info.value)
    assert "tenant_a" not in str(exc_info.value)


def test_flow14_immutable_recovery_record(manager):
    """Flow 14 — Immutable Recovery Record."""
    tenant_id = "tenant_a"
    rb = manager.runbook_manager.create_runbook(tenant_id, "Failover Runbook")
    manager.runbook_manager.finalize_runbook(rb.runbook_id, tenant_id)

    with pytest.raises(ImmutableResilienceRecordException):
        manager.runbook_manager.add_step_to_runbook(
            rb.runbook_id, tenant_id, RunbookStep(step_number=99, name="Illegal Step")
        )


def test_flow15_chaos_experiment_governance(manager):
    """Flow 15 — Chaos Experiment Governance."""
    tenant_id = "tenant_a"

    with pytest.raises(HighRiskRecoveryRequiresApprovalException):
        manager.chaos_manager.plan_experiment(
            tenant_id, "Latency Test", "InferenceEngine", ExperimentScenario.LATENCY_INJECTION, risk=ExperimentRisk.HIGH
        )


def test_flow16_runbook_execution(manager):
    """Flow 16 — Runbook Execution."""
    tenant_id = "tenant_a"
    rb = manager.runbook_manager.create_runbook(tenant_id, "Emergency Recovery", RunbookTrigger.INCIDENT_DETECTED)
    assert len(rb.steps) > 0
    assert rb.trigger == RunbookTrigger.INCIDENT_DETECTED


def test_flow17_production_readiness_hard_failure(manager):
    """Flow 17 — Production Readiness Hard Failure."""
    tenant_id = "tenant_a"
    reqs = [
        ReadinessRequirement(
            dimension=ReadinessDimension.SECURITY, name="Security Audit", is_mandatory=True, is_passed=False
        ),
        ReadinessRequirement(
            dimension=ReadinessDimension.RELIABILITY, name="SLO Defined", is_mandatory=False, is_passed=True
        ),
    ]

    ass = manager.readiness_manager.assess_readiness(tenant_id, "Service_X", requirements=reqs)
    # Hard failure overrides aggregate score
    assert ass.status.value == "NOT_READY"
    assert len(ass.hard_failures) > 0


def test_flow18_sensitive_data_redaction(manager):
    """Flow 18 — Sensitive Data Redaction."""
    tenant_id = "tenant_a"
    raw_ev = {"db_password": "supersecretpassword123", "service_name": "Inference_DB"}

    ev = manager.evidence_manager.add_evidence("bundle_001", tenant_id, "DB_BACKUP_CHECK", raw_ev)
    assert ev.sanitized_content["db_password"] == "[REDACTED]"
    assert ev.sanitized_content["service_name"] == "Inference_DB"


def test_flow19_recovery_learning(manager):
    """Flow 19 — Recovery Learning."""
    tenant_id = "tenant_a"
    learn = manager.learning_manager.record_learning(tenant_id, "Service_Y", "Capacity saturation failure")

    assert len(learn.recommendations) > 0
    rec = learn.recommendations[0]
    assert rec.auto_execute is False  # Never auto-execute
    assert rec.requires_approval is True


def test_flow20_full_enterprise_resilience_lifecycle(manager):
    """Flow 20 — Full Enterprise Resilience Lifecycle."""
    tenant_id = "tenant_enterprise"

    res = manager.run_full_resilience_lifecycle(
        tenant_id=tenant_id,
        service_name="Enterprise_AI_Inference_Core",
        source_region="us-east-1",
        target_region="us-west-2",
    )

    assert res["status"] == "COMPLETED"
    assert res["verification_status"] == "PASSED"
    assert res["evidence_checksum"] != ""
    assert res["snapshot_id"] is not None

    summary = manager.get_platform_summary(tenant_id)
    assert summary["status"] == "OPERATIONAL"
    assert summary["metrics"]["ai_resilience_recoveries_total"] > 0
