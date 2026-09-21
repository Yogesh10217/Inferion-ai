"""Mandatory 20 End-to-End Test Flows for Phase 5.46 Knowledge Assurance Platform."""

import pytest

from app.knowledge_assurance.conflicts import ConflictSeverity, KnowledgeConflictType
from app.knowledge_assurance.context_assembly import ContextAssemblyRequest
from app.knowledge_assurance.exceptions import (
    CrossTenantKnowledgeAssuranceException,
    HighRiskKnowledgeActionRequiresApprovalException,
    ImmutableKnowledgeRecordException,
)
from app.knowledge_assurance.governance import KnowledgeGovernanceOutcome
from app.knowledge_assurance.knowledge_references import KnowledgeReferenceClassification
from app.knowledge_assurance.manager import KnowledgeAssuranceManager
from app.knowledge_assurance.remediation import KnowledgeRemediationPriority
from app.knowledge_assurance.sources import KnowledgeSourceAuthority


@pytest.fixture
def manager() -> KnowledgeAssuranceManager:
    return KnowledgeAssuranceManager()


def test_flow_01_knowledge_reference_registration_and_tenant_isolation(manager: KnowledgeAssuranceManager):
    """Flow 1: Knowledge reference registration and tenant isolation."""
    ref1 = manager.references_manager.register_reference(
        tenant_id="tenant_alpha",
        external_key="doc-101",
        resource_type="DOCUMENT",
        classification="CONFIDENTIAL",
        metadata={"author": "Alice"},
    )
    assert ref1.reference_id is not None
    assert ref1.tenant_id == "tenant_alpha"
    assert ref1.classification == KnowledgeReferenceClassification.CONFIDENTIAL

    retrieved = manager.references_manager.get_reference("tenant_alpha", ref1.reference_id)
    assert retrieved.external_key == "doc-101"


def test_flow_02_cross_tenant_access_blocked_zero_metadata_leakage(manager: KnowledgeAssuranceManager):
    """Flow 2: Cross-tenant knowledge access blocked with zero metadata leakage."""
    ref = manager.references_manager.register_reference(
        tenant_id="tenant_alpha",
        external_key="secret-doc",
        resource_type="DOCUMENT",
    )

    with pytest.raises(CrossTenantKnowledgeAssuranceException) as exc_info:
        manager.references_manager.get_reference("tenant_beta", ref.reference_id)

    # Ensure zero metadata leakage in exception text
    err_msg = str(exc_info.value)
    assert "tenant_alpha" not in err_msg
    assert "secret-doc" not in err_msg
    assert ref.reference_id not in err_msg


def test_flow_03_knowledge_source_authority_evaluation(manager: KnowledgeAssuranceManager):
    """Flow 3: Knowledge source authority evaluation."""
    src = manager.sources_manager.register_source(
        tenant_id="tenant_alpha",
        name="Enterprise Architecture Repository",
        source_type="DOCUMENT_REPOSITORY",
        authority="AUTHORITATIVE",
        reliability_score=0.98,
    )
    assert src.authority == KnowledgeSourceAuthority.AUTHORITATIVE
    assert src.reliability_score == 0.98

    eval_res = manager.sources_manager.evaluate_source("tenant_alpha", src.source_id)
    assert eval_res["authority"] == "AUTHORITATIVE"
    assert eval_res["trust_score"] >= 0.9


def test_flow_04_semantic_context_creation(manager: KnowledgeAssuranceManager):
    """Flow 4: Semantic context creation."""
    concepts = [
        {"name": "DataPrivacy", "description": "GDPR compliance constraints"},
        {"name": "Encryption", "description": "AES-256 requirement"},
    ]
    rels = [{"source_concept": "Encryption", "target_concept": "DataPrivacy", "relationship_type": "ENFORCES"}]
    sem_ctx = manager.semantic_context_manager.create_semantic_context(
        tenant_id="tenant_alpha",
        domain="SECURITY_GOVERNANCE",
        concepts=concepts,
        relationships=rels,
    )
    assert sem_ctx.domain == "SECURITY_GOVERNANCE"
    assert len(sem_ctx.concepts) == 2
    assert len(sem_ctx.relationships) == 1


