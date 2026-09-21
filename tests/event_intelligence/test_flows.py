"""Mandatory 16 E2E Verification Test Flows for Event Intelligence Platform (Phase 5.34)."""

import pytest

from app.event_intelligence.causality import CausalRelationship
from app.event_intelligence.correlation import CorrelationType
from app.event_intelligence.events import EventCategory, EventPriority, EventSeverity, EventType
from app.event_intelligence.exceptions import (
    CrossTenantEventAccessException,
    EventResolutionException,
)
from app.event_intelligence.manager import EventIntelligenceManager
from app.event_intelligence.resolution import EventResolutionStatus
from app.platform_contracts.delegation import DelegationTarget
from app.platform_contracts.governance import GovernanceDecisionStatus


def test_flow1_reliability_event_to_incident():
    """Flow 1: Reliability event -> normalization -> correlation -> incident context."""
    mgr = EventIntelligenceManager()
    tenant = "tenant_evt_1"

    src = mgr.source_manager.register_source(tenant, "ReliabilityPlatform")
    raw_evt = {"event_type": "INCIDENT_RAISED", "severity": "HIGH", "payload": {"service": "payments_service"}}
    norm = mgr.normalizer.normalize(tenant, raw_evt, source_id=src.source_id, source_name=src.name)
    evt = norm.event

    corr_group = mgr.correlation_manager.correlate_events(
        tenant, "Reliability Correlation", [evt], CorrelationType.RELIABILITY_CASCADE
    )
    ctx = mgr.context_manager.assemble_event_context(evt)

    assert evt.severity == EventSeverity.HIGH
    assert evt.correlation_reference == corr_group.group_id
    assert len(ctx.references) > 0


def test_flow2_security_threat_high_severity():
    """Flow 2: Security threat -> enterprise event -> high severity classification."""
    mgr = EventIntelligenceManager()
    tenant = "tenant_evt_2"

    src = mgr.source_manager.register_source(tenant, "SecurityIntelligence")
    evt = mgr.event_manager.create_event(
        tenant,
        src.source_id,
        src.name,
        event_type=EventType.SECURITY_THREAT_DETECTED,
        category=EventCategory.SECURITY,
        severity=EventSeverity.CRITICAL,
    )
    cls = mgr.classifier.classify_event(evt)

    assert cls.governance_sensitive is True
    assert cls.business_impact == "HIGH"


def test_flow3_duplicate_event_deduplication():
    """Flow 3: Duplicate event delivery -> deduplication -> existing result returned."""
    mgr = EventIntelligenceManager()
    tenant = "tenant_evt_3"

    src = mgr.source_manager.register_source(tenant, "AppPlatform")
    payload = {"query": "SELECT * FROM users"}

    evt1 = mgr.event_manager.create_event(tenant, src.source_id, src.name, payload=payload)
    res1 = mgr.deduplicator.process_deduplication(evt1)

    evt2 = mgr.event_manager.create_event(tenant, src.source_id, src.name, payload=payload)
    res2 = mgr.deduplicator.process_deduplication(evt2)

    assert not res1.is_duplicate
    assert res2.is_duplicate
    assert res2.existing_event_id == evt1.event_id


def test_flow4_idempotency_conflict_detection():
    """Flow 4: Same idempotency key -> deduplication returns duplicate."""
    mgr = EventIntelligenceManager()
    tenant = "tenant_evt_4"

    src = mgr.source_manager.register_source(tenant, "AppPlatform")

    evt1 = mgr.event_manager.create_event(tenant, src.source_id, src.name, idempotency_reference="idemp_key_100")
    res1 = mgr.deduplicator.process_deduplication(evt1)

    evt2 = mgr.event_manager.create_event(tenant, src.source_id, src.name, idempotency_reference="idemp_key_100")
    res2 = mgr.deduplicator.process_deduplication(evt2)

    assert not res1.is_duplicate
    assert res2.is_duplicate


def test_flow5_cross_platform_event_correlation():
    """Flow 5: Reliability + Security + Architecture -> correlation group."""
    mgr = EventIntelligenceManager()
    tenant = "tenant_evt_5"

    src = mgr.source_manager.register_source(tenant, "MultiSource")
    evt1 = mgr.event_manager.create_event(tenant, src.source_id, src.name, category=EventCategory.OPERATIONAL)
    evt2 = mgr.event_manager.create_event(tenant, src.source_id, src.name, category=EventCategory.SECURITY)
    evt3 = mgr.event_manager.create_event(tenant, src.source_id, src.name, category=EventCategory.ARCHITECTURE)

    corr = mgr.correlation_manager.correlate_events(
        tenant, "Cross Platform Cascade", [evt1, evt2, evt3], CorrelationType.CROSS_DOMAIN
    )

    assert len(corr.event_ids) == 3
    assert evt1.correlation_reference == corr.group_id


def test_flow6_causality_analysis_distinction():
    """Flow 6: Causality analysis distinguishes CAUSE vs DOWNSTREAM_EFFECT."""
    mgr = EventIntelligenceManager()
    tenant = "tenant_evt_6"

    src = mgr.source_manager.register_source(tenant, "Source_6")
    evt_cause = mgr.event_manager.create_event(tenant, src.source_id, src.name)
    evt_effect = mgr.event_manager.create_event(tenant, src.source_id, src.name)

    causal = mgr.causality_analyzer.analyze_causality(tenant, [evt_cause, evt_effect])

    assert causal.root_cause_event_id == evt_cause.event_id
    assert causal.downstream_event_ids[0] == evt_effect.event_id
    assert causal.graph.edges[0].relationship == CausalRelationship.DOWNSTREAM_EFFECT


