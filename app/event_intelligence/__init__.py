"""Enterprise AI Event Intelligence, Automation & Cross-Platform Coordination Platform Exports (Phase 5.34)."""

from app.event_intelligence.exceptions import (
    EventIntelligenceException,
    CrossTenantEventAccessException,
    EventNotFoundException,
    InvalidEventException,
    EventSchemaValidationException,
    DuplicateEventException,
    EventCorrelationException,
    EventAutomationBlockedException,
    EventPolicyViolationException,
    ImmutableEventRecordException,
    EventDelegationBlockedException,
    EventResolutionException,
    EventSourceNotRegisteredException,
    EventCausalityException,
    HighRiskAutomationRequiresApprovalException,
)

from app.event_intelligence.events import (
    EnterpriseEvent,
    EventType,
    EventCategory,
    EventSeverity,
    EventPriority,
    EventStatus,
    EventSource,
    EventMetadata,
    EventReference,
    EventManager,
)

from app.event_intelligence.sources import (
    EventSourceDefinition,
    EventSourceType,
    EventSourceStatus,
    EventSourceCapability,
    EventSourceRegistration,
    EventSourceManager,
)

from app.event_intelligence.normalization import (
    EventNormalizer,
    NormalizedEvent,
    EventNormalizationRule,
    EventSchema,
    EventSchemaRegistry,
)

from app.event_intelligence.classification import (
    EventClassification,
    EventClassificationDimension,
    EventClassifier,
    ClassificationConfidence,
)

from app.event_intelligence.deduplication import (
    EventFingerprint,
    EventDuplicate,
    EventDeduplicationResult,
    EventDeduplicator,
)

from app.event_intelligence.correlation import (
    EventCorrelation,
    CorrelationGroup,
    CorrelationType,
    CorrelationConfidence,
    CorrelationEvidence,
    EventCorrelationManager,
)

from app.event_intelligence.causality import (
    CausalRelationship,
    CausalNode,
    CausalEdge,
    CausalGraph,
    CausalConfidence,
    CausalityAnalysis,
    EventCausalityAnalyzer,
)

from app.event_intelligence.context import (
    EventContext,
    EventContextReference,
    EventContextSource,
    EventContextBuilder,
    EventContextManager,
)

from app.event_intelligence.impact import (
    EventImpactAssessment,
    EventImpactDimension,
    EventImpactSeverity,
    BusinessImpact,
    TechnicalImpact,
    FinancialImpact,
    ComplianceImpact,
    CustomerImpact,
    EventImpactAnalyzer,
)

from app.event_intelligence.patterns import (
    EventPattern,
    PatternType,
    PatternConfidence,
    PatternEvidence,
    EventPatternDetector,
)

from app.event_intelligence.automation import (
    AutomationTrigger,
    AutomationCondition,
    AutomationAction,
    AutomationPlan,
    AutomationStatus,
    AutomationEligibility,
    AutomationManager,
)


from app.event_intelligence.rules import (
    EventRule,
    EventRuleCondition,
    EventRuleAction,
    EventRuleStatus,
    EventRuleEvaluation,
    EventRuleManager,
)

from app.event_intelligence.prioritization import (
    EventPriorityScore,
    PriorityDimension,
    EventPrioritizationResult,
    EventPrioritizationEngine,
)

from app.event_intelligence.governance import (
    EventGovernanceEngine,
)

from app.event_intelligence.response import (
    EventResponsePlan,
    EventResponseAction,
    ResponseTarget,
    ResponseStatus,
    EventResponseManager,
)

from app.event_intelligence.delegation import (
    EventDelegationPlan,
    EventDelegationReference,
    EventDelegationManager,
)

from app.event_intelligence.resolution import (
    EventResolution,
    EventResolutionStatus,
    ResolutionEvidence,
    ResolutionVerification,
    EventResolutionManager,
)

from app.event_intelligence.investigations import (
    EventInvestigation,
    InvestigationStatus,
    InvestigationFinding,
    InvestigationEvidence,
    InvestigationConclusion,
    EventInvestigationManager,
)

from app.event_intelligence.learning import (
    EventLearningRecord,
    EventPatternLearning,
    EventRecommendation,
    EventLearningManager,
)

from app.event_intelligence.trust import (
    EventTrustScore,
    EventTrustDimension,
    EventTrustEngine,
)