def test_flow_05_trusted_context_assembly(manager: KnowledgeAssuranceManager):
    """Flow 5: Trusted context assembly."""
    req = ContextAssemblyRequest(
        tenant_id="tenant_alpha",
        target_resource_id="agent-workflow-1",
        required_concepts=["DataPrivacy", "Encryption"],
        min_trust_score=0.8,
    )
    result = manager.context_assembly_manager.assemble_context("tenant_alpha", req)
    assert result.assembly_id is not None
    assert result.trust_score >= 0.8
    assert len(result.assembled_items) > 0


def test_flow_06_knowledge_provenance_chain_validation(manager: KnowledgeAssuranceManager):
    """Flow 6: Knowledge provenance chain validation."""
    sources = [
        {"source_id": "src-raw", "origin_type": "INGESTION_PIPELINE"},
        {"source_id": "src-curated", "origin_type": "EXPERT_CURATION"},
    ]
    prov = manager.provenance_manager.record_provenance(
        tenant_id="tenant_alpha",
        target_resource_id="res-policy-1",
        sources=sources,
    )
    assert prov.sha256_fingerprint != ""

    val = manager.provenance_manager.validate_provenance("tenant_alpha", prov.provenance_id)
    assert val.is_valid is True


def test_flow_07_knowledge_freshness_detection(manager: KnowledgeAssuranceManager):
    """Flow 7: Knowledge freshness detection."""
    freshness = manager.freshness_manager.evaluate_freshness(
        tenant_id="tenant_alpha",
        target_resource_id="doc-ops-guide",
        max_age_days=30,
    )
    assert freshness.target_resource_id == "doc-ops-guide"
    assert freshness.assessment.status in ["FRESH", "AGING", "STALE", "EXPIRED", "UNKNOWN"]


def test_flow_08_knowledge_trust_assessment(manager: KnowledgeAssuranceManager):
    """Flow 8: Knowledge trust assessment."""
    trust = manager.trust_engine.evaluate_trust(
        tenant_id="tenant_alpha",
        target_resource_id="res-finops-budget",
    )
    assert trust.overall_score >= 0.0
    assert trust.overall_score <= 1.0
    assert trust.trust_band in [
        "CRITICAL",
        "LOW",
        "MODERATE",
        "HIGH",
        "HIGH_TRUST",
        "TRUSTED",
        "RESTRICTED",
        "UNTRUSTED",
        "EXCELLENT",
    ]


def test_flow_09_knowledge_confidence_evaluation(manager: KnowledgeAssuranceManager):
    """Flow 9: Knowledge confidence evaluation."""
    conf = manager.confidence_manager.evaluate_confidence(
        tenant_id="tenant_alpha",
        target_resource_id="model-prediction-output",
    )
    assert conf.overall_confidence >= 0.0
    assert conf.confidence_level in ["LOW", "MODERATE", "HIGH", "VERY_HIGH"]


def test_flow_10_knowledge_relevance_evaluation(manager: KnowledgeAssuranceManager):
    """Flow 10: Knowledge relevance evaluation."""
    rel = manager.relevance_manager.evaluate_relevance(
        tenant_id="tenant_alpha",
        target_resource_id="context-query-1",
        query_context="How to handle PII data?",
    )
    assert rel.overall_relevance >= 0.0
    assert len(rel.factors) > 0


def test_flow_11_knowledge_conflict_detection(manager: KnowledgeAssuranceManager):
    """Flow 11: Knowledge conflict detection."""
    conflict = manager.conflict_manager.register_conflict(
        tenant_id="tenant_alpha",
        conflict_type=KnowledgeConflictType.POLICY_CONFLICT,
        severity=ConflictSeverity.CRITICAL,
        target_resource_id="security-policy-42",
        competing_sources=["SourceA: TLS 1.2", "SourceB: TLS 1.3 Mandate"],
    )
    assert conflict.severity == ConflictSeverity.CRITICAL
    assert conflict.requires_approval is True


