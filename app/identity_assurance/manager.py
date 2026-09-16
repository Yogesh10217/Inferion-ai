"""Master Orchestrator for Identity Assurance Platform."""

import logging
from typing import Optional

from app.identity_assurance.access_graph import AccessGraphManager
from app.identity_assurance.access_paths import AccessPathManager
from app.identity_assurance.access_patterns import AccessPatternManager
from app.identity_assurance.access_reviews import AccessReviewManager
from app.identity_assurance.analytics import IdentityAssuranceAnalyticsEngine
from app.identity_assurance.anomalies import IdentityAnomalyManager
from app.identity_assurance.assurance import IdentityAssuranceEngine, IdentityAssuranceScore
from app.identity_assurance.authentication_intelligence import AuthenticationIntelligenceManager
from app.identity_assurance.authorization_intelligence import AuthorizationIntelligenceManager
from app.identity_assurance.behavioral_analysis import IdentityBehaviorManager
from app.identity_assurance.billing import IdentityAssuranceBillingTracker
from app.identity_assurance.certifications import IdentityCertificationManager
from app.identity_assurance.correlation import IdentityCorrelationManager
from app.identity_assurance.delegation import IdentityDelegationManager
from app.identity_assurance.emergency_access import EmergencyAccessManager
from app.identity_assurance.entitlement_analysis import EntitlementAnalysisManager
from app.identity_assurance.evidence import IdentityEvidenceManager
from app.identity_assurance.governance import IdentityGovernanceEngine
from app.identity_assurance.identities import IdentityCategory, IdentityManager, IdentityReference, IdentityType
from app.identity_assurance.identity_profiles import IdentityProfileManager
from app.identity_assurance.impact import IdentityImpactManager
from app.identity_assurance.investigations import IdentityInvestigationManager
from app.identity_assurance.learning import IdentityLearningManager
from app.identity_assurance.least_privilege import LeastPrivilegeManager
from app.identity_assurance.observability import IdentityAssuranceMetricsCollector
from app.identity_assurance.privilege_creep import PrivilegeCreepManager
from app.identity_assurance.privileges import PrivilegeIntelligenceManager
from app.identity_assurance.remediation import IdentityRemediationManager
from app.identity_assurance.risk import IdentityRiskManager
from app.identity_assurance.segregation import SegregationManager
from app.identity_assurance.signals import IdentitySignalManager
from app.identity_assurance.snapshots import IdentityAssuranceSnapshotManager
from app.identity_assurance.toxic_combinations import ToxicCombinationManager
from app.identity_assurance.trust import IdentityTrustEngine
from app.identity_assurance.verification import IdentityVerificationManager

logger = logging.getLogger(__name__)


class IdentityAssuranceManager:
    """Master Orchestrator for Enterprise Identity Intelligence & Governance Assurance."""

    def __init__(self) -> None:
        self.identity_manager = IdentityManager()
        self.profile_manager = IdentityProfileManager()
        self.trust_engine = IdentityTrustEngine()
        self.auth_manager = AuthenticationIntelligenceManager()
        self.authorization_manager = AuthorizationIntelligenceManager()
        self.privilege_manager = PrivilegeIntelligenceManager()
        self.entitlement_manager = EntitlementAnalysisManager()
        self.least_privilege_manager = LeastPrivilegeManager()
        self.access_pattern_manager = AccessPatternManager()
        self.behavior_manager = IdentityBehaviorManager()
        self.anomaly_manager = IdentityAnomalyManager()
        self.privilege_creep_manager = PrivilegeCreepManager()
        self.toxic_combination_manager = ToxicCombinationManager()
        self.segregation_manager = SegregationManager()
        self.access_graph_manager = AccessGraphManager()
        self.access_path_manager = AccessPathManager()
        self.delegation_manager = IdentityDelegationManager()
        self.emergency_access_manager = EmergencyAccessManager()
        self.access_review_manager = AccessReviewManager()
        self.certification_manager = IdentityCertificationManager()
        self.governance_engine = IdentityGovernanceEngine()
        self.risk_manager = IdentityRiskManager()
        self.impact_manager = IdentityImpactManager()
        self.investigation_manager = IdentityInvestigationManager()
        self.remediation_manager = IdentityRemediationManager()
        self.verification_manager = IdentityVerificationManager()
        self.evidence_manager = IdentityEvidenceManager()
        self.signal_manager = IdentitySignalManager()
        self.correlation_manager = IdentityCorrelationManager()
        self.assurance_engine = IdentityAssuranceEngine()
        self.snapshot_manager = IdentityAssuranceSnapshotManager()
        self.learning_manager = IdentityLearningManager()
        self.analytics_engine = IdentityAssuranceAnalyticsEngine()
        self.metrics_collector = IdentityAssuranceMetricsCollector()
        self.billing_tracker = IdentityAssuranceBillingTracker()

    def register_identity(
        self,
        tenant_id: str,
        name: str,
        identity_type: IdentityType,
        category: IdentityCategory = IdentityCategory.EMPLOYEE,
        external_id: Optional[str] = None,
    ) -> IdentityReference:
        identity = self.identity_manager.register_identity(
            tenant_id=tenant_id,
            name=name,
            identity_type=identity_type,
            category=category,
            external_id=external_id,
        )
        self.profile_manager.assess_profile(tenant_id, identity)
        self.trust_engine.assess_trust(tenant_id, identity.identity_id)
        self.metrics_collector.record_trust_score(tenant_id, 0.90)
        self.billing_tracker.record_cost(tenant_id, identity.identity_id, "REGISTER_IDENTITY")
        return identity

    def get_identity(self, tenant_id: str, identity_id: str) -> IdentityReference:
        return self.identity_manager.get_identity(tenant_id, identity_id)

    def evaluate_identity_assurance(self, tenant_id: str, identity_id: str) -> IdentityAssuranceScore:
        identity = self.identity_manager.get_identity(tenant_id, identity_id)
        trust = self.trust_engine.assess_trust(tenant_id, identity_id)
        assurance = self.assurance_engine.assess_assurance(
            tenant_id=tenant_id,
            identity_id=identity_id,
            trust_score=trust.trust_score.overall_trust_score,
        )
        self.metrics_collector.record_assurance_score(tenant_id, assurance.overall_assurance_score)
        return assurance
