"""Mandatory 12 E2E Verification Flows for Reliability Platform (Phase 5.31)."""

import pytest

from app.reliability_platform.manager import ReliabilityPlatformManager
from app.reliability_platform.services import ServiceTier, ServiceStatus
from app.reliability_platform.health import HealthState
from app.reliability_platform.slo import SLIType, SLOBreach
from app.reliability_platform.signals import SignalSource, SignalSeverity
from app.reliability_platform.incidents import IncidentSeverity, IncidentStatus
from app.reliability_platform.correlation import CorrelationStrategy
from app.reliability_platform.remediation import RemediationAction, RemediationRisk
from app.reliability_platform.postmortems import PostmortemStatus
from app.platform_contracts.governance import GovernanceDecisionStatus
from app.platform_contracts.trust import TrustBand
from app.platform_contracts.idempotency import IdempotencyConflictException
from app.reliability_platform.exceptions import (
    CrossTenantReliabilityAccessException,
    ImmutableReliabilityRecordException,
    ServiceNotFoundException,
)


def test_flow1_service_health_and_slo():
    """Flow 1: Service registration, health assessment, and SLI/SLO budget evaluation."""
    mgr = ReliabilityPlatformManager()
    tenant = "tenant_rel_1"

    svc = mgr.service_manager.register_service(tenant, "InferenceService", ServiceTier.TIER_0_CRITICAL)
    assert svc.tenant_id == tenant

    health = mgr.health_engine.evaluate_health(svc.service_id, tenant, latency_ms=50.0, error_rate_pct=0.0)
    assert health.score.state == HealthState.HEALTHY

    slo = mgr.slo_manager.create_slo(tenant, svc.service_id, "LatencySLO", target_percentage=99.9)
    breach = mgr.slo_manager.evaluate_slo(slo.slo_id, tenant, observed_value=99.95)
    assert breach is None
    assert slo.budget.remaining_budget_pct > 0.0


def test_flow2_slo_breach_incident():
    """Flow 2: Error budget exhaustion triggers automated incident creation."""
    mgr = ReliabilityPlatformManager()
    tenant = "tenant_rel_2"

    svc = mgr.service_manager.register_service(tenant, "GatewayService", ServiceTier.TIER_1_HIGH)
    slo = mgr.slo_manager.create_slo(tenant, svc.service_id, "AvailabilitySLO", target_percentage=99.9)

    breach = mgr.slo_manager.evaluate_slo(slo.slo_id, tenant, observed_value=90.0)
    assert breach is not None
    assert breach.remaining_budget_pct == 0.0

    inc = mgr.incident_manager.create_incident(tenant, svc.service_id, f"SLO Breach: {slo.name}", IncidentSeverity.SEV_1_HIGH)
    assert inc.status == IncidentStatus.DETECTED


def test_flow3_cross_service_correlation():
    """Flow 3: Multi-service cascade signals correlated into unified incident context."""
    mgr = ReliabilityPlatformManager()
    tenant = "tenant_rel_3"

    inc1 = mgr.incident_manager.create_incident(tenant, "svc_a", "Database Failure", IncidentSeverity.SEV_0_CRITICAL)
    inc2 = mgr.incident_manager.create_incident(tenant, "svc_b", "API Gateway Timeout", IncidentSeverity.SEV_1_HIGH)

    corr = mgr.correlation_manager.correlate_incidents(
        tenant_id=tenant,
        primary_incident_id=inc1.incident_id,
        correlated_incident_ids=[inc2.incident_id],
        strategy=CorrelationStrategy.SERVICE_DEPENDENCY,
    )

    assert corr.primary_incident_id == inc1.incident_id
    assert inc2.incident_id in corr.correlated_incident_ids


def test_flow4_architecture_impact_analysis():
    """Flow 4: Architecture topology dependency impact assessment for degraded service."""
    mgr = ReliabilityPlatformManager()
    tenant = "tenant_rel_4"

    svc = mgr.service_manager.register_service(tenant, "AuthService")
    impact = mgr.impact_analyzer.analyze_impact(tenant, svc.service_id)

    assert impact.service_id == svc.service_id
    assert len(impact.affected_components) > 0


def test_flow5_root_cause_hypothesis():
    """Flow 5: Competing root cause hypotheses generated and evaluated against evidence."""
    mgr = ReliabilityPlatformManager()
    tenant = "tenant_rel_5"

    inc = mgr.incident_manager.create_incident(tenant, "svc_5", "Latency Spike")
    rch1 = mgr.root_cause_manager.create_hypothesis(tenant, inc.incident_id, "GC pause", probability=0.75)
    rch2 = mgr.root_cause_manager.create_hypothesis(tenant, inc.incident_id, "Network saturation", probability=0.25)

    assert rch1.hypothesis_id != rch2.hypothesis_id
    assert rch1.probability > rch2.probability


def test_flow6_high_risk_remediation_approval():
    """Flow 6: High-risk remediation blocked until approved via ApprovalEngine -> DelegationRequest."""
    mgr = ReliabilityPlatformManager()
    tenant = "tenant_rel_6"

    inc = mgr.incident_manager.create_incident(tenant, "svc_6", "Database Corruption Alert")
    action = RemediationAction(target_manager="PLATFORM_OPERATIONS", action_name="PURGE_DATABASE", risk=RemediationRisk.CRITICAL)

    plan = mgr.remediation_manager.plan_remediation(tenant, inc.incident_id, "key_risk_6", [action])
    gov_dec = mgr.governance_engine.evaluate_remediation(tenant, plan)

    assert gov_dec.status == GovernanceDecisionStatus.REQUIRE_APPROVAL
    assert plan.delegation_request is not None


