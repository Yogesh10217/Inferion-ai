"""Knowledge Assurance Orchestrator Module.

Master KnowledgeAssuranceManager that coordinates all knowledge lifecycle, trust,
assurance, governance, context assembly, and correlation sub-managers.
"""

from typing import Any, Dict

from app.knowledge_assurance.analytics import KnowledgeAnalyticsManager
from app.knowledge_assurance.assurance import KnowledgeContinuousAssuranceManager
from app.knowledge_assurance.billing import KnowledgeBillingTracker
from app.knowledge_assurance.confidence import KnowledgeConfidenceManager
from app.knowledge_assurance.conflicts import KnowledgeConflictManager
from app.knowledge_assurance.consistency import KnowledgeConsistencyManager
from app.knowledge_assurance.context import KnowledgeContextManager
from app.knowledge_assurance.context_assembly import ContextAssemblyManager
from app.knowledge_assurance.correlation import KnowledgeCorrelationManager
from app.knowledge_assurance.coverage import KnowledgeCoverageManager
from app.knowledge_assurance.decision_context import DecisionContextManager
from app.knowledge_assurance.delegation import KnowledgeDelegationManager
from app.knowledge_assurance.duplication import KnowledgeDuplicationManager
from app.knowledge_assurance.evidence import KnowledgeEvidenceManager
from app.knowledge_assurance.freshness import KnowledgeFreshnessManager
from app.knowledge_assurance.gaps import KnowledgeGapManager
from app.knowledge_assurance.governance import KnowledgeGovernanceEngine
from app.knowledge_assurance.investigations import KnowledgeInvestigationManager
from app.knowledge_assurance.knowledge_graph import KnowledgeGraphManager
from app.knowledge_assurance.knowledge_references import KnowledgeReferenceManager
from app.knowledge_assurance.learning import KnowledgeLearningManager
from app.knowledge_assurance.observability import KnowledgeAssuranceMetrics
from app.knowledge_assurance.provenance import KnowledgeProvenanceManager
from app.knowledge_assurance.relevance import KnowledgeRelevanceManager
from app.knowledge_assurance.remediation import KnowledgeRemediationManager
from app.knowledge_assurance.risk import KnowledgeRiskManager
from app.knowledge_assurance.semantic_context import SemanticContextManager
from app.knowledge_assurance.signals import KnowledgeSignalManager
from app.knowledge_assurance.snapshots import KnowledgeAssuranceSnapshotManager
from app.knowledge_assurance.sources import KnowledgeSourceManager
from app.knowledge_assurance.trust import KnowledgeTrustEngine
from app.knowledge_assurance.verification import KnowledgeVerificationManager


class KnowledgeAssuranceManager:
    """Master Knowledge Assurance Orchestrator for Phase 5.46 platform."""

    def __init__(self) -> None:
        self.references_manager = KnowledgeReferenceManager()
        self.sources_manager = KnowledgeSourceManager()
        self.context_manager = KnowledgeContextManager()
        self.context_assembly_manager = ContextAssemblyManager()
        self.semantic_context_manager = SemanticContextManager()
        self.graph_manager = KnowledgeGraphManager()
        self.provenance_manager = KnowledgeProvenanceManager()
        self.freshness_manager = KnowledgeFreshnessManager()
        self.trust_engine = KnowledgeTrustEngine()
        self.confidence_manager = KnowledgeConfidenceManager()
        self.relevance_manager = KnowledgeRelevanceManager()
        self.conflict_manager = KnowledgeConflictManager()
        self.consistency_manager = KnowledgeConsistencyManager()
        self.duplication_manager = KnowledgeDuplicationManager()
        self.gap_manager = KnowledgeGapManager()
        self.coverage_manager = KnowledgeCoverageManager()
        self.correlation_manager = KnowledgeCorrelationManager()
        self.signal_manager = KnowledgeSignalManager()
        self.decision_context_manager = DecisionContextManager()
        self.governance_engine = KnowledgeGovernanceEngine()
        self.risk_manager = KnowledgeRiskManager()
        self.investigation_manager = KnowledgeInvestigationManager()
        self.remediation_manager = KnowledgeRemediationManager()
        self.delegation_manager = KnowledgeDelegationManager()
        self.verification_manager = KnowledgeVerificationManager()
        self.evidence_manager = KnowledgeEvidenceManager()
        self.assurance_manager = KnowledgeContinuousAssuranceManager()
        self.snapshot_manager = KnowledgeAssuranceSnapshotManager()
        self.learning_manager = KnowledgeLearningManager()
        self.analytics_manager = KnowledgeAnalyticsManager()
        self.metrics = KnowledgeAssuranceMetrics()
        self.billing = KnowledgeBillingTracker()

    def get_status(self, tenant_id: str) -> Dict[str, Any]:
        """Provides status summary for tenant knowledge assurance layer."""
        refs = self.references_manager.list_references(tenant_id)
        sources = self.sources_manager.list_sources(tenant_id)
        conflicts = self.conflict_manager.list_conflicts(tenant_id)
        ass_score = self.assurance_manager.assess_knowledge_assurance(
            tenant_id=tenant_id, target_resource_id="ORGANIZATION_SUMMARY"
        )
        return {
            "tenant_id": tenant_id,
            "status": "OPERATIONAL",
            "active_references_count": len(refs),
            "sources_count": len(sources),
            "conflicts_count": len(conflicts),
            "assurance_score": ass_score.assurance_score.overall_score,
            "assurance_level": ass_score.assurance_score.assurance_level,
        }
