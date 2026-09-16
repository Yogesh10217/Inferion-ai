"""Enterprise AI Security Intelligence, Threat Detection, Vulnerability & Security Governance Platform Exports (Phase 5.32)."""

from app.security_intelligence.ai_threats import (
    AIThreat,
    AIThreatDetection,
    AIThreatManager,
    AIThreatSeverity,
    AIThreatType,
)
from app.security_intelligence.analytics import (
    SecurityAnalyticsEngine,
)
from app.security_intelligence.assets import (
    SecurityAsset,
    SecurityAssetCriticality,
    SecurityAssetExposure,
    SecurityAssetManager,
    SecurityAssetStatus,
    SecurityAssetType,
)
from app.security_intelligence.attack_paths import (
    AttackPath,
    AttackPathAnalyzer,
    AttackPathEdge,
    AttackPathNode,
    AttackPathRisk,
)
from app.security_intelligence.attack_surface import (
    AttackSurface,
    AttackSurfaceEntry,
    AttackSurfaceExposure,
    AttackSurfaceManager,
    AttackSurfaceRisk,
)
from app.security_intelligence.billing import (
    SecurityBillingTracker,
)
from app.security_intelligence.correlation import (
    AttackChain,
    CorrelationConfidence,
    CorrelationType,
    SecurityCorrelation,
    SecurityCorrelationManager,
)
from app.security_intelligence.evidence import (
    SecurityEvidence,
    SecurityEvidenceBundle,
    SecurityEvidenceIntegrity,
    SecurityEvidenceManager,
)
from app.security_intelligence.exceptions import (
    AttackPathNotFoundException,
    CrossTenantSecurityAccessException,
    HighRiskSecurityActionRequiresApprovalException,
    ImmutableSecurityRecordException,
    InvalidSecurityIncidentTransitionException,
    SecurityEvidenceIntegrityException,
    SecurityIncidentNotFoundException,
    SecurityIntelligenceException,
    SecurityPolicyViolationException,
    SecurityRemediationBlockedException,
    SecuritySignalValidationException,
    SecurityThreatNotFoundException,
    VulnerabilityNotFoundException,
)
from app.security_intelligence.governance import (
    SecurityGovernanceEngine,
)
from app.security_intelligence.impact import (
    SecurityImpactAnalyzer,
    SecurityImpactAssessment,
    SecurityImpactDimension,
    SecurityImpactSeverity,
)
from app.security_intelligence.incidents import (
    SecurityIncident,
    SecurityIncidentManager,
    SecurityIncidentSeverity,
    SecurityIncidentStatus,
    SecurityIncidentTimelineEvent,
)
from app.security_intelligence.investigations import (
    InvestigationFinding,
    InvestigationManager,
    InvestigationStatus,
    SecurityInvestigation,
)
from app.security_intelligence.learning import (
    SecurityLearningManager,
    SecurityLearningRecord,
    SecurityPattern,
    SecurityRecommendation,
)
from app.security_intelligence.manager import (
    SecurityIntelligenceManager,
)
from app.security_intelligence.observability import (
    SecurityMetricsCollector,
)
from app.security_intelligence.posture import (
    SecurityPosture,
    SecurityPostureBand,
    SecurityPostureDimension,
    SecurityPostureManager,
)
from app.security_intelligence.remediation import (
    SecurityRemediationAction,
    SecurityRemediationManager,
    SecurityRemediationPlan,
    SecurityRemediationPriority,
    SecurityRemediationStatus,
)
from app.security_intelligence.repositories import (
    SecurityAssetRepository,
    SecurityIncidentRepository,
    SecurityPostureRepository,
    SecurityRepository,
    SecurityThreatRepository,
    SecurityVulnerabilityRepository,
)
from app.security_intelligence.risk import (
    SecurityRiskAssessment,
    SecurityRiskDimension,
    SecurityRiskManager,
    SecurityRiskProfile,
)
from app.security_intelligence.signals import (
    SecuritySignal,
    SecuritySignalManager,
    SecuritySignalSeverity,
    SecuritySignalSource,
    SecuritySignalType,
)
from app.security_intelligence.threats import (
    SecurityThreat,
    ThreatConfidence,
    ThreatEvidence,
    ThreatManager,
    ThreatSeverity,
    ThreatStatus,
    ThreatType,
)
from app.security_intelligence.trust import (
    SecurityTrustDimension,
    SecurityTrustEngine,
    SecurityTrustScore,
)
from app.security_intelligence.vulnerabilities import (
    SecurityVulnerability,
    VulnerabilityEvidence,
    VulnerabilityManager,
    VulnerabilitySeverity,
    VulnerabilityStatus,
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