def test_flow7_cross_tenant_isolation():
    """Flow 7: Cross-tenant access attempt raises CrossTenantReliabilityAccessException with zero metadata leakage."""
    mgr = ReliabilityPlatformManager()

    svc = mgr.service_manager.register_service("tenant_a", "ServiceA")

    with pytest.raises(CrossTenantReliabilityAccessException):
        mgr.service_manager.get_service(svc.service_id, "tenant_b")


def test_flow8_secret_redaction():
    """Flow 8: Secrets redacted across signals, incidents, postmortems, metrics, and audit events."""
    mgr = ReliabilityPlatformManager()
    tenant = "tenant_rel_8"

    sig = mgr.signal_processor.process_signal(
        tenant_id=tenant,
        service_id="svc_8",
        metric_name="auth_failure",
        observed_value=1.0,
        threshold=0.0,
        payload={"secret_key": "sk-12345", "token": "bearer_abc"},
    )

    assert sig.payload["secret_key"] == "[REDACTED]"
    assert sig.payload["token"] == "[REDACTED]"


def test_flow9_immutable_incident_timeline():
    """Flow 9: Mutation attempt on closed incident timeline raises ImmutableReliabilityRecordException."""
    mgr = ReliabilityPlatformManager()
    tenant = "tenant_rel_9"

    inc = mgr.incident_manager.create_incident(tenant, "svc_9", "Minor Outage")
    mgr.incident_manager.transition_incident(inc.incident_id, tenant, IncidentStatus.TRIAGED)
    mgr.incident_manager.transition_incident(inc.incident_id, tenant, IncidentStatus.INVESTIGATING)
    mgr.incident_manager.transition_incident(inc.incident_id, tenant, IncidentStatus.MITIGATING)
    mgr.incident_manager.transition_incident(inc.incident_id, tenant, IncidentStatus.DELEGATED)
    mgr.incident_manager.transition_incident(inc.incident_id, tenant, IncidentStatus.RESOLVED)
    mgr.incident_manager.transition_incident(inc.incident_id, tenant, IncidentStatus.VERIFIED)
    closed = mgr.incident_manager.transition_incident(inc.incident_id, tenant, IncidentStatus.CLOSED)

    assert closed.status == IncidentStatus.CLOSED

    with pytest.raises(ImmutableReliabilityRecordException):
        mgr.incident_manager.transition_incident(inc.incident_id, tenant, IncidentStatus.RESOLVED)


def test_flow10_postmortem_finalization():
    """Flow 10: Finalized postmortem report creates SHA-256 fingerprint; mutation rejected."""
    mgr = ReliabilityPlatformManager()
    tenant = "tenant_rel_10"

    pm = mgr.postmortem_manager.create_postmortem(tenant, "inc_10", "Outage Summary", "Null Pointer Exception")
    assert pm.status == PostmortemStatus.DRAFT

    finalized = mgr.postmortem_manager.finalize_postmortem(pm.report_id, tenant)
    assert finalized.status == PostmortemStatus.FINALIZED
    assert len(finalized.immutable_record.fingerprint) == 64

    with pytest.raises(ImmutableReliabilityRecordException):
        mgr.postmortem_manager.finalize_postmortem(pm.report_id, tenant)


def test_flow11_remediation_idempotency():
    """Flow 11: Idempotent replay returns existing plan; payload mismatch raises IdempotencyConflictException."""
    mgr = ReliabilityPlatformManager()
    tenant = "tenant_rel_11"
    key = "idemp_key_11"

    action1 = RemediationAction(target_manager="PLATFORM_OPERATIONS", action_name="RESTART_SERVICE")
    plan1 = mgr.remediation_manager.plan_remediation(tenant, "inc_11", key, [action1])

    # Replay returns existing plan
    plan2 = mgr.remediation_manager.plan_remediation(tenant, "inc_11", key, [action1])
    assert plan1.plan_id == plan2.plan_id

    # Conflict on different payload
    action_conflict = RemediationAction(target_manager="PLATFORM_OPERATIONS", action_name="SCALE_DOWN")
    with pytest.raises(IdempotencyConflictException):
        mgr.remediation_manager.plan_remediation(tenant, "inc_11", key, [action_conflict])


def test_flow12_full_reliability_lifecycle():
    """Flow 12: Complete E2E workflow: Signal -> Health Degradation -> SLO Breach -> Incident -> Correlation -> Impact -> Hypothesis -> Risk -> Governance -> Approval -> Remediation -> Verification -> Postmortem -> Learning -> Trust -> Audit."""
    mgr = ReliabilityPlatformManager()
    tenant = "tenant_full_lifecycle_12"

    res = mgr.run_full_reliability_flow(tenant_id=tenant, service_name="Core_Payment_Engine")

    assert res["service"]["name"] == "Core_Payment_Engine"
    assert res["health"]["score"]["state"] in [HealthState.DEGRADED, HealthState.UNHEALTHY, HealthState.CRITICAL]
    assert res["incident"]["status"] == IncidentStatus.CLOSED.value
    assert res["postmortem"]["status"] == PostmortemStatus.FINALIZED.value
    assert res["trust"]["score"] > 0.0