def test_flow7_priority_escalation():
    """Flow 7: High business impact + high security risk -> priority escalation (P1_CRITICAL)."""
    mgr = EventIntelligenceManager()
    tenant = "tenant_evt_7"

    src = mgr.source_manager.register_source(tenant, "Source_7")
    evt = mgr.event_manager.create_event(tenant, src.source_id, src.name, severity=EventSeverity.HIGH)
    prio_res = mgr.prioritization_engine.prioritize_event(evt, security_risk_high=True, business_impact_high=True)

    assert prio_res.priority == EventPriority.P1_CRITICAL


def test_flow8_high_risk_automation_approval():
    """Flow 8: High-risk automation -> ApprovalEngine required."""
    mgr = EventIntelligenceManager()
    tenant = "tenant_evt_8"

    src = mgr.source_manager.register_source(tenant, "Source_8")
    evt = mgr.event_manager.create_event(tenant, src.source_id, src.name)
    gov_dec = mgr.governance_engine.evaluate_automation_governance(tenant, evt.event_id, is_high_risk=True)

    assert gov_dec.status == GovernanceDecisionStatus.REQUIRE_APPROVAL


def test_flow9_direct_mutation_blocked():
    """Flow 9: Automation attempts direct infrastructure mutation -> BLOCKED."""
    mgr = EventIntelligenceManager()
    tenant = "tenant_evt_9"

    src = mgr.source_manager.register_source(tenant, "Source_9")
    evt = mgr.event_manager.create_event(tenant, src.source_id, src.name)
    gov_dec = mgr.governance_engine.evaluate_automation_governance(tenant, evt.event_id, attempts_direct_mutation=True)

    assert gov_dec.status == GovernanceDecisionStatus.BLOCK


def test_flow10_delegated_response():
    """Flow 10: Delegated response -> DelegationRequest generated."""
    mgr = EventIntelligenceManager()
    tenant = "tenant_evt_10"

    src = mgr.source_manager.register_source(tenant, "Source_10")
    evt = mgr.event_manager.create_event(tenant, src.source_id, src.name)
    del_plan = mgr.delegation_manager.delegate_event_response(
        tenant, evt.event_id, DelegationTarget.PLATFORM_OPERATIONS, "EXECUTE_ACTION"
    )

    assert del_plan.delegation_request is not None
    assert del_plan.delegation_request.target == DelegationTarget.PLATFORM_OPERATIONS


def test_flow11_cross_tenant_access_blocked():
    """Flow 11: Cross-tenant event access -> CrossTenantEventAccessException."""
    mgr = EventIntelligenceManager()

    src = mgr.source_manager.register_source("tenant_a", "SourceA")
    evt = mgr.event_manager.create_event("tenant_a", src.source_id, src.name)

    with pytest.raises(CrossTenantEventAccessException):
        mgr.event_manager.get_event(evt.event_id, "tenant_b")


def test_flow12_sensitive_data_redaction():
    """Flow 12: Sensitive metadata in event -> fully redacted."""
    mgr = EventIntelligenceManager()
    tenant = "tenant_evt_12"

    src = mgr.source_manager.register_source(tenant, "Source_12")
    raw_payload = {"api_key": "sk_live_999999", "password": "supersecretpassword", "normal_field": "ok"}
    norm = mgr.normalizer.normalize(tenant, {"payload": raw_payload}, source_id=src.source_id, source_name=src.name)

    assert norm.event.metadata.payload["api_key"] == "[REDACTED]"
    assert norm.event.metadata.payload["password"] == "[REDACTED]"
    assert norm.event.metadata.payload["normal_field"] == "ok"


def test_flow13_event_investigation_snapshot():
    """Flow 13: Event investigation -> immutable PlatformSnapshot."""
    mgr = EventIntelligenceManager()
    tenant = "tenant_evt_13"

    inv = mgr.investigation_manager.initiate_investigation(tenant, "evt_13")
    concluded = mgr.investigation_manager.conclude_investigation(inv.investigation_id, tenant, "Root cause found")

    assert concluded.snapshot is not None
    assert concluded.snapshot.metadata.resource_id == inv.investigation_id


def test_flow14_invalid_resolution_lifecycle():
    """Flow 14: Invalid resolution lifecycle transition -> EventResolutionException."""
    mgr = EventIntelligenceManager()
    tenant = "tenant_evt_14"

    res = mgr.resolution_manager.create_resolution(tenant, "evt_14")

    with pytest.raises(EventResolutionException):
        mgr.resolution_manager.transition_resolution(res.resolution_id, tenant, EventResolutionStatus.RESOLVED)


def test_flow15_recurring_pattern_recommendation():
    """Flow 15: Recurring event pattern -> recommendation generated without autonomous mutation."""
    mgr = EventIntelligenceManager()
    tenant = "tenant_evt_15"

    src = mgr.source_manager.register_source(tenant, "Source_15")
    evt = mgr.event_manager.create_event(tenant, src.source_id, src.name)
    pats = mgr.pattern_detector.detect_patterns(tenant, [evt])

    assert len(pats) > 0
    assert len(pats[0].recommendations) > 0


def test_flow16_full_enterprise_event_lifecycle():
    """Flow 16: Complete 20-step end-to-end enterprise event intelligence lifecycle flow."""
    mgr = EventIntelligenceManager()
    tenant = "tenant_evt_16"

    res = mgr.run_full_event_intelligence_flow(tenant_id=tenant, source_name="FullPipelineSource")

    assert res["event"]["tenant_id"] == tenant
    assert res["deduplication"]["is_duplicate"] is False
    assert res["resolution"]["status"] == EventResolutionStatus.RESOLVED.value
    assert res["investigation"]["snapshot"] is not None
