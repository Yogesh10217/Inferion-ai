"""
Phase 5.51 Enterprise AI Unified Intelligence, Cross-Domain Reasoning & Autonomous Assurance Coordination Platform.

Package exports for unified intelligence platform capabilities.
"""

from app.unified_intelligence.analytics import CrossDomainAnalyticsEngine, UnifiedAnalyticsSummary
from app.unified_intelligence.assurance_coordination import CrossDomainAssuranceCoordinator, UnifiedAssurancePosture
from app.unified_intelligence.billing import IntelligenceBillingEngine, UnifiedBillingRecord
from app.unified_intelligence.causal_analysis import CausalAnalysisEngine, CausalHypothesis, CausalStatus
from app.unified_intelligence.confidence import ConfidenceCalculator
from app.unified_intelligence.context_fusion import ContextFusionEngine, UnifiedContext, UnifiedContextPolicy
from app.unified_intelligence.coordination import CoordinationPlan, CoordinationPlannerEngine, CoordinationStep
from app.unified_intelligence.correlation import CorrelationGroup, CrossDomainCorrelationEngine
from app.unified_intelligence.delegation import AutonomousDelegationEngine
from app.unified_intelligence.dependency_intelligence import DependencyGraph, DependencyIntelligenceEngine
from app.unified_intelligence.domains import IntelligenceDomain
from app.unified_intelligence.evidence import SHA256EvidenceLedgerEngine, UnifiedEvidenceRecord
from app.unified_intelligence.exceptions import (
    CrossTenantUnifiedIntelligenceException,
    GovernanceUnifiedPolicyViolationException,
    HighRiskUnifiedActionRequiresApprovalException,
    ImmutableUnifiedIntelligenceRecordException,
    InvalidUnifiedIntelligenceInputException,
    UnifiedIntelligenceException,
    UnifiedIntelligenceProviderUnavailableException,
)
from app.unified_intelligence.governance import GovernanceEvaluationResult, GovernancePolicyEvaluatorEngine
from app.unified_intelligence.idempotency import IdempotencyEngine
from app.unified_intelligence.impact import UnifiedImpactAssessment, UnifiedImpactEngine
from app.unified_intelligence.investigations import UnifiedInvestigation, UnifiedInvestigationEngine
from app.unified_intelligence.learning import AdvisoryLearningEngine, AdvisoryModelInsight
from app.unified_intelligence.manager import UnifiedIntelligenceManager
from app.unified_intelligence.normalization_contracts import NormalizedSignal, UnifiedDomainInput
from app.unified_intelligence.observability import UnifiedObservabilityEngine
from app.unified_intelligence.providers import (
    BaseIntelligenceProvider,
    IntelligenceProvider,
    IntelligenceProviderRegistry,
)
from app.unified_intelligence.recommendations import UnifiedRecommendation, UnifiedRecommendationEngine
from app.unified_intelligence.remediation import CrossDomainRemediationCoordinator, RemediationActionResult
from app.unified_intelligence.repositories import UnifiedIntelligenceRepository
from app.unified_intelligence.risk import UnifiedRiskAssessment, UnifiedRiskEngine
from app.unified_intelligence.risk_propagation import RiskPropagationEngine, RiskPropagationGraph
from app.unified_intelligence.signal_normalization import SignalNormalizationEngine
from app.unified_intelligence.signals import UnifiedSignal
from app.unified_intelligence.situation_awareness import (
    EnterpriseSituation,
    SituationAwarenessEngine,
    SituationSeverity,
    SituationStatus,
)
from app.unified_intelligence.snapshots import UnifiedSnapshotGenerator
from app.unified_intelligence.timeline import CorrelationTimeline, UnifiedTimelineEngine
from app.unified_intelligence.trust import CrossDomainTrustEngine, UnifiedTrustAssessment
from app.unified_intelligence.verification import DelegationVerificationEngine, UnifiedVerificationResult

__all__ = [
    "UnifiedIntelligenceException",
    "CrossTenantUnifiedIntelligenceException",
    "InvalidUnifiedIntelligenceInputException",
    "UnifiedIntelligenceProviderUnavailableException",
    "HighRiskUnifiedActionRequiresApprovalException",
    "ImmutableUnifiedIntelligenceRecordException",
    "GovernanceUnifiedPolicyViolationException",
    "IntelligenceDomain",
    "IntelligenceProvider",
    "BaseIntelligenceProvider",
    "IntelligenceProviderRegistry",
    "UnifiedDomainInput",
    "NormalizedSignal",
    "ConfidenceCalculator",
    "UnifiedSignal",
    "SignalNormalizationEngine",
    "ContextFusionEngine",
    "UnifiedContextPolicy",
    "UnifiedContext",
    "CrossDomainCorrelationEngine",
    "CorrelationGroup",
    "CausalAnalysisEngine",
    "CausalHypothesis",
    "CausalStatus",
    "DependencyIntelligenceEngine",
    "DependencyGraph",
    "RiskPropagationEngine",
    "RiskPropagationGraph",
    "SituationAwarenessEngine",
    "EnterpriseSituation",
    "SituationStatus",
    "SituationSeverity",
    "UnifiedTimelineEngine",
    "CorrelationTimeline",
    "UnifiedImpactEngine",
    "UnifiedImpactAssessment",
    "UnifiedRiskEngine",
    "UnifiedRiskAssessment",
    "CrossDomainAssuranceCoordinator",
    "UnifiedAssurancePosture",
    "CrossDomainTrustEngine",
    "UnifiedTrustAssessment",
    "UnifiedRecommendationEngine",
    "UnifiedRecommendation",
    "CoordinationPlannerEngine",
    "CoordinationPlan",
    "CoordinationStep",
    "GovernancePolicyEvaluatorEngine",
    "GovernanceEvaluationResult",
    "UnifiedInvestigationEngine",
    "UnifiedInvestigation",
    "CrossDomainRemediationCoordinator",
    "RemediationActionResult",
    "AutonomousDelegationEngine",
    "DelegationVerificationEngine",
    "UnifiedVerificationResult",
    "SHA256EvidenceLedgerEngine",
    "UnifiedEvidenceRecord",
    "UnifiedSnapshotGenerator",
    "AdvisoryLearningEngine",
    "AdvisoryModelInsight",
    "CrossDomainAnalyticsEngine",
    "UnifiedAnalyticsSummary",
    "UnifiedObservabilityEngine",
    "IntelligenceBillingEngine",
    "UnifiedBillingRecord",
    "IdempotencyEngine",
    "UnifiedIntelligenceRepository",
    "UnifiedIntelligenceManager",
]
