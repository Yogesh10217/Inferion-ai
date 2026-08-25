"""Enterprise AI Security Intelligence, Threat Detection, Vulnerability & Security Governance Platform Exports (Phase 5.32)."""

from app.security_intelligence.exceptions import (
    SecurityIntelligenceException,
    CrossTenantSecurityAccessException,
    ImmutableSecurityRecordException,
    SecurityThreatNotFoundException,
    SecurityIncidentNotFoundException,
    VulnerabilityNotFoundException,
    AttackPathNotFoundException,
    InvalidSecurityIncidentTransitionException,
    SecurityPolicyViolationException,
    SecurityRemediationBlockedException,
    SecurityEvidenceIntegrityException,
    SecuritySignalValidationException,
    HighRiskSecurityActionRequiresApprovalException,
)

from app.security_intelligence.assets import (
    SecurityAsset,
    SecurityAssetType,
    SecurityAssetCriticality,
    SecurityAssetExposure,
    SecurityAssetStatus,
    SecurityAssetManager,
)

from app.security_intelligence.attack_surface import (
    AttackSurface,
    AttackSurfaceExposure,
    AttackSurfaceEntry,
    AttackSurfaceRisk,
    AttackSurfaceManager,
)

from app.security_intelligence.signals import (
    SecuritySignal,
    SecuritySignalType,
    SecuritySignalSeverity,
    SecuritySignalSource,
    SecuritySignalManager,
)

from app.security_intelligence.threats import (
    SecurityThreat,
    ThreatType,
    ThreatSeverity,
    ThreatStatus,
    ThreatConfidence,
    ThreatEvidence,
    ThreatManager,
)

from app.security_intelligence.ai_threats import (
    AIThreat,
    AIThreatType,
    AIThreatSeverity,
    AIThreatDetection,
    AIThreatManager,
)

from app.security_intelligence.vulnerabilities import (
    SecurityVulnerability,
    VulnerabilitySeverity,
    VulnerabilityStatus,
    VulnerabilityEvidence,
    VulnerabilityManager,
)

from app.security_intelligence.correlation import (
    SecurityCorrelation,
    CorrelationType,
    CorrelationConfidence,
    AttackChain,
    SecurityCorrelationManager,
)

from app.security_intelligence.attack_paths import (
    AttackPath,
    AttackPathNode,
    AttackPathEdge,
    AttackPathRisk,
    AttackPathAnalyzer,
)

from app.security_intelligence.incidents import (
    SecurityIncident,
    SecurityIncidentStatus,
    SecurityIncidentSeverity,
    SecurityIncidentTimelineEvent,
    SecurityIncidentManager,
)

from app.security_intelligence.impact import (
    SecurityImpactAssessment,
    SecurityImpactDimension,
    SecurityImpactSeverity,
    SecurityImpactAnalyzer,
)

from app.security_intelligence.risk import (
    SecurityRiskProfile,
    SecurityRiskDimension,
    SecurityRiskAssessment,
    SecurityRiskManager,
)

from app.security_intelligence.governance import (
    SecurityGovernanceEngine,
)

from app.security_intelligence.remediation import (
    SecurityRemediationPlan,
    SecurityRemediationAction,
    SecurityRemediationStatus,
    SecurityRemediationPriority,
    SecurityRemediationManager,
)

from app.security_intelligence.posture import (
    SecurityPosture,
    SecurityPostureDimension,
    SecurityPostureBand,
    SecurityPostureManager,
)

from app.security_intelligence.trust import (
    SecurityTrustScore,
    SecurityTrustDimension,
    SecurityTrustEngine,
)

from app.security_intelligence.evidence import (
    SecurityEvidence,
    SecurityEvidenceBundle,
    SecurityEvidenceIntegrity,
    SecurityEvidenceManager,
)

from app.security_intelligence.investigations import (
    SecurityInvestigation,
    InvestigationStatus,
    InvestigationFinding,
    InvestigationManager,
)

from app.security_intelligence.learning import (
    SecurityLearningRecord,
    SecurityPattern,
    SecurityRecommendation,
    SecurityLearningManager,
)

from app.security_intelligence.analytics import (
    SecurityAnalyticsEngine,
)

