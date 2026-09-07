"""Phase 5.50 — Enterprise AI Security Intelligence & Continuous Security Assurance Platform."""

from app.security_assurance.exceptions import (
    SecurityAssuranceException,
    CrossTenantSecurityAssuranceException,
    SecurityAssetNotFoundException,
    SecurityThreatNotFoundException,
    SecurityVulnerabilityNotFoundException,
    SecurityIncidentNotFoundException,
    SecurityInvestigationNotFoundException,
    HighRiskSecurityActionRequiresApprovalException,
    ImmutableSecurityRecordException,
    SecretsExposureException,
    InvalidSecurityPayloadException,
)
from app.security_assurance.assets import SecurityAsset, SecurityAssetType, SecurityCriticality
from app.security_assurance.asset_inventory import SecurityAssetInventory
from app.security_assurance.posture import SecurityPostureEngine, SecurityPostureAssessment, SecurityPostureGrade
from app.security_assurance.threats import SecurityThreatStore, SecurityThreat, ThreatType, ThreatSeverity
from app.security_assurance.threat_indicators import ThreatIndicatorManager, ThreatIndicator
from app.security_assurance.threat_detection import SecurityThreatDetector
from app.security_assurance.threat_correlation import ThreatCorrelationEngine, CorrelatedThreatCluster
from app.security_assurance.vulnerabilities import SecurityVulnerabilityStore, SecurityVulnerability, VulnerabilitySeverity
from app.security_assurance.vulnerability_risk import VulnerabilityRiskAssessor, VulnerabilityRiskAssessment
from app.security_assurance.attack_surface import AttackSurfaceAnalyzer, AttackSurfaceProfile
from app.security_assurance.attack_graph import AnalyticalAttackGraph, AttackNode, AttackEdge
from app.security_assurance.attack_paths import AttackPathFinder, DefensiveAttackPath
from app.security_assurance.misconfigurations import MisconfigurationDetector, SecurityMisconfiguration
from app.security_assurance.exposure import ExposureAnalyzer, ExposureRiskAssessment
from app.security_assurance.secrets_intelligence import SecretsIntelligenceEngine, SecretReference
from app.security_assurance.application_security import AppSecEngine, AppSecScanResult
from app.security_assurance.api_security import APISecurityEngine, APISecurityAssessment
from app.security_assurance.model_security import ModelSecurityEngine, ModelVulnerabilityAssessment
from app.security_assurance.agent_security import AgentSecurityEngine, AgentRiskAssessment
from app.security_assurance.data_security import DataSecurityEngine, DataExfiltrationRiskAssessment
from app.security_assurance.identity_security import IdentitySecurityEngine, IdentityRiskAssessment
from app.security_assurance.cloud_security import CloudSecurityEngine, CloudPostureAssessment
from app.security_assurance.container_security import ContainerSecurityEngine, ContainerScanResult
from app.security_assurance.network_security import NetworkSecurityEngine, NetworkPostureAssessment
from app.security_assurance.incidents import SecurityIncidentManager, SecurityIncident, SecurityIncidentSeverity, SecurityIncidentState
from app.security_assurance.investigations import SecurityInvestigationManager, SecurityInvestigation
from app.security_assurance.root_cause import SecurityRootCauseEngine, SecurityRootCauseAssessment
from app.security_assurance.impact import SecurityImpactEngine, SecurityImpactScore
from app.security_assurance.risk import SecurityRiskEngine, SecurityRiskAssessment
from app.security_assurance.governance import SecurityGovernanceEngine, SecurityGovernanceResult, SecurityGovernanceRequest
from app.security_assurance.recommendations import SecurityRecommendationManager, SecurityRecommendation
from app.security_assurance.remediation import SecurityRemediationPlanner, SecurityRemediationPlan
from app.security_assurance.delegation import SecurityDelegationManager, SecurityDelegationPlan, SecurityDelegationAction
from app.security_assurance.verification import SecurityVerificationEngine, SecurityVerificationResult
from app.security_assurance.evidence import SecurityEvidenceManager, SecurityEvidence
from app.security_assurance.signals import SecuritySignalEngine, SecuritySignal, SecuritySignalType
from app.security_assurance.correlation import CrossDomainSecurityCorrelationEngine, CrossDomainCorrelationResult
from app.security_assurance.assurance import SecurityAssuranceEngine, SecurityAssuranceScore
from app.security_assurance.trust import SecurityTrustEngine, SecurityTrustScore
from app.security_assurance.snapshots import SecurityAssuranceSnapshotManager, SecurityAssuranceSnapshot
from app.security_assurance.learning import SecurityLearningManager, SecurityLearningRecord
from app.security_assurance.analytics import SecurityAnalyticsEngine, SecurityAnalyticsReport
from app.security_assurance.observability import SecurityObservabilityEngine
from app.security_assurance.billing import SecurityBillingTracker
from app.security_assurance.manager import SecurityAssuranceManager