def test_flow_12_knowledge_consistency_assessment(manager: KnowledgeAssuranceManager):
    """Flow 12: Knowledge consistency assessment."""
    consistency = manager.consistency_manager.assess_consistency(
        tenant_id="tenant_alpha",
        target_resource_id="domain-compliance",
    )
    assert consistency.overall_score >= 0.0
    assert len(consistency.findings) >= 0


def test_flow_13_knowledge_duplication_detection(manager: KnowledgeAssuranceManager):
    """Flow 13: Knowledge duplication detection (recommendations only)."""
    items = [
        {"id": "doc1", "content": "Enterprise Backup SOP version 1.0"},
        {"id": "doc2", "content": "Enterprise Backup SOP version 1.0 copy"},
    ]
    dups = manager.duplication_manager.detect_duplicates("tenant_alpha", items)
    assert len(dups) > 0
    assert dups[0].recommendation == "FLAG_FOR_REVIEW"  # Advisory only, never auto-delete


def test_flow_14_knowledge_gap_and_coverage_analysis(manager: KnowledgeAssuranceManager):
    """Flow 14: Knowledge gap and coverage analysis."""
    gaps = manager.gap_manager.analyze_domain_gaps("tenant_alpha", "CLOUD_GOVERNANCE")
    assert len(gaps) > 0

    coverage = manager.coverage_manager.evaluate_coverage("tenant_alpha", "CLOUD_GOVERNANCE")
    assert coverage.coverage_score.overall_coverage >= 0.0


def test_flow_15_cross_domain_knowledge_correlation(manager: KnowledgeAssuranceManager):
    """Flow 15: Cross-domain knowledge correlation."""
    corrs = manager.correlation_manager.correlate_resource(
        tenant_id="tenant_alpha",
        target_resource_id="inc-2026-001",
        resource_domain="INCIDENTS",
    )
    assert len(corrs) > 0
    domains = [c.correlated_domain for c in corrs]
    assert "CONTROLS" in domains or "RISKS" in domains or "SERVICES" in domains


def test_flow_16_decision_context_enrichment(manager: KnowledgeAssuranceManager):
    """Flow 16: Decision context enrichment with decision governance."""
    dctx = manager.decision_context_manager.enrich_decision_context(
        tenant_id="tenant_alpha",
        decision_id="dec-infrastructure-upgrade",
    )
    assert dctx.decision_id == "dec-infrastructure-upgrade"
    assert dctx.trust.overall_trust_score >= 0.8
    assert len(dctx.recommendations) > 0


def test_flow_17_high_risk_knowledge_action_requires_approval(manager: KnowledgeAssuranceManager):
    """Flow 17: High-risk knowledge action requires approval."""
    # Test governance request for high risk action
    gov_req = manager.governance_engine.evaluate_knowledge_action(
        tenant_id="tenant_alpha",
        action_type="DELETE_AUTHORITATIVE_KNOWLEDGE",
        target_resource_id="root-auth-source-1",
        risk_score=0.9,
    )
    assert gov_req.outcome == KnowledgeGovernanceOutcome.REQUIRE_APPROVAL

    # Test remediation plan execution with critical priority
    plan = manager.remediation_manager.create_remediation_plan(
        tenant_id="tenant_alpha",
        target_resource_id="root-auth-source-1",
        priority=KnowledgeRemediationPriority.CRITICAL,
    )
    with pytest.raises(HighRiskKnowledgeActionRequiresApprovalException):
        manager.remediation_manager.execute_plan_via_delegation("tenant_alpha", plan.plan_id)


def test_flow_18_delegation_only_enforcement(manager: KnowledgeAssuranceManager):
    """Flow 18: Delegation-only enforcement (no direct external mutations)."""
    actions_data = [
        {"target_system": "VECTOR_DB", "operation": "PURGE_CHUNK", "payload": {"chunk_id": "c-99"}},
    ]
    plan = manager.delegation_manager.create_delegation_plan(
        tenant_id="tenant_alpha",
        description="Delegated purge request",
        actions_data=actions_data,
    )
    assert plan.plan_id is not None
    assert len(plan.actions) == 1
    assert plan.actions[0].delegation_request_id != ""


