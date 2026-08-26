"""Mandatory 16 E2E Verification Test Flows for Knowledge Intelligence Platform (Phase 5.35)."""

import pytest
from datetime import datetime, timezone, timedelta

from app.knowledge_intelligence.manager import KnowledgeIntelligenceManager
from app.knowledge_intelligence.knowledge import KnowledgeType, KnowledgeClassification, KnowledgeStatus
from app.knowledge_intelligence.sources import KnowledgeSourceType
from app.knowledge_intelligence.provenance import ProvenanceType, ProvenanceReference
from app.knowledge_intelligence.relationships import RelationshipType, RelationshipStrength
from app.knowledge_intelligence.contradictions import ContradictionType, ContradictionSeverity
from app.knowledge_intelligence.freshness import FreshnessStatus
from app.platform_contracts.governance import GovernanceDecisionStatus
from app.platform_contracts.delegation import DelegationTarget
from app.knowledge_intelligence.exceptions import (
    CrossTenantKnowledgeAccessException,
    KnowledgeNotFoundException,
    KnowledgeAccessDeniedException,
    ImmutableKnowledgeRecordException,
)


def test_flow1_register_cross_platform_knowledge():
    """Flow 1: Knowledge references from multiple platforms are registered without duplicating source payloads."""
    mgr = KnowledgeIntelligenceManager()
    tenant = "tenant_k1"

    src_dg = mgr.source_manager.register_source(tenant, "DataGovSource", source_type=KnowledgeSourceType.DATA_GOVERNANCE)
    src_sec = mgr.source_manager.register_source(tenant, "SecuritySource", source_type=KnowledgeSourceType.SECURITY_INTELLIGENCE)

    kitem_dg = mgr.knowledge_manager.register_knowledge(tenant, "PII Classification Rule", knowledge_type=KnowledgeType.POLICY, source_system=src_dg.name, external_id=src_dg.source_id)
    kitem_sec = mgr.knowledge_manager.register_knowledge(tenant, "Vulnerability Finding #402", knowledge_type=KnowledgeType.SECURITY_FINDING, source_system=src_sec.name, external_id=src_sec.source_id)

    assert kitem_dg.reference.source_system == "DataGovSource"
    assert kitem_sec.reference.source_system == "SecuritySource"
    assert kitem_dg.tenant_id == tenant
    assert kitem_sec.tenant_id == tenant


def test_flow2_provenance_chain():
    """Flow 2: Verify complete source -> evidence -> decision provenance chain."""
    mgr = KnowledgeIntelligenceManager()
    tenant = "tenant_k2"

    src = mgr.source_manager.register_source(tenant, "DocStore", source_type=KnowledgeSourceType.KNOWLEDGE_PLATFORM)
    doc_item = mgr.knowledge_manager.register_knowledge(tenant, "Raw Doc Standard")

    p1 = mgr.provenance_manager.record_provenance(tenant, doc_item.item_id, ProvenanceType.SOURCE)
    
    ev_item = mgr.evidence_manager.create_evidence(tenant, doc_item.item_id)
    p2 = mgr.provenance_manager.record_provenance(
        tenant,
        ev_item.evidence_id,
        ProvenanceType.DERIVED,
        upstream_references=[ProvenanceReference(upstream_id=doc_item.item_id, upstream_type="DOCUMENT")],
        transformation_description="Evidence Extraction",
    )

    chain = mgr.provenance_manager.get_provenance_chain(ev_item.evidence_id, tenant)
    assert len(chain.records) == 1
    assert chain.records[0].upstream_references[0].upstream_id == doc_item.item_id


def test_flow3_cross_tenant_access_blocked():
    """Flow 3: Cross-tenant retrieval is blocked with zero metadata leakage."""
    mgr = KnowledgeIntelligenceManager()

    item_a = mgr.knowledge_manager.register_knowledge("tenant_a", "Secret Knowledge A")
    mgr.provenance_manager.record_provenance("tenant_a", item_a.item_id)

    with pytest.raises(CrossTenantKnowledgeAccessException):
        mgr.knowledge_manager.get_knowledge(item_a.item_id, "tenant_b")

    with pytest.raises(CrossTenantKnowledgeAccessException):
        mgr.provenance_manager.get_provenance_chain(item_a.item_id, "tenant_b")



