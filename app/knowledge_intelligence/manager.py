"""Master Knowledge Intelligence Orchestrator Subsystem (Phase 5.35)."""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from app.knowledge_intelligence.exceptions import (
    CrossTenantKnowledgeAccessException,
    KnowledgeNotFoundException,
    ImmutableKnowledgeRecordException,
)
from app.knowledge_intelligence.knowledge import (
    KnowledgeItem,
    KnowledgeType,
    KnowledgeStatus,
    KnowledgeClassification,
    KnowledgeOrigin,
    KnowledgeManager,
)
from app.knowledge_intelligence.sources import (
    KnowledgeSource,
    KnowledgeSourceType,
    KnowledgeSourceManager,
)
from app.knowledge_intelligence.normalization import KnowledgeNormalizer, KnowledgeNormalizationResult
from app.knowledge_intelligence.provenance import (
    KnowledgeProvenanceManager,
    ProvenanceRecord,
    ProvenanceType,
    ProvenanceReference,
    ProvenanceChain,
)
from app.knowledge_intelligence.relationships import (
    KnowledgeRelationshipManager,
    KnowledgeRelationship,
    RelationshipType,
    RelationshipStrength,
)
from app.knowledge_intelligence.graph import KnowledgeGraphManager, GraphTraversalResult
from app.knowledge_intelligence.semantic import SemanticIntelligenceManager, SemanticRepresentation
from app.knowledge_intelligence.evidence import KnowledgeEvidenceManager, KnowledgeEvidenceBundle
from app.knowledge_intelligence.trust import KnowledgeTrustEngine, KnowledgeTrustScore
from app.knowledge_intelligence.freshness import KnowledgeFreshnessManager, FreshnessEvaluation
from app.knowledge_intelligence.contradictions import KnowledgeContradictionManager, KnowledgeContradiction, ContradictionType
from app.knowledge_intelligence.retrieval import KnowledgeRetrievalManager, KnowledgeRetrievalRequest, RetrievalResult
from app.knowledge_intelligence.context import KnowledgeContextManager, KnowledgeContext
from app.knowledge_intelligence.recommendations import KnowledgeRecommendationEngine, KnowledgeRecommendation, KnowledgeRecommendationType
from app.knowledge_intelligence.governance import KnowledgeGovernanceEngine, KnowledgeGovernanceDecision
from app.knowledge_intelligence.delegation import KnowledgeDelegationManager, KnowledgeDelegationPlan
from app.knowledge_intelligence.investigations import KnowledgeInvestigationManager, KnowledgeInvestigation
from app.knowledge_intelligence.memory import OrganizationalMemoryManager, OrganizationalMemory
from app.knowledge_intelligence.learning import KnowledgeLearningManager, KnowledgeLearningRecord
from app.knowledge_intelligence.analytics import KnowledgeAnalyticsEngine
from app.knowledge_intelligence.observability import KnowledgeMetricsCollector
from app.knowledge_intelligence.billing import KnowledgeBillingTracker
from app.platform_contracts.snapshots import SnapshotFactory, PlatformSnapshot
from app.platform_contracts.redaction import SensitiveDataSanitizer

logger = logging.getLogger(__name__)