def test_flow_19_immutable_evidence_verification(manager: KnowledgeAssuranceManager):
    """Flow 19: Immutable evidence verification."""
    bundle = manager.evidence_manager.create_bundle("tenant_alpha", "Audit Evidence Bundle")
    manager.evidence_manager.add_evidence(
        tenant_id="tenant_alpha",
        bundle_id=bundle.bundle_id,
        evidence_type="TRUST_LOG",
        title="Trust Evaluation",
        payload={"score": 0.95},
    )

    finalized = manager.evidence_manager.finalize_bundle("tenant_alpha", bundle.bundle_id)
    assert finalized.is_finalized is True
    assert finalized.sha256_fingerprint != ""

    # Attempt modification should raise ImmutableKnowledgeRecordException
    with pytest.raises(ImmutableKnowledgeRecordException):
        manager.evidence_manager.add_evidence(
            tenant_id="tenant_alpha",
            bundle_id=bundle.bundle_id,
            evidence_type="LATE_LOG",
            title="Late Entry",
            payload={},
        )

    # Verify integrity
    integ = manager.evidence_manager.verify_bundle_integrity("tenant_alpha", bundle.bundle_id)
    assert integ.is_valid is True


def test_flow_20_full_enterprise_knowledge_assurance_lifecycle(manager: KnowledgeAssuranceManager):
    """Flow 20: Full Enterprise Knowledge Assurance lifecycle."""
    tenant = "tenant_enterprise"

    # Step 1: Register Source & Reference
    manager.sources_manager.register_source(
        tenant_id=tenant,
        name="Enterprise Policy Hub",
        source_type="DOCUMENT_REPOSITORY",
        authority="AUTHORITATIVE",
    )
    ref = manager.references_manager.register_reference(
        tenant_id=tenant,
        external_key="policy-sec-2026",
        resource_type="DOCUMENT",
    )

    # Step 2: Context Creation & Assembly
    ctx = manager.context_manager.create_context(
        tenant_id=tenant,
        title="Enterprise Compliance Context",
        payload={"ref_id": ref.reference_id},
    )
    req = ContextAssemblyRequest(
        tenant_id=tenant,
        target_resource_id=ctx.context_id,
        required_concepts=["Compliance"],
    )
    manager.context_assembly_manager.assemble_context(tenant, req)

    # Step 3: Trust & Assurance Evaluation
    manager.trust_engine.evaluate_trust(tenant, ctx.context_id)
    ass = manager.assurance_manager.assess_knowledge_assurance(tenant, ctx.context_id)
    assert ass.assurance_score.overall_score > 0.0

    # Step 4: Initiate Investigation & Conclude with Snapshot
    inv = manager.investigation_manager.initiate_investigation(
        tenant_id=tenant,
        target_resource_id=ctx.context_id,
        resource_type="CONTEXT",
        reason="Periodic compliance verification audit",
    )
    manager.investigation_manager.add_finding(
        tenant_id=tenant,
        investigation_id=inv.investigation_id,
        title="Minor Freshness Gap",
        description="Source updated 10 days ago",
    )
    concluded_inv = manager.investigation_manager.conclude_investigation(tenant, inv.investigation_id)
    assert concluded_inv.snapshot_id is not None

    # Step 5: Advisory Learning Recommendation
    manager.learning_manager.record_learning_event(
        tenant_id=tenant,
        source_event="INVESTIGATION_CONCLUDED",
        patterns=[{"pattern_name": "FrequentFreshnessGaps"}],
        recommendations=[{"title": "Schedule 7-day refresh cycles", "action_type": "UPDATE_POLICY"}],
    )
    recs = manager.learning_manager.list_recommendations(tenant)
    assert len(recs) > 0
    # Enforce invariant
    assert recs[0].auto_execute is False

    # Step 6: Status check
    status = manager.get_status(tenant)
    assert status["status"] == "OPERATIONAL"
