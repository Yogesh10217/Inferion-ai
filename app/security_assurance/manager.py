"""Master Orchestrator for Enterprise AI Security Intelligence & Continuous Security Assurance Platform."""

import logging
from typing import Dict, Any, List, Optional

from app.security_assurance.assets import SecurityAsset, SecurityAssetType, SecurityCriticality
from app.security_assurance.asset_inventory import SecurityAssetInventory
from app.security_assurance.posture import SecurityPostureEngine, SecurityPostureAssessment
from app.security_assurance.threats import SecurityThreatStore, SecurityThreat, ThreatType, ThreatSeverity
from app.security_assurance.threat_indicators import ThreatIndicatorManager, ThreatIndicator
from app.security_assurance.threat_detection import SecurityThreatDetector
from app.security_assurance.threat_correlation import ThreatCorrelationEngine, CorrelatedThreatCluster
from app.security_assurance.vulnerabilities import SecurityVulnerabilityStore, SecurityVulnerability, VulnerabilitySeverity
from app.security_assurance.vulnerability_risk import VulnerabilityRiskAssessor, VulnerabilityRiskAssessment
from app.security_assurance.attack_surface import AttackSurfaceAnalyzer, AttackSurfaceProfile
from app.security_assurance.attack_graph import AnalyticalAttackGraph
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
from app.security_assurance.governance import SecurityGovernanceEngine, SecurityGovernanceResult
from app.security_assurance.recommendations import SecurityRecommendationManager, SecurityRecommendation
from app.security_assurance.remediation import SecurityRemediationPlanner, SecurityRemediationPlan
from app.security_assurance.delegation import SecurityDelegationManager, SecurityDelegationPlan
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

logger = logging.getLogger(__name__)


class SecurityAssuranceManager:
    """Master Orchestrator for Phase 5.50 — Enterprise AI Security Intelligence & Continuous Security Assurance Platform."""

    def __init__(self) -> None:
        self.asset_inventory = SecurityAssetInventory()
        self.posture_engine = SecurityPostureEngine(self.asset_inventory)
        self.threat_store = SecurityThreatStore()
        self.indicator_manager = ThreatIndicatorManager()
        self.threat_detector = SecurityThreatDetector(self.threat_store, self.indicator_manager)
        self.threat_correlation_engine = ThreatCorrelationEngine(self.threat_store)
        self.vuln_store = SecurityVulnerabilityStore()
        self.vuln_risk_assessor = VulnerabilityRiskAssessor(self.vuln_store, self.asset_inventory)
        self.attack_surface_analyzer = AttackSurfaceAnalyzer(self.asset_inventory)
        self.attack_graph = AnalyticalAttackGraph()
        self.attack_path_finder = AttackPathFinder(self.attack_graph)
        self.misconfig_detector = MisconfigurationDetector(self.asset_inventory)
        self.exposure_analyzer = ExposureAnalyzer(self.asset_inventory)
        self.secrets_engine = SecretsIntelligenceEngine()
        self.appsec_engine = AppSecEngine()
        self.api_security_engine = APISecurityEngine()
        self.model_security_engine = ModelSecurityEngine()
        self.agent_security_engine = AgentSecurityEngine()
        self.data_security_engine = DataSecurityEngine()
        self.identity_security_engine = IdentitySecurityEngine()
        self.cloud_security_engine = CloudSecurityEngine()
        self.container_security_engine = ContainerSecurityEngine()
        self.network_security_engine = NetworkSecurityEngine()
        self.incident_manager = SecurityIncidentManager()
        self.investigation_manager = SecurityInvestigationManager()
        self.root_cause_engine = SecurityRootCauseEngine()
        self.impact_engine = SecurityImpactEngine()
        self.risk_engine = SecurityRiskEngine()
        self.governance_engine = SecurityGovernanceEngine()
        self.recommendation_manager = SecurityRecommendationManager()
        self.remediation_planner = SecurityRemediationPlanner()
        self.delegation_manager = SecurityDelegationManager()
        self.verification_engine = SecurityVerificationEngine()
        self.evidence_manager = SecurityEvidenceManager()
        self.signal_engine = SecuritySignalEngine()
        self.cross_domain_correlation_engine = CrossDomainSecurityCorrelationEngine()
        self.assurance_engine = SecurityAssuranceEngine()
        self.trust_engine = SecurityTrustEngine()
        self.snapshot_manager = SecurityAssuranceSnapshotManager()
        self.learning_manager = SecurityLearningManager()
        self.analytics_engine = SecurityAnalyticsEngine()
        self.observability_engine = SecurityObservabilityEngine()
        self.billing_tracker = SecurityBillingTracker()

    def register_asset(
        self,
        tenant_id: str,
        name: str,
        asset_type: SecurityAssetType,
        criticality: SecurityCriticality = SecurityCriticality.MEDIUM,
        location: str = "internal",
        owner: str = "security-team",
        metadata: Optional[Dict] = None,
    ) -> SecurityAsset:
        asset = self.asset_inventory.register_asset(
            tenant_id=tenant_id,
            name=name,
            asset_type=asset_type,
            criticality=criticality,
            location=location,
            owner=owner,
            metadata=metadata,
        )
        self.observability_engine.record_asset_count(tenant_id, len(self.asset_inventory.list_assets(tenant_id)))
        self.billing_tracker.record_cost(tenant_id, asset.asset_id, "REGISTER_SECURITY_ASSET")
        return asset

    def evaluate_posture(self, tenant_id: str) -> SecurityPostureAssessment:
        open_vulns = len(self.vuln_store.list_vulnerabilities(tenant_id, status="OPEN"))
        misconfigs = len(self.misconfig_detector.scan_misconfigurations(tenant_id))
        active_threats = len(self.threat_store.list_threats(tenant_id, status="ACTIVE"))

        assessment = self.posture_engine.evaluate_posture(
            tenant_id=tenant_id,
            open_vulnerabilities=open_vulns,
            misconfigurations=misconfigs,
            active_threats=active_threats,
        )
        self.observability_engine.record_posture_score(tenant_id, assessment.score)
        return assessment

    def evaluate_assurance(self, tenant_id: str) -> SecurityAssuranceScore:
        posture = self.evaluate_posture(tenant_id)
        active_threats = len(self.threat_store.list_threats(tenant_id, status="ACTIVE"))
        score = self.assurance_engine.compute_assurance_score(
            tenant_id=tenant_id,
            posture_score=posture.score,
            unmitigated_threats=active_threats,
        )
        return score
