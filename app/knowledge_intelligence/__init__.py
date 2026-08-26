"""Enterprise AI Knowledge Intelligence Platform Package (Phase 5.35)."""

from app.knowledge_intelligence.exceptions import (
    KnowledgeIntelligenceException,
    CrossTenantKnowledgeAccessException,
    KnowledgeNotFoundException,
    KnowledgeSourceNotFoundException,
    KnowledgeProvenanceException,
    KnowledgeIntegrityException,
    KnowledgeAccessDeniedException,
    KnowledgeRetrievalBlockedException,
    KnowledgePolicyViolationException,
    KnowledgeGraphException,
    KnowledgeRelationshipNotFoundException,
    ImmutableKnowledgeRecordException,
    KnowledgeRecommendationBlockedException,
    KnowledgeDelegationBlockedException,
    KnowledgeEvidenceValidationException,
    KnowledgeLearningException,
)

from app.knowledge_intelligence.knowledge import (
    KnowledgeItem,
    KnowledgeType,
    KnowledgeStatus,
    KnowledgeClassification,
    KnowledgeOrigin,
    KnowledgeMetadata,
    KnowledgeReference,
    KnowledgeManager,
)

from app.knowledge_intelligence.sources import (
    KnowledgeSource,
    KnowledgeSourceType,
    KnowledgeSourceStatus,
    KnowledgeSourceCapability,
    KnowledgeSourceReference,
    KnowledgeSourceManager,
)

from app.knowledge_intelligence.normalization import (
    NormalizedKnowledge,
    KnowledgeNormalizationRule,
    KnowledgeNormalizationResult,
    KnowledgeNormalizer,
)

from app.knowledge_intelligence.provenance import (
    KnowledgeProvenance,
    ProvenanceRecord,
    ProvenanceType,
    ProvenanceChain,
    ProvenanceReference,
    ProvenanceIntegrity,
    KnowledgeProvenanceManager,
)

from app.knowledge_intelligence.relationships import (
    KnowledgeRelationship,
    RelationshipType,
    RelationshipStrength,
    RelationshipDirection,
    RelationshipEvidence,
    KnowledgeRelationshipManager,
)

from app.knowledge_intelligence.graph import (
    KnowledgeGraph,
    KnowledgeGraphNode,
    KnowledgeGraphEdge,
    GraphTraversal,
    GraphTraversalResult,
    KnowledgeGraphManager,
)

from app.knowledge_intelligence.semantic import (
    SemanticRepresentation,
    SemanticConcept,
    SemanticEntity,
    SemanticRelationship,
    SemanticSimilarity,
    SemanticEnrichmentResult,
    SemanticIntelligenceManager,
)

from app.knowledge_intelligence.evidence import (
    KnowledgeEvidence,
    KnowledgeEvidenceBundle,
    KnowledgeEvidenceStrength,
    KnowledgeEvidenceIntegrity,
    KnowledgeEvidenceManager,
)

from app.knowledge_intelligence.trust import (
    KnowledgeTrustScore,
    KnowledgeTrustDimension,
    KnowledgeTrustFactor,
    KnowledgeTrustEngine,
)

from app.knowledge_intelligence.freshness import (
    KnowledgeFreshness,
    FreshnessStatus,
    FreshnessPolicy,
    FreshnessEvaluation,
    KnowledgeFreshnessManager,
)

from app.knowledge_intelligence.contradictions import (
    KnowledgeContradiction,
    ContradictionType,
    ContradictionSeverity,
    ContradictionStatus,
    ContradictionEvidence,
    KnowledgeContradictionManager,
)

from app.knowledge_intelligence.retrieval import (
    KnowledgeRetrievalRequest,
    RetrievalStrategy,
    RetrievalConstraint,
    RetrievalResult,
    RetrievalEvidence,
    KnowledgeRetrievalManager,
)

from app.knowledge_intelligence.context import (
    KnowledgeContext,
    KnowledgeContextItem,
    KnowledgeContextReference,
    ContextAssemblyPlan,
    KnowledgeContextBuilder,
    KnowledgeContextManager,
)

from app.knowledge_intelligence.recommendations import (
    KnowledgeRecommendation,
    KnowledgeRecommendationType,
    RecommendationPriority,
    RecommendationConfidence,
    RecommendationStatus,
    KnowledgeRecommendationEngine,
)

from app.knowledge_intelligence.governance import (
    KnowledgeGovernanceDecision,
    KnowledgeGovernanceStatus,
    KnowledgeGovernanceRequirement,
    KnowledgeGovernanceEngine,
)

from app.knowledge_intelligence.delegation import (
    KnowledgeDelegationPlan,
    KnowledgeDelegationAction,
    KnowledgeDelegationManager,
)

from app.knowledge_intelligence.investigations import (
    KnowledgeInvestigation,
    KnowledgeInvestigationStatus,
    KnowledgeFinding,
    KnowledgeInvestigationManager,
)

from app.knowledge_intelligence.memory import (
    OrganizationalMemory,
    MemoryType,
    MemoryScope,
    MemoryRetentionStatus,
    MemoryReference,
    OrganizationalMemoryManager,
)

from app.knowledge_intelligence.learning import (
    KnowledgeLearningRecord,
    KnowledgePattern,
    KnowledgeLearningSignal,
    KnowledgeLearningRecommendation,
    KnowledgeLearningManager,
)

from app.knowledge_intelligence.analytics import (
    KnowledgeAnalyticsEngine,
    KnowledgeReport,
    KnowledgeInsight,
)