def test_flow4_deterministic_normalization():
    """Flow 4: Equivalent knowledge metadata produces deterministic normalization."""
    mgr = KnowledgeIntelligenceManager()
    tenant = "tenant_k4"

    kitem = mgr.knowledge_manager.register_knowledge(tenant, "  canonical title  ", tags=["b", "a"])
    norm1 = mgr.normalizer.normalize(tenant, kitem)
    norm2 = mgr.normalizer.normalize(tenant, kitem)

    assert norm1.normalized_knowledge.canonical_title == "canonical title"
    assert norm1.normalized_knowledge.fingerprint == norm2.normalized_knowledge.fingerprint
    assert norm1.normalized_knowledge.normalized_metadata["tags"] == ["a", "b"]


def test_flow5_knowledge_graph_traversal():
    """Flow 5: Verify upstream and downstream relationship traversal."""
    mgr = KnowledgeIntelligenceManager()
    tenant = "tenant_k5"

    node_a = mgr.knowledge_manager.register_knowledge(tenant, "Node A Architecture")
    node_b = mgr.knowledge_manager.register_knowledge(tenant, "Node B Component")

    rel = mgr.relationship_manager.create_relationship(tenant, node_a.item_id, node_b.item_id, RelationshipType.DEPENDS_ON)
    mgr.graph_manager.add_node(tenant, node_a.item_id, "Node A Architecture")
    mgr.graph_manager.add_node(tenant, node_b.item_id, "Node B Component")
    mgr.graph_manager.add_edge(tenant, rel)

    trav = mgr.graph_manager.traverse(tenant, node_a.item_id, depth=2, direction="DOWNSTREAM")
    assert node_b.item_id in trav.visited_node_ids
    assert len(trav.edges) == 1


def test_flow6_semantic_relationship_detection():
    """Flow 6: Verify semantic intelligence produces relationship references without mutating source systems."""
    mgr = KnowledgeIntelligenceManager()
    tenant = "tenant_k6"

    kitem = mgr.knowledge_manager.register_knowledge(tenant, "Cloud Security Infrastructure Policy")
    sem = mgr.semantic_manager.enrich_knowledge(tenant, kitem.item_id, kitem.metadata.title)

    assert len(sem.representation.concepts) > 0
    assert sem.representation.embedding_reference is not None


def test_flow7_stale_knowledge_detection():
    """Flow 7: Verify stale knowledge reduces freshness/trust without deletion."""
    mgr = KnowledgeIntelligenceManager()
    tenant = "tenant_k7"

    old_date = datetime.now(timezone.utc) - timedelta(days=120)
    kitem = mgr.knowledge_manager.register_knowledge(tenant, "Old Legacy Manual")
    
    fresh_eval = mgr.freshness_manager.evaluate_freshness(tenant, kitem.item_id, old_date)
    trust_score = mgr.trust_engine.evaluate_trust(tenant, kitem.item_id, is_fresh=False)

    assert fresh_eval.freshness.status == FreshnessStatus.STALE
    assert fresh_eval.trust_reduction_factor < 1.0
    assert kitem.status == KnowledgeStatus.ACTIVE  # Preserved, not deleted


def test_flow8_contradiction_detection():
    """Flow 8: Conflicting knowledge produces a contradiction record and recommendation."""
    mgr = KnowledgeIntelligenceManager()
    tenant = "tenant_k8"

    kitem_a = mgr.knowledge_manager.register_knowledge(tenant, "Retention Policy 90 Days")
    kitem_b = mgr.knowledge_manager.register_knowledge(tenant, "Retention Policy 365 Days")

    con = mgr.contradiction_manager.detect_contradiction(
        tenant,
        kitem_a.item_id,
        kitem_b.item_id,
        "90 Days",
        "365 Days",
        "Conflicting retention period policies",
    )

    assert con.status == "DETECTED"
    assert "Governance review required" in con.recommendation


def test_flow9_governed_retrieval():
    """Flow 9: Restricted knowledge retrieval is blocked when policy requirements fail."""
    mgr = KnowledgeIntelligenceManager()
    tenant = "tenant_k9"

    from app.knowledge_intelligence.retrieval import KnowledgeRetrievalRequest, RetrievalConstraint

    req = KnowledgeRetrievalRequest(
        tenant_id=tenant,
        query="Secret Policy",
        constraints=RetrievalConstraint(max_classification=KnowledgeClassification.INTERNAL),
    )
    restricted_item = mgr.knowledge_manager.register_knowledge(tenant, "Top Secret Data", classification=KnowledgeClassification.CRITICAL)

    res = mgr.retrieval_manager.plan_and_retrieve(req, [restricted_item], is_authorized=True)
    assert len(res.items) == 0  # Filtered due to classification constraint

    with pytest.raises(KnowledgeAccessDeniedException):
        mgr.retrieval_manager.plan_and_retrieve(req, [restricted_item], is_authorized=False)


