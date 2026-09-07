"""
Phase 5.51 Enterprise AI Unified Intelligence, Cross-Domain Reasoning & Autonomous Assurance Coordination Platform.

Package exports for unified intelligence platform capabilities.
"""

from app.unified_intelligence.exceptions import (
    UnifiedIntelligenceException,
    CrossTenantUnifiedIntelligenceException,
    InvalidUnifiedIntelligenceInputException,
    UnifiedIntelligenceProviderUnavailableException,
    HighRiskUnifiedActionRequiresApprovalException,
    ImmutableUnifiedIntelligenceRecordException,
    GovernanceUnifiedPolicyViolationException
)
from app.unified_intelligence.domains import IntelligenceDomain
from app.unified_intelligence.providers import (
    IntelligenceProvider,
    BaseIntelligenceProvider,
    IntelligenceProviderRegistry
)
from app.unified_intelligence.normalization_contracts import UnifiedDomainInput, NormalizedSignal
from app.unified_intelligence.confidence import ConfidenceCalculator
from app.unified_intelligence.signals import UnifiedSignal
from app.unified_intelligence.signal_normalization import SignalNormalizationEngine
from app.unified_intelligence.context_fusion import ContextFusionEngine, UnifiedContextPolicy, UnifiedContext
from app.unified_intelligence.correlation import CrossDomainCorrelationEngine, CorrelationGroup
from app.unified_intelligence.causal_analysis import CausalAnalysisEngine, CausalHypothesis, CausalStatus
from app.unified_intelligence.dependency_intelligence import DependencyIntelligenceEngine, DependencyGraph
from app.unified_intelligence.risk_propagation import RiskPropagationEngine, RiskPropagationGraph
from app.unified_intelligence.situation_awareness import (
    SituationAwarenessEngine,
    EnterpriseSituation,
    SituationStatus,
    SituationSeverity
)
from app.unified_intelligence.timeline import UnifiedTimelineEngine, CorrelationTimeline
from app.unified_intelligence.impact import UnifiedImpactEngine, UnifiedImpactAssessment
from app.unified_intelligence.risk import UnifiedRiskEngine, UnifiedRiskAssessment
from app.unified_intelligence.assurance_coordination import CrossDomainAssuranceCoordinator, UnifiedAssurancePosture
from app.unified_intelligence.trust import CrossDomainTrustEngine, UnifiedTrustAssessment
from app.unified_intelligence.recommendations import UnifiedRecommendationEngine, UnifiedRecommendation
from app.unified_intelligence.coordination import CoordinationPlannerEngine, CoordinationPlan, CoordinationStep
from app.unified_intelligence.governance import GovernancePolicyEvaluatorEngine, GovernanceEvaluationResult
from app.unified_intelligence.investigations import UnifiedInvestigationEngine, UnifiedInvestigation
from app.unified_intelligence.remediation import CrossDomainRemediationCoordinator, RemediationActionResult
from app.unified_intelligence.delegation import AutonomousDelegationEngine
from app.unified_intelligence.verification import DelegationVerificationEngine, UnifiedVerificationResult
from app.unified_intelligence.evidence import SHA256EvidenceLedgerEngine, UnifiedEvidenceRecord
from app.unified_intelligence.snapshots import UnifiedSnapshotGenerator
from app.unified_intelligence.learning import AdvisoryLearningEngine, AdvisoryModelInsight
from app.unified_intelligence.analytics import CrossDomainAnalyticsEngine, UnifiedAnalyticsSummary
from app.unified_intelligence.observability import UnifiedObservabilityEngine
from app.unified_intelligence.billing import IntelligenceBillingEngine, UnifiedBillingRecord
from app.unified_intelligence.idempotency import IdempotencyEngine
from app.unified_intelligence.repositories import UnifiedIntelligenceRepository
from app.unified_intelligence.manager import UnifiedIntelligenceManager

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
    "UnifiedIntelligenceManager"
]