class KnowledgeIntelligenceManager:
    """Master Enterprise AI Knowledge Intelligence Orchestrator coordinating all 24 domain subsystems."""

    def __init__(self) -> None:
        self.knowledge_manager = KnowledgeManager()
        self.source_manager = KnowledgeSourceManager()
        self.normalizer = KnowledgeNormalizer()
        self.provenance_manager = KnowledgeProvenanceManager()
        self.relationship_manager = KnowledgeRelationshipManager()
        self.graph_manager = KnowledgeGraphManager()
        self.semantic_manager = SemanticIntelligenceManager()
        self.evidence_manager = KnowledgeEvidenceManager()
        self.trust_engine = KnowledgeTrustEngine()
        self.freshness_manager = KnowledgeFreshnessManager()
        self.contradiction_manager = KnowledgeContradictionManager()
        self.retrieval_manager = KnowledgeRetrievalManager()
        self.context_manager = KnowledgeContextManager()
        self.recommendation_engine = KnowledgeRecommendationEngine()
        self.governance_engine = KnowledgeGovernanceEngine()
        self.delegation_manager = KnowledgeDelegationManager()
        self.investigation_manager = KnowledgeInvestigationManager()
        self.memory_manager = OrganizationalMemoryManager()
        self.learning_manager = KnowledgeLearningManager()
        self.analytics_engine = KnowledgeAnalyticsEngine()
        self.metrics_collector = KnowledgeMetricsCollector()
        self.billing_tracker = KnowledgeBillingTracker()
        
        # Immutable snapshot registry
        self._finalized_snapshots: Dict[str, PlatformSnapshot] = {}
        logger.info("[KNOWLEDGE INTELLIGENCE MASTER] KnowledgeIntelligenceManager initialized with 24 subsystems.")

    def run_full_knowledge_lifecycle(
        self,
        tenant_id: str,
        title: str = "Enterprise Architecture Standard",
        source_name: str = "ArchitecturePlatform",
        is_high_risk: bool = False,
    ) -> Dict[str, Any]:
        # 1. Source registration reference
        src = self.source_manager.register_source(
            tenant_id=tenant_id,
            name=source_name,
            source_type=KnowledgeSourceType.ARCHITECTURE_PLATFORM,
        )

        # 2. Knowledge item registration reference
        kitem = self.knowledge_manager.register_knowledge(
            tenant_id=tenant_id,
            title=title,
            knowledge_type=KnowledgeType.ARCHITECTURE,
            classification=KnowledgeClassification.INTERNAL,
            source_system=src.name,
            external_id=src.source_id,
        )

        # 3. Normalization
        norm_res = self.normalizer.normalize(tenant_id, kitem)

        # 4. Provenance capture
        prov_rec = self.provenance_manager.record_provenance(
            tenant_id=tenant_id,
            target_id=kitem.item_id,
            provenance_type=ProvenanceType.SOURCE,
            upstream_references=[ProvenanceReference(upstream_id=src.source_id, upstream_type="KNOWLEDGE_SOURCE")],
            transformation_description="Source Registration Provenance",
        )
        prov_chain = self.provenance_manager.get_provenance_chain(kitem.item_id, tenant_id)

        # 5. Semantic enrichment
        sem_res = self.semantic_manager.enrich_knowledge(tenant_id, kitem.item_id, title)

        # 6. Relationship & Graph Update
        rel = self.relationship_manager.create_relationship(
            tenant_id=tenant_id,
            source_id=kitem.item_id,
            target_id=src.source_id,
            relationship_type=RelationshipType.DERIVED_FROM,
        )
        self.graph_manager.add_node(tenant_id, kitem.item_id, title)
        self.graph_manager.add_node(tenant_id, src.source_id, src.name)
        self.graph_manager.add_edge(tenant_id, rel)
        graph_trav = self.graph_manager.traverse(tenant_id, kitem.item_id)

        # 7. Evidence Bundle
        ev_item = self.evidence_manager.create_evidence(tenant_id, kitem.item_id, source_subsystem=src.name)
        ev_bundle = self.evidence_manager.assemble_bundle(tenant_id, kitem.item_id, [ev_item])

        # 8. Freshness evaluation
        fresh_eval = self.freshness_manager.evaluate_freshness(tenant_id, kitem.item_id, kitem.updated_at)

        # 9. Contradiction analysis
        # Create secondary item to test contradiction detection
        kitem_alt = self.knowledge_manager.register_knowledge(
            tenant_id=tenant_id,
            title=f"{title} Alt",
            knowledge_type=KnowledgeType.ARCHITECTURE,
        )
        con = self.contradiction_manager.detect_contradiction(
            tenant_id=tenant_id,
            item_a_id=kitem.item_id,
            item_b_id=kitem_alt.item_id,
            item_a_statement="Microservices architecture",
            item_b_statement="Monolithic architecture",
            discrepancy="Architectural pattern conflict",
        )

        # 10. Trust evaluation
        trust_score = self.trust_engine.evaluate_trust(
            tenant_id=tenant_id,
            item_id=kitem.item_id,
            is_fresh=(fresh_eval.freshness.status.name == "FRESH"),
            has_provenance=True,
            evidence_count=len(ev_bundle.items),
            contradiction_count=1,
        )
        trust_assessment = self.trust_engine.to_trust_assessment(trust_score)

        # 11. Governed Retrieval
        req = KnowledgeRetrievalRequest(tenant_id=tenant_id, query=title)
        ret_res = self.retrieval_manager.plan_and_retrieve(req, [kitem, kitem_alt])

        # 12. Context Assembly
        ctx = self.context_manager.create_context(tenant_id, ret_res.items)

        # 13. Recommendations
        rec = self.recommendation_engine.create_recommendation(
            tenant_id=tenant_id,
            target_id=kitem.item_id,
            title="Resolve Architectural Contradiction",
            rationale="Contradiction detected with alternative standard",
            recommendation_type=KnowledgeRecommendationType.RESOLVE_CONTRADICTION,
            is_high_risk=is_high_risk,
        )

        # 14. Governance Evaluation
        gov_dec = self.governance_engine.evaluate_action_governance(
            tenant_id=tenant_id,
            target_id=kitem.item_id,
            action_name="RESOLVE_KNOWLEDGE_CONTRADICTION",
            is_high_risk=is_high_risk,
        )

        # 15. Action Delegation
        del_plan = self.delegation_manager.delegate_action(
            tenant_id=tenant_id,
            target_id=kitem.item_id,
            action_type="UPDATE_KNOWLEDGE_INDEX",
        )

        # 16. Organizational Memory Recording
        omem = self.memory_manager.record_memory(
            tenant_id=tenant_id,
            key=f"architecture_standard:{kitem.item_id}",
            value_summary=title,
            reference_id=kitem.item_id,
        )

        # 17. Learning
        learn_rec = self.learning_manager.record_learning(tenant_id, kitem.item_id)

        # 18. Immutable Snapshot
        snap = SnapshotFactory.create_snapshot(
            tenant_id=tenant_id,
            resource_type="KNOWLEDGE_PROVENANCE_BUNDLE",
            resource_id=kitem.item_id,
            domain_payload={"provenance_chain": prov_chain.model_dump()},
        )
        self._finalized_snapshots[snap.metadata.snapshot_id] = snap

        # 19. Analytics & Cost
        report = self.analytics_engine.generate_report(tenant_id, total_items=2, stale_count=0, contradiction_count=1)
        self.metrics_collector.increment("ai_knowledge_retrieval_total")
        self.billing_tracker.record_knowledge_cost(tenant_id, kitem.item_id, 0.05, "Lifecycle run")

        return {
            "source": src.model_dump(),
            "knowledge_item": kitem.model_dump(),
            "normalization": norm_res.model_dump(),
            "provenance_chain": prov_chain.model_dump(),
            "semantic": sem_res.model_dump(),
            "graph_traversal": graph_trav.model_dump(),
            "evidence_bundle": ev_bundle.model_dump(),
            "freshness": fresh_eval.model_dump(),
            "contradiction": con.model_dump(),
            "trust_score": trust_score.model_dump(),
            "trust_assessment": trust_assessment.model_dump(),
            "retrieval": ret_res.model_dump(),
            "context": ctx.model_dump(),
            "recommendation": rec.model_dump(),
            "governance_decision": gov_dec.model_dump(),
            "delegation_plan": del_plan.model_dump(),
            "organizational_memory": omem.model_dump(),
            "learning": learn_rec.model_dump(),
            "snapshot": snap.model_dump(),
            "report": report.model_dump(),
        }