from app.security_intelligence.observability import (
    SecurityMetricsCollector,
)

from app.security_intelligence.billing import (
    SecurityBillingTracker,
)

from app.security_intelligence.repositories import (
    SecurityRepository,
    SecurityAssetRepository,
    SecurityThreatRepository,
    SecurityIncidentRepository,
    SecurityVulnerabilityRepository,
    SecurityPostureRepository,
)

from app.security_intelligence.manager import (
    SecurityIntelligenceManager,
)

__all__ = [
    "SecurityIntelligenceException",
    "CrossTenantSecurityAccessException",
    "ImmutableSecurityRecordException",
    "SecurityThreatNotFoundException",
    "SecurityIncidentNotFoundException",
    "VulnerabilityNotFoundException",
    "AttackPathNotFoundException",
    "InvalidSecurityIncidentTransitionException",
    "SecurityPolicyViolationException",
    "SecurityRemediationBlockedException",
    "SecurityEvidenceIntegrityException",
    "SecuritySignalValidationException",
    "HighRiskSecurityActionRequiresApprovalException",
    "SecurityAsset",
    "SecurityAssetType",
    "SecurityAssetCriticality",
    "SecurityAssetExposure",
    "SecurityAssetStatus",
    "SecurityAssetManager",
    "AttackSurface",
    "AttackSurfaceExposure",
    "AttackSurfaceEntry",
    "AttackSurfaceRisk",
    "AttackSurfaceManager",
    "SecuritySignal",
    "SecuritySignalType",
    "SecuritySignalSeverity",
    "SecuritySignalSource",
    "SecuritySignalManager",
    "SecurityThreat",
    "ThreatType",
    "ThreatSeverity",
    "ThreatStatus",
    "ThreatConfidence",
    "ThreatEvidence",
    "ThreatManager",
    "AIThreat",
    "AIThreatType",
    "AIThreatSeverity",
    "AIThreatDetection",
    "AIThreatManager",
    "SecurityVulnerability",
    "VulnerabilitySeverity",
    "VulnerabilityStatus",
    "VulnerabilityEvidence",
    "VulnerabilityManager",
    "SecurityCorrelation",
    "CorrelationType",
    "CorrelationConfidence",
    "AttackChain",
    "SecurityCorrelationManager",
    "AttackPath",
    "AttackPathNode",
    "AttackPathEdge",
    "AttackPathRisk",
    "AttackPathAnalyzer",
    "SecurityIncident",
    "SecurityIncidentStatus",
    "SecurityIncidentSeverity",
    "SecurityIncidentTimelineEvent",
    "SecurityIncidentManager",
    "SecurityImpactAssessment",
    "SecurityImpactDimension",
    "SecurityImpactSeverity",
    "SecurityImpactAnalyzer",
    "SecurityRiskProfile",
    "SecurityRiskDimension",
    "SecurityRiskAssessment",
    "SecurityRiskManager",
    "SecurityGovernanceEngine",
    "SecurityRemediationPlan",
    "SecurityRemediationAction",
    "SecurityRemediationStatus",
    "SecurityRemediationPriority",
    "SecurityRemediationManager",
    "SecurityPosture",
    "SecurityPostureDimension",
    "SecurityPostureBand",
    "SecurityPostureManager",
    "SecurityTrustScore",
    "SecurityTrustDimension",
    "SecurityTrustEngine",
    "SecurityEvidence",
    "SecurityEvidenceBundle",
    "SecurityEvidenceIntegrity",
    "SecurityEvidenceManager",
    "SecurityInvestigation",
    "InvestigationStatus",
    "InvestigationFinding",
    "InvestigationManager",
    "SecurityLearningRecord",
    "SecurityPattern",
    "SecurityRecommendation",
    "SecurityLearningManager",
    "SecurityAnalyticsEngine",
    "SecurityMetricsCollector",
    "SecurityBillingTracker",
    "SecurityRepository",
    "SecurityAssetRepository",
    "SecurityThreatRepository",
    "SecurityIncidentRepository",
    "SecurityVulnerabilityRepository",
    "SecurityPostureRepository",
    "SecurityIntelligenceManager",
]