from app.event_intelligence.analytics import (
    EventAnalyticsEngine,
)

from app.event_intelligence.observability import (
    EventMetricsCollector,
)

from app.event_intelligence.billing import (
    EventBillingTracker,
)

from app.event_intelligence.repositories import (
    EventRepository,
    EventCorrelationRepository,
    AutomationRepository,
    InvestigationRepository,
    ResolutionRepository,
)

from app.event_intelligence.manager import (
    EventIntelligenceManager,
)

__all__ = [
    "EventIntelligenceException",
    "CrossTenantEventAccessException",
    "EventNotFoundException",
    "InvalidEventException",
    "EventSchemaValidationException",
    "DuplicateEventException",
    "EventCorrelationException",
    "EventAutomationBlockedException",
    "EventPolicyViolationException",
    "ImmutableEventRecordException",
    "EventDelegationBlockedException",
    "EventResolutionException",
    "EventSourceNotRegisteredException",
    "EventCausalityException",
    "HighRiskAutomationRequiresApprovalException",
    "EnterpriseEvent",
    "EventType",
    "EventCategory",
    "EventSeverity",
    "EventPriority",
    "EventStatus",
    "EventSource",
    "EventMetadata",
    "EventReference",
    "EventManager",
    "EventSourceDefinition",
    "EventSourceType",
    "EventSourceStatus",
    "EventSourceCapability",
    "EventSourceRegistration",
    "EventSourceManager",
    "EventNormalizer",
    "NormalizedEvent",
    "EventNormalizationRule",
    "EventSchema",
    "EventSchemaRegistry",
    "EventClassification",
    "EventClassificationDimension",
    "EventClassifier",
    "ClassificationConfidence",
    "EventFingerprint",
    "EventDuplicate",
    "EventDeduplicationResult",
    "EventDeduplicator",
    "EventCorrelation",
    "CorrelationGroup",
    "CorrelationType",
    "CorrelationConfidence",
    "CorrelationEvidence",
    "EventCorrelationManager",
    "CausalRelationship",
    "CausalNode",
    "CausalEdge",
    "CausalGraph",
    "CausalConfidence",
    "CausalityAnalysis",
    "EventCausalityAnalyzer",
    "EventContext",
    "EventContextReference",
    "EventContextSource",
    "EventContextBuilder",
    "EventContextManager",
    "EventImpactAssessment",
    "EventImpactDimension",
    "EventImpactSeverity",
    "BusinessImpact",
    "TechnicalImpact",
    "FinancialImpact",
    "ComplianceImpact",
    "CustomerImpact",
    "EventImpactAnalyzer",
    "EventPattern",
    "PatternType",
    "PatternConfidence",
    "PatternEvidence",
    "EventPatternDetector",
    "AutomationTrigger",
    "AutomationCondition",

    "AutomationAction",
    "AutomationPlan",
    "AutomationStatus",
    "AutomationEligibility",
    "AutomationManager",
    "EventRule",
    "EventRuleCondition",
    "EventRuleAction",
    "EventRuleStatus",
    "EventRuleEvaluation",
    "EventRuleManager",
    "EventPriorityScore",
    "PriorityDimension",
    "EventPrioritizationResult",
    "EventPrioritizationEngine",
    "EventGovernanceEngine",
    "EventResponsePlan",
    "EventResponseAction",
    "ResponseTarget",
    "ResponseStatus",
    "EventResponseManager",
    "EventDelegationPlan",
    "EventDelegationReference",
    "EventDelegationManager",
    "EventResolution",
    "EventResolutionStatus",
    "ResolutionEvidence",
    "ResolutionVerification",
    "EventResolutionManager",
    "EventInvestigation",
    "InvestigationStatus",
    "InvestigationFinding",
    "InvestigationEvidence",
    "InvestigationConclusion",
    "EventInvestigationManager",
    "EventLearningRecord",
    "EventPatternLearning",
    "EventRecommendation",
    "EventLearningManager",
    "EventTrustScore",
    "EventTrustDimension",
    "EventTrustEngine",
    "EventAnalyticsEngine",
    "EventMetricsCollector",
    "EventBillingTracker",
    "EventRepository",
    "EventCorrelationRepository",
    "AutomationRepository",
    "InvestigationRepository",
    "ResolutionRepository",
    "EventIntelligenceManager",
]
