"""
E2E Test Suite for Phase 5.51 Enterprise AI Unified Intelligence Platform.

Validates all 20 mandatory end-to-end intelligence flows, domain provider contracts,
fault isolation, idempotency, context limits, causal explainability, and governance gates.
"""

import pytest

from app.platform_contracts.delegation import DelegationRequest
from app.unified_intelligence.causal_analysis import CausalStatus
from app.unified_intelligence.context_fusion import UnifiedContextPolicy
from app.unified_intelligence.domains import IntelligenceDomain
from app.unified_intelligence.exceptions import (
    CrossTenantUnifiedIntelligenceException,
    HighRiskUnifiedActionRequiresApprovalException,
    ImmutableUnifiedIntelligenceRecordException,
)
from app.unified_intelligence.manager import UnifiedIntelligenceManager
from app.unified_intelligence.normalization_contracts import UnifiedDomainInput
from app.unified_intelligence.providers import BaseIntelligenceProvider
from app.unified_intelligence.situation_awareness import SituationSeverity, SituationStatus


class MockSecurityProvider(BaseIntelligenceProvider):
    def get_domain(self) -> IntelligenceDomain:
        return IntelligenceDomain.SECURITY

    def get_signals(self, tenant_id: str):
        return [{"signal_id": "sec-1", "type": "threat"}]

    def get_assurance(self, tenant_id: str):
        return {"score": 0.88, "domain": "security"}


class MockFailingProvider(BaseIntelligenceProvider):
    def get_domain(self) -> IntelligenceDomain:
        return IntelligenceDomain.OPERATIONS

    def get_signals(self, tenant_id: str):
        raise RuntimeError("Operations provider backend database timeout")

    def get_assurance(self, tenant_id: str):
        raise RuntimeError("Operations provider backend unreachable")


@pytest.fixture
def manager():
    return UnifiedIntelligenceManager()


def test_flow_01_domain_input_normalization_and_ingestion(manager):
    """Flow 01: Normalizes domain inputs into standard UnifiedSignal objects."""
    inp = UnifiedDomainInput(
        domain=IntelligenceDomain.SECURITY,
        tenant_id="tenant_a",
        entity_reference="model://llama-3",
        signal_type="PROMPT_INJECTION",
        severity="HIGH",
        confidence_score=0.92,
        risk_score=0.78,
    )
    sig = manager.ingest_domain_input("tenant_a", inp)
    assert (
        sig.signal_id.startswith("norm-sig-")
        or sig.signal_id.startswith("unif-sig-")
        or sig.signal_id.startswith("sig-")
    )
    assert sig.domain == IntelligenceDomain.SECURITY
    assert sig.tenant_id == "tenant_a"
    assert sig.severity == "HIGH"
    assert sig.confidence_score == 0.92


def test_flow_02_intelligence_provider_contract_isolation(manager):
    """Flow 02: Decouples UnifiedIntelligenceManager from direct domain manager imports via IntelligenceProvider contract."""
    prov = MockSecurityProvider()
    manager.register_provider(IntelligenceDomain.SECURITY, prov)

    stored_prov = manager.provider_registry.get_provider(IntelligenceDomain.SECURITY)
    assert stored_prov == prov
    assert stored_prov.get_domain() == IntelligenceDomain.SECURITY
    res = stored_prov.get_assurance("tenant_a")
    assert res["score"] == 0.88


def test_flow_03_context_fusion_size_and_age_bounded_window(manager):
    """Flow 03: Applies size, age, and domain limits to avoid memory bloat."""
    # Ingest 15 signals
    for i in range(15):
        inp = UnifiedDomainInput(
            domain=IntelligenceDomain.SECURITY if i % 2 == 0 else IntelligenceDomain.IDENTITY,
            tenant_id="tenant_a",
            entity_reference=f"entity-{i}",
            signal_type="ANOMALY",
            severity="MEDIUM",
        )
        manager.ingest_domain_input("tenant_a", inp)

    policy = UnifiedContextPolicy(max_signals=5, max_domains=2)
    context = manager.fuse_context("tenant_a", policy=policy)
    assert len(context.signals) <= 5
    assert len(context.participating_domains) <= 2
    assert context.sha256_fingerprint is not None