__all__ = [
    "SecurityAssuranceException",
    "CrossTenantSecurityAssuranceException",
    "SecurityAssetNotFoundException",
    "SecurityThreatNotFoundException",
    "SecurityVulnerabilityNotFoundException",
    "SecurityIncidentNotFoundException",
    "SecurityInvestigationNotFoundException",
    "HighRiskSecurityActionRequiresApprovalException",
    "ImmutableSecurityRecordException",
    "SecretsExposureException",
    "InvalidSecurityPayloadException",
    "SecurityAsset",
    "SecurityAssetType",
    "SecurityCriticality",
    "SecurityAssetInventory",
    "SecurityPostureEngine",
    "SecurityPostureAssessment",
    "SecurityPostureGrade",
    "SecurityThreatStore",
    "SecurityThreat",
    "ThreatType",
    "ThreatSeverity",
    "ThreatIndicatorManager",
    "ThreatIndicator",
    "SecurityThreatDetector",
    "ThreatCorrelationEngine",
    "CorrelatedThreatCluster",
    "SecurityVulnerabilityStore",
    "SecurityVulnerability",
    "VulnerabilitySeverity",
    "VulnerabilityRiskAssessor",
    "VulnerabilityRiskAssessment",
    "AttackSurfaceAnalyzer",
    "AttackSurfaceProfile",
    "AnalyticalAttackGraph",
    "AttackNode",
    "AttackEdge",
    "AttackPathFinder",
    "DefensiveAttackPath",
    "MisconfigurationDetector",
    "SecurityMisconfiguration",
    "ExposureAnalyzer",
    "ExposureRiskAssessment",
    "SecretsIntelligenceEngine",
    "SecretReference",
    "AppSecEngine",
    "AppSecScanResult",
    "APISecurityEngine",
    "APISecurityAssessment",
    "ModelSecurityEngine",
    "ModelVulnerabilityAssessment",
    "AgentSecurityEngine",
    "AgentRiskAssessment",
    "DataSecurityEngine",
    "DataExfiltrationRiskAssessment",
    "IdentitySecurityEngine",
    "IdentityRiskAssessment",
    "CloudSecurityEngine",
    "CloudPostureAssessment",
    "ContainerSecurityEngine",
    "ContainerScanResult",
    "NetworkSecurityEngine",
    "NetworkPostureAssessment",
    "SecurityIncidentManager",
    "SecurityIncident",
    "SecurityIncidentSeverity",
    "SecurityIncidentState",
    "SecurityInvestigationManager",
    "SecurityInvestigation",
    "SecurityRootCauseEngine",
    "SecurityRootCauseAssessment",
    "SecurityImpactEngine",
    "SecurityImpactScore",
    "SecurityRiskEngine",
    "SecurityRiskAssessment",
    "SecurityGovernanceEngine",
    "SecurityGovernanceResult",
    "SecurityGovernanceRequest",
    "SecurityRecommendationManager",
    "SecurityRecommendation",
    "SecurityRemediationPlanner",
    "SecurityRemediationPlan",
    "SecurityDelegationManager",
    "SecurityDelegationPlan",
    "SecurityDelegationAction",
    "SecurityVerificationEngine",
    "SecurityVerificationResult",
    "SecurityEvidenceManager",
    "SecurityEvidence",
    "SecuritySignalEngine",
    "SecuritySignal",
    "SecuritySignalType",
    "CrossDomainSecurityCorrelationEngine",
    "CrossDomainCorrelationResult",
    "SecurityAssuranceEngine",
    "SecurityAssuranceScore",
    "SecurityTrustEngine",
    "SecurityTrustScore",
    "SecurityAssuranceSnapshotManager",
    "SecurityAssuranceSnapshot",
    "SecurityLearningManager",
    "SecurityLearningRecord",
    "SecurityAnalyticsEngine",
    "SecurityAnalyticsReport",
    "SecurityObservabilityEngine",
    "SecurityBillingTracker",
    "SecurityAssuranceManager",
]