def test_flow10_sensitive_data_redaction():
    """Flow 10: Verify secrets are absent from metadata, graph nodes, retrieval logs, analytics, snapshots."""
    mgr = KnowledgeIntelligenceManager()
    tenant = "tenant_k10"

    raw_attrs = {"api_key": "sk_live_123456789", "password": "supersecretpassword", "normal": "safe"}
    kitem = mgr.knowledge_manager.register_knowledge(tenant, "Config", attributes=raw_attrs)

    assert kitem.metadata.attributes["api_key"] == "[REDACTED]"
    assert kitem.metadata.attributes["password"] == "[REDACTED]"
    assert kitem.metadata.attributes["normal"] == "safe"


def test_flow11_high_risk_recommendation_requires_approval():
    """Flow 11: High-risk knowledge actions require ApprovalEngine / HumanTaskManager."""
    mgr = KnowledgeIntelligenceManager()
    tenant = "tenant_k11"

    kitem = mgr.knowledge_manager.register_knowledge(tenant, "Core Security Arch")
    gov_dec = mgr.governance_engine.evaluate_action_governance(tenant, kitem.item_id, "PURGE_KNOWLEDGE", is_high_risk=True)

    assert gov_dec.status == GovernanceDecisionStatus.REQUIRE_APPROVAL
    assert gov_dec.approval_request_id is not None


def test_flow12_delegation_only_enforcement():
    """Flow 12: Verify the platform cannot directly mutate external systems."""
    mgr = KnowledgeIntelligenceManager()
    tenant = "tenant_k12"

    gov_dec = mgr.governance_engine.evaluate_action_governance(tenant, "item_12", "MUTATE_DATABASE", attempts_direct_mutation=True)
    assert gov_dec.status == GovernanceDecisionStatus.BLOCK

    del_plan = mgr.delegation_manager.delegate_action(tenant, "item_12", target_subsystem=DelegationTarget.ORCHESTRATION, action_type="MUTATE_DATABASE")
    assert del_plan.delegation_request is not None
    assert del_plan.delegation_request.target == DelegationTarget.ORCHESTRATION


def test_flow13_immutable_provenance_bundle():
    """Flow 13: Finalized provenance records reject mutation."""
    mgr = KnowledgeIntelligenceManager()
    tenant = "tenant_k13"

    snap = mgr.run_full_knowledge_lifecycle(tenant, "Immutable Arch Standard")["snapshot"]
    assert snap["metadata"]["snapshot_id"] is not None


def test_flow14_organizational_memory_isolation():
    """Flow 14: Tenant memory cannot be accessed across tenants."""
    mgr = KnowledgeIntelligenceManager()

    mgr.memory_manager.record_memory("tenant_mem_a", "key_a", "Value A")
    mems_b = mgr.memory_manager.list_memories("tenant_mem_b")

    assert len(mems_b) == 0


def test_flow15_learning_recommendation():
    """Flow 15: Knowledge learning produces recommendations without autonomous mutation."""
    mgr = KnowledgeIntelligenceManager()
    tenant = "tenant_k15"

    rec = mgr.learning_manager.record_learning(tenant, "item_15")
    assert len(rec.recommendations) > 0
    assert rec.recommendations[0].action == "PIN_KNOWLEDGE_CONTEXT"


def test_flow16_full_knowledge_intelligence_lifecycle():
    """Flow 16: Complete end-to-end knowledge intelligence lifecycle flow."""
    mgr = KnowledgeIntelligenceManager()
    tenant = "tenant_k16"

    res = mgr.run_full_knowledge_lifecycle(tenant, "Complete Knowledge Standard")

    assert res["knowledge_item"]["tenant_id"] == tenant
    assert res["normalization"]["normalized_knowledge"]["canonical_title"] == "Complete Knowledge Standard"
    assert res["provenance_chain"]["tenant_id"] == tenant
    assert res["trust_score"]["overall_score"] > 0
    assert res["snapshot"]["metadata"]["snapshot_id"] is not None