def test_flow_04_cross_domain_signal_correlation_and_confidence(manager):
    """Flow 04: Groups signals across different domains and calculates composite confidence."""
    manager.ingest_domain_input(
        "tenant_a",
        UnifiedDomainInput(
            domain=IntelligenceDomain.SECURITY,
            tenant_id="tenant_a",
            entity_reference="user:alice",
            signal_type="SUSPICIOUS_LOGIN",
            confidence_score=0.9,
        ),
    )
    manager.ingest_domain_input(
        "tenant_a",
        UnifiedDomainInput(
            domain=IntelligenceDomain.IDENTITY,
            tenant_id="tenant_a",
            entity_reference="user:alice",
            signal_type="PRIVILEGE_ESCALATION",
            confidence_score=0.85,
        ),
    )

    context = manager.fuse_context("tenant_a")
    correlations = manager.correlation_engine.correlate_context(context)
    assert len(correlations) >= 1
    assert correlations[0].composite_confidence > 0.8


def test_flow_05_explainable_causal_hypothesis_generation(manager):
    """Flow 05: Generates causal hypotheses with confidence, evidence, and status without claiming 100% correlation=causation."""
    corr_group = manager.correlation_engine.correlate_context(manager.fuse_context("tenant_a"))
    if not corr_group:
        # Create a sample correlation
        manager.ingest_domain_input(
            "tenant_a",
            UnifiedDomainInput(
                domain=IntelligenceDomain.SECURITY,
                tenant_id="tenant_a",
                entity_reference="sys-1",
                signal_type="EXPLOIT",
            ),
        )
        corr_group = manager.correlation_engine.correlate_context(manager.fuse_context("tenant_a"))

    hypotheses = manager.causal_engine.hypothesize_causality("tenant_a", corr_group[0])
    assert len(hypotheses) >= 1
    hyp = hypotheses[0]
    assert hyp.status in [CausalStatus.HYPOTHESIZED, CausalStatus.SUPPORTED, CausalStatus.LIKELY]
    assert hyp.explainability is not None
    assert len(hyp.alternative_hypotheses) >= 1


def test_flow_06_situation_awareness_lifecycle_and_severity_separation(manager):
    """Flow 06: Separates situation lifecycle state (e.g., ANALYZING, WATCH) from severity (CRITICAL, HIGH)."""
    manager.ingest_domain_input(
        "tenant_a",
        UnifiedDomainInput(
            domain=IntelligenceDomain.SECURITY,
            tenant_id="tenant_a",
            entity_reference="node-1",
            signal_type="BREACH",
            severity="CRITICAL",
        ),
    )
    manager.ingest_domain_input(
        "tenant_a",
        UnifiedDomainInput(
            domain=IntelligenceDomain.OPERATIONS,
            tenant_id="tenant_a",
            entity_reference="node-1",
            signal_type="OUTAGE",
            severity="CRITICAL",
        ),
    )

    situations = manager.detect_situations("tenant_a")
    assert len(situations) >= 1
    sit = situations[0]
    assert isinstance(sit.status, SituationStatus)
    assert isinstance(sit.severity, SituationSeverity)
    assert sit.severity == SituationSeverity.CRITICAL


def test_flow_07_cross_domain_risk_propagation_graph(manager):
    """Flow 07: Models risk propagation across interconnected domains."""
    graph = manager.risk_propagation_engine.build_graph(
        "tenant_a",
        [
            (IntelligenceDomain.IDENTITY, IntelligenceDomain.SECURITY, 0.8),
            (IntelligenceDomain.SECURITY, IntelligenceDomain.OPERATIONS, 0.7),
        ],
    )
    assert len(graph.nodes) >= 3
    propagated = manager.risk_propagation_engine.propagate_risk(
        "tenant_a", graph, IntelligenceDomain.IDENTITY, initial_risk=0.9
    )
    assert propagated.nodes[IntelligenceDomain.SECURITY.value].current_risk_score > 0.5


def test_flow_08_multi_domain_unified_impact_analysis(manager):
    """Flow 08: Evaluates business, operational, security, and compliance impact scores."""
    manager.ingest_domain_input(
        "tenant_a",
        UnifiedDomainInput(
            domain=IntelligenceDomain.SECURITY,
            tenant_id="tenant_a",
            entity_reference="db-prod",
            signal_type="DATA_EXFILTRATION",
            severity="HIGH",
        ),
    )
    situations = manager.detect_situations("tenant_a")
    assert len(situations) >= 1

    impact = manager.impact_engine.evaluate_situation_impact("tenant_a", situations[0])
    assert impact.security_impact_score > 0.0
    assert impact.aggregate_impact_score > 0.0


def test_flow_09_holistic_enterprise_risk_engine_evaluation(manager):
    """Flow 09: Calculates holistic cross-domain risk score."""
    manager.ingest_domain_input(
        "tenant_a",
        UnifiedDomainInput(
            domain=IntelligenceDomain.SECURITY,
            tenant_id="tenant_a",
            entity_reference="svc-auth",
            signal_type="ATTACK",
            risk_score=0.85,
        ),
    )
    risk = manager.evaluate_risk("tenant_a")
    assert risk.overall_risk_score > 0.0
    assert risk.risk_level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