from app.knowledge_intelligence.observability import (
    KnowledgeMetricsCollector,
)

from app.knowledge_intelligence.billing import (
    KnowledgeCostEvent,
    KnowledgeBillingTracker,
)

from app.knowledge_intelligence.repositories import (
    KnowledgeRepository,
    KnowledgeSourceRepository,
    ProvenanceRepository,
    KnowledgeRelationshipRepository,
    KnowledgeInvestigationRepository,
    MemoryRepository,
)

from app.knowledge_intelligence.manager import (
    KnowledgeIntelligenceManager,
)

__all__ = [
    "KnowledgeIntelligenceException",
    "CrossTenantKnowledgeAccessException",
    "KnowledgeNotFoundException",
    "KnowledgeSourceNotFoundException",
    "KnowledgeProvenanceException",
    "KnowledgeIntegrityException",
    "KnowledgeAccessDeniedException",
    "KnowledgeRetrievalBlockedException",
    "KnowledgePolicyViolationException",
    "KnowledgeGraphException",
    "KnowledgeRelationshipNotFoundException",
    "ImmutableKnowledgeRecordException",
    "KnowledgeRecommendationBlockedException",
    "KnowledgeDelegationBlockedException",
    "KnowledgeEvidenceValidationException",
    "KnowledgeLearningException",
    "KnowledgeItem",
    "KnowledgeType",
    "KnowledgeStatus",
    "KnowledgeClassification",
    "KnowledgeOrigin",
    "KnowledgeMetadata",
    "KnowledgeReference",
    "KnowledgeManager",
    "KnowledgeSource",
    "KnowledgeSourceType",
    "KnowledgeSourceStatus",
    "KnowledgeSourceCapability",
    "KnowledgeSourceReference",
    "KnowledgeSourceManager",
    "NormalizedKnowledge",
    "KnowledgeNormalizationRule",
    "KnowledgeNormalizationResult",
    "KnowledgeNormalizer",
    "KnowledgeProvenance",
    "ProvenanceRecord",
    "ProvenanceType",
    "ProvenanceChain",
    "ProvenanceReference",
    "ProvenanceIntegrity",
    "KnowledgeProvenanceManager",
    "KnowledgeRelationship",
    "RelationshipType",
    "RelationshipStrength",
    "RelationshipDirection",
    "RelationshipEvidence",
    "KnowledgeRelationshipManager",
    "KnowledgeGraph",
    "KnowledgeGraphNode",
    "KnowledgeGraphEdge",
    "GraphTraversal",
    "GraphTraversalResult",
    "KnowledgeGraphManager",
    "SemanticRepresentation",
    "SemanticConcept",
    "SemanticEntity",
    "SemanticRelationship",
    "SemanticSimilarity",
    "SemanticEnrichmentResult",
    "SemanticIntelligenceManager",
    "KnowledgeEvidence",
    "KnowledgeEvidenceBundle",
    "KnowledgeEvidenceStrength",
    "KnowledgeEvidenceIntegrity",
    "KnowledgeEvidenceManager",
    "KnowledgeTrustScore",
    "KnowledgeTrustDimension",
    "KnowledgeTrustFactor",
    "KnowledgeTrustEngine",
    "KnowledgeFreshness",
    "FreshnessStatus",
    "FreshnessPolicy",
    "FreshnessEvaluation",
    "KnowledgeFreshnessManager",
    "KnowledgeContradiction",
    "ContradictionType",
    "ContradictionSeverity",
    "ContradictionStatus",
    "ContradictionEvidence",
    "KnowledgeContradictionManager",
    "KnowledgeRetrievalRequest",
    "RetrievalStrategy",
    "RetrievalConstraint",
    "RetrievalResult",
    "RetrievalEvidence",
    "KnowledgeRetrievalManager",
    "KnowledgeContext",
    "KnowledgeContextItem",
    "KnowledgeContextReference",
    "ContextAssemblyPlan",
    "KnowledgeContextBuilder",
    "KnowledgeContextManager",
    "KnowledgeRecommendation",
    "KnowledgeRecommendationType",
    "RecommendationPriority",
    "RecommendationConfidence",
    "RecommendationStatus",
    "KnowledgeRecommendationEngine",
    "KnowledgeGovernanceDecision",
    "KnowledgeGovernanceStatus",
    "KnowledgeGovernanceRequirement",
    "KnowledgeGovernanceEngine",
    "KnowledgeDelegationPlan",
    "KnowledgeDelegationAction",
    "KnowledgeDelegationManager",
    "KnowledgeInvestigation",
    "KnowledgeInvestigationStatus",
    "KnowledgeFinding",
    "KnowledgeInvestigationManager",
    "OrganizationalMemory",
    "MemoryType",
    "MemoryScope",
    "MemoryRetentionStatus",
    "MemoryReference",
    "OrganizationalMemoryManager",
    "KnowledgeLearningRecord",
    "KnowledgePattern",
    "KnowledgeLearningSignal",
    "KnowledgeLearningRecommendation",
    "KnowledgeLearningManager",
    "KnowledgeAnalyticsEngine",
    "KnowledgeReport",
    "KnowledgeInsight",
    "KnowledgeMetricsCollector",
    "KnowledgeCostEvent",
    "KnowledgeBillingTracker",
    "KnowledgeRepository",
    "KnowledgeSourceRepository",
    "ProvenanceRepository",
    "KnowledgeRelationshipRepository",
    "KnowledgeInvestigationRepository",
    "MemoryRepository",
    "KnowledgeIntelligenceManager",
]