def test_flow_10_cross_domain_assurance_posture_coordination(manager):
    """Flow 10: Coordinates multi-domain assurance posture."""
    manager.register_provider(IntelligenceDomain.SECURITY, MockSecurityProvider())
    posture = manager.evaluate_assurance("tenant_a")
    assert posture.overall_assurance_score > 0.0
    assert posture.assurance_level in ["HIGH", "MODERATE", "LOW", "DEGRADED"]


def test_flow_11_cross_domain_trust_assessment(manager):
    """Flow 11: Computes composite trust scores for entities across domains."""
    trust = manager.evaluate_trust("tenant_a", "entity://user-bob")
    assert trust.overall_trust_score >= 0.0
    assert trust.trust_level in ["TRUSTED", "VERIFIED", "CONDITIONAL", "HIGH_RISK", "UNTRUSTED"]


def test_flow_12_prioritized_recommendation_generation(manager):
    """Flow 12: Generates actionable cross-domain recommendations prioritized by risk reduction."""
    manager.ingest_domain_input(
        "tenant_a",
        UnifiedDomainInput(
            domain=IntelligenceDomain.SECURITY,
            tenant_id="tenant_a",
            entity_reference="res-1",
            signal_type="FAIL",
            severity="HIGH",
        ),
    )
    sits = manager.detect_situations("tenant_a")
    recs = manager.generate_recommendations("tenant_a", sits[0].situation_id)
    assert len(recs) >= 1
    assert recs[0].action_type in ["ISOLATION", "AUDIT", "REMEDIATION"]


def test_flow_13_multi_step_coordination_plan_building(manager):
    """Flow 13: Builds multi-step coordination plan enforcing domain execution order and dependencies."""
    manager.ingest_domain_input(
        "tenant_a",
        UnifiedDomainInput(
            domain=IntelligenceDomain.SECURITY,
            tenant_id="tenant_a",
            entity_reference="res-1",
            signal_type="FAIL",
            severity="HIGH",
        ),
    )
    sits = manager.detect_situations("tenant_a")
    recs = manager.generate_recommendations("tenant_a", sits[0].situation_id)
    plan = manager.build_coordination_plan("tenant_a", recs[0].recommendation_id)

    assert plan.plan_id.startswith("plan-")
    assert len(plan.steps) >= 1


def test_flow_14_human_governance_approval_gate_enforcement(manager):
    """Flow 14: Raises HighRiskUnifiedActionRequiresApprovalException if high-risk action lacks human approval."""
    manager.ingest_domain_input(
        "tenant_a",
        UnifiedDomainInput(
            domain=IntelligenceDomain.SECURITY,
            tenant_id="tenant_a",
            entity_reference="res-1",
            signal_type="FAIL",
            severity="CRITICAL",
        ),
    )
    sits = manager.detect_situations("tenant_a")
    recs = manager.generate_recommendations("tenant_a", sits[0].situation_id)
    rec = recs[0]
    rec.priority = "CRITICAL"
    rec.requires_human_approval = True

    # Unapproved call must raise exception
    with pytest.raises(HighRiskUnifiedActionRequiresApprovalException):
        manager.evaluate_governance("tenant_a", rec, approved_by=None)

    # Approved call passes
    res = manager.evaluate_governance("tenant_a", rec, approved_by="admin@enterprise.com")
    assert res.policy_status == "APPROVED"


def test_flow_15_cross_tenant_isolation_boundary_enforcement(manager):
    """Flow 15: Enforces strict tenant boundaries, raising CrossTenantUnifiedIntelligenceException if data leaks across tenants."""
    manager.ingest_domain_input(
        "tenant_a",
        UnifiedDomainInput(
            domain=IntelligenceDomain.SECURITY, tenant_id="tenant_a", entity_reference="res-a", signal_type="SIG_A"
        ),
    )

    # Accessing tenant_a data with tenant_b context must be isolated or raise exception
    signals_b = manager.repository.list_signals("tenant_b")
    assert len(signals_b) == 0

    sig_a = manager.repository.list_signals("tenant_a")[0]
    with pytest.raises(CrossTenantUnifiedIntelligenceException):
        manager.repository.get_signal("tenant_b", sig_a.signal_id)


def test_flow_16_autonomous_delegation_request_construction(manager):
    """Flow 16: Translates coordination plan steps into standardized DelegationRequest objects (no direct domain mutation)."""
    manager.ingest_domain_input(
        "tenant_a",
        UnifiedDomainInput(
            domain=IntelligenceDomain.SECURITY,
            tenant_id="tenant_a",
            entity_reference="res-1",
            signal_type="FAIL",
            severity="LOW",
        ),
    )
    sits = manager.detect_situations("tenant_a")
    recs = manager.generate_recommendations("tenant_a", sits[0].situation_id)
    plan = manager.build_coordination_plan("tenant_a", recs[0].recommendation_id)
    step = plan.steps[0]

    delegation = manager.delegation_engine.create_delegation_request("tenant_a", plan, step)
    assert isinstance(delegation, DelegationRequest)
    assert delegation.delegation_id.startswith("del-")
    assert delegation.tenant_id == "tenant_a"


def test_flow_17_delegation_verification_and_outcome_tracking(manager):
    """Flow 17: Verifies success and outcomes of delegated operations."""
    manager.ingest_domain_input(
        "tenant_a",
        UnifiedDomainInput(
            domain=IntelligenceDomain.SECURITY,
            tenant_id="tenant_a",
            entity_reference="res-1",
            signal_type="FAIL",
            severity="LOW",
        ),
    )
    sits = manager.detect_situations("tenant_a")
    recs = manager.generate_recommendations("tenant_a", sits[0].situation_id)
    plan = manager.build_coordination_plan("tenant_a", recs[0].recommendation_id)
    step = plan.steps[0]
    delegation = manager.delegation_engine.create_delegation_request("tenant_a", plan, step)

    res = manager.verification_engine.verify_delegation(
        "tenant_a", delegation, {"success": True, "message": "Quarantined model."}
    )
    assert res.verified_successful is True


def test_flow_18_sha256_immutable_evidence_ledger_sealing(manager):
    """Flow 18: Seals audit records with SHA-256 signatures, raising ImmutableUnifiedIntelligenceRecordException on modification."""
    record = manager.evidence_ledger.create_evidence(
        "tenant_a", "security", {"action": "quarantine", "entity": "node-1"}
    )
    assert record.sha256_hash is not None
    assert manager.evidence_ledger.verify_integrity(record.evidence_id) is True

    with pytest.raises(ImmutableUnifiedIntelligenceRecordException):
        record.update_payload({"tampered": True})


def test_flow_19_idempotency_and_signal_deduplication(manager):
    """Flow 19: Prevents duplicate signal processing when identical idempotency_key is submitted."""
    inp = UnifiedDomainInput(
        domain=IntelligenceDomain.SECURITY,
        tenant_id="tenant_a",
        entity_reference="res-1",
        signal_type="PROMPT_INJECTION",
        idempotency_key="key-abc-123",
    )

    sig1 = manager.ingest_domain_input("tenant_a", inp, idempotency_key="key-abc-123")
    sig2 = manager.ingest_domain_input("tenant_a", inp, idempotency_key="key-abc-123")
    assert sig1.signal_id == sig2.signal_id


def test_flow_20_partial_domain_failure_fault_isolation(manager):
    """Flow 20: Ensures that a failing domain provider does not crash Unified Intelligence for available domains."""
    manager.register_provider(IntelligenceDomain.SECURITY, MockSecurityProvider())
    manager.register_provider(IntelligenceDomain.OPERATIONS, MockFailingProvider())

    posture = manager.evaluate_assurance("tenant_a")
    assert posture.overall_assurance_score > 0.0
    # Security succeeded (0.88), Operations failed over gracefully (0.70)
    assert posture.domain_assurance_scores[IntelligenceDomain.SECURITY.value] == 0.88
    assert posture.domain_assurance_scores[IntelligenceDomain.OPERATIONS.value] == 0.70


# Additional critical test flows
def test_duplicate_signal_idempotency(manager):
    """Validates duplicate signal idempotency suppresses redundant situations."""
    inp = UnifiedDomainInput(
        domain=IntelligenceDomain.SECURITY,
        tenant_id="tenant_idemp",
        entity_reference="res-dup",
        signal_type="DUP_ALERT",
        idempotency_key="dup-key-999",
    )
    s1 = manager.ingest_domain_input("tenant_idemp", inp)
    s2 = manager.ingest_domain_input("tenant_idemp", inp)
    assert s1.signal_id == s2.signal_id


def test_correlation_does_not_claim_causation(manager):
    """Ensures correlation engine does not claim automatic 100% causation without confidence and hypotheses."""
    manager.ingest_domain_input(
        "tenant_causal",
        UnifiedDomainInput(
            domain=IntelligenceDomain.SECURITY,
            tenant_id="tenant_causal",
            entity_reference="sys-x",
            signal_type="LOG_EVENT",
        ),
    )
    sits = manager.detect_situations("tenant_causal")
    if sits:
        for hyp in sits[0].causal_hypotheses:
            assert hyp.confidence < 1.0 or hyp.status != CausalStatus.CONFIRMED
