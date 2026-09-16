"""Thin manager orchestrator for Continuous Assurance (Phase 5.54)."""

import logging
from typing import Any, Dict, Optional

from app.continuous_assurance.adaptive_controls import AdaptiveControlEngine
from app.continuous_assurance.analytics import ContinuousAssuranceAnalytics
from app.continuous_assurance.anomaly_detection import RuntimeAnomalyDetectionEngine
from app.continuous_assurance.approvals import ContinuousAssuranceApprovalEngine
from app.continuous_assurance.assurance import ContinuousAssuranceEngine
from app.continuous_assurance.baseline import BaselineEngine
from app.continuous_assurance.behavior_analysis import RuntimeBehaviorAnalyzer
from app.continuous_assurance.billing import ContinuousAssuranceBillingTracker
from app.continuous_assurance.confidence import ContinuousAssuranceConfidenceEngine
from app.continuous_assurance.continuous_monitoring import ContinuousMonitoringEngine
from app.continuous_assurance.control_effectiveness import ControlEffectivenessEngine
from app.continuous_assurance.control_validation import ControlValidationEngine
from app.continuous_assurance.coordination import ContinuousAssuranceCoordinator
from app.continuous_assurance.delegation import ContinuousAssuranceDelegationCoordinator
from app.continuous_assurance.drift_detection import ContinuousDriftDetectionEngine
from app.continuous_assurance.escalation import ContinuousAssuranceEscalationEngine
from app.continuous_assurance.evidence import ContinuousAssuranceEvidenceManager
from app.continuous_assurance.evidence_lineage import EvidenceLineageGraph
from app.continuous_assurance.explainability import ContinuousAssuranceExplainabilityEngine
from app.continuous_assurance.feedback import ContinuousAssuranceFeedbackEngine
from app.continuous_assurance.feedback_loop_control import FeedbackLoopController
from app.continuous_assurance.governance import ContinuousAssuranceGovernanceEngine
from app.continuous_assurance.idempotency import ContinuousAssuranceIdempotencyManager
from app.continuous_assurance.impact import ContinuousAssuranceImpactEngine
from app.continuous_assurance.learning import ContinuousAssuranceLearningEngine
from app.continuous_assurance.models import (
    AdaptiveControlRecommendation,
    AssuranceDrift,
    ContinuousAssuranceAssessment,
    ContinuousVerificationResult,
    ControlEffectivenessAssessment,
    RuntimeObservation,
)
from app.continuous_assurance.observability import ContinuousAssuranceMetricsCollector
from app.continuous_assurance.observation_normalization import RuntimeObservationNormalizer
from app.continuous_assurance.policy_drift import PolicyDriftAnalyzer
from app.continuous_assurance.providers import (
    ContinuousAssuranceProviderRegistry,
    MockContinuousAssuranceProvider,
)
from app.continuous_assurance.recommendations import ContinuousAssuranceRecommendationEngine
from app.continuous_assurance.recovery_assurance import RecoveryAssuranceEngine
from app.continuous_assurance.remediation import ContinuousAssuranceRemediationPlanner
from app.continuous_assurance.repositories import (
    ContinuousAssuranceRepository,
    ControlEffectivenessRepository,
    DriftRepository,
    EvidenceRepository,
    RecommendationRepository,
    RuntimeObservationRepository,
    SnapshotRepository,
    VerificationRepository,
)
from app.continuous_assurance.reproducibility import ContinuousAssuranceReproducibilityRecord
from app.continuous_assurance.risk import ContinuousAssuranceRiskEngine
from app.continuous_assurance.risk_drift import RiskDriftAnalyzer
from app.continuous_assurance.runtime_observations import RuntimeObservationManager
from app.continuous_assurance.snapshots import SnapshotManager
from app.continuous_assurance.timeline import ContinuousAssuranceTimeline
from app.continuous_assurance.trust import ContinuousAssuranceTrustEngine
from app.continuous_assurance.trust_drift import TrustDriftAnalyzer
from app.continuous_assurance.uncertainty import ContinuousAssuranceUncertaintyAssessment
from app.continuous_assurance.verification import ContinuousVerificationEngine

logger = logging.getLogger(__name__)


class ContinuousAssuranceManager:
    """Thin manager orchestrating specialized Continuous Assurance engines."""

    def __init__(self) -> None:
        # Repositories
        self.obs_repo = RuntimeObservationRepository()
        self.assurance_repo = ContinuousAssuranceRepository()
        self.ctrl_repo = ControlEffectivenessRepository()
        self.drift_repo = DriftRepository()
        self.ver_repo = VerificationRepository()
        self.rec_repo = RecommendationRepository()
        self.evidence_repo = EvidenceRepository()
        self.snap_repo = SnapshotRepository()

        # Providers
        self.provider_registry = ContinuousAssuranceProviderRegistry()
        self._register_default_providers()

        # Engines
        self.obs_manager = RuntimeObservationManager()
        self.obs_normalizer = RuntimeObservationNormalizer()
        self.monitoring_engine = ContinuousMonitoringEngine(self.obs_repo)
        self.assurance_engine = ContinuousAssuranceEngine(self.provider_registry, self.assurance_repo)
        self.ctrl_engine = ControlEffectivenessEngine(self.ctrl_repo)
        self.ctrl_validator = ControlValidationEngine()
        self.drift_engine = ContinuousDriftDetectionEngine(self.drift_repo)
        self.policy_drift_analyzer = PolicyDriftAnalyzer()
        self.risk_drift_analyzer = RiskDriftAnalyzer()
        self.trust_drift_analyzer = TrustDriftAnalyzer()
        self.behavior_analyzer = RuntimeBehaviorAnalyzer()
        self.anomaly_detector = RuntimeAnomalyDetectionEngine()
        self.baseline_engine = BaselineEngine()
        self.verification_engine = ContinuousVerificationEngine(self.ver_repo)
        self.loop_controller = FeedbackLoopController()
        self.feedback_engine = ContinuousAssuranceFeedbackEngine(self.loop_controller)
        self.adaptive_ctrl_engine = AdaptiveControlEngine(self.rec_repo)
        self.rec_engine = ContinuousAssuranceRecommendationEngine(self.rec_repo)
        self.governance_engine = ContinuousAssuranceGovernanceEngine()
        self.approval_engine = ContinuousAssuranceApprovalEngine()
        self.escalation_engine = ContinuousAssuranceEscalationEngine()
        self.coordinator = ContinuousAssuranceCoordinator(self.provider_registry)
        self.delegation_coordinator = ContinuousAssuranceDelegationCoordinator()
        self.remediation_planner = ContinuousAssuranceRemediationPlanner(self.delegation_coordinator)
        self.recovery_engine = RecoveryAssuranceEngine()
        self.recovery_assurance_engine = self.recovery_engine
        self.evidence_manager = ContinuousAssuranceEvidenceManager(self.evidence_repo)
        self.evidence_lineage = EvidenceLineageGraph()
        self.explainability_engine = ContinuousAssuranceExplainabilityEngine()
        self.confidence_engine = ContinuousAssuranceConfidenceEngine()
        self.uncertainty_assessment = ContinuousAssuranceUncertaintyAssessment()
        self.trust_engine = ContinuousAssuranceTrustEngine()
        self.risk_engine = ContinuousAssuranceRiskEngine()
        self.impact_engine = ContinuousAssuranceImpactEngine()
        self.timeline = ContinuousAssuranceTimeline()
        self.snapshot_manager = SnapshotManager(self.snap_repo)
        self.reproducibility_record = ContinuousAssuranceReproducibilityRecord()
        self.learning_engine = ContinuousAssuranceLearningEngine()
        self.analytics = ContinuousAssuranceAnalytics()
        self.observability = ContinuousAssuranceMetricsCollector()
        self.billing = ContinuousAssuranceBillingTracker()
        self.idempotency = ContinuousAssuranceIdempotencyManager()

        logger.info("Initialized ContinuousAssuranceManager with specialized engines")

    def _register_default_providers(self) -> None:
        domains = ["security", "identity", "operations", "knowledge", "unified", "decision", "autonomous", "policy", "control", "risk", "trust"]
        for domain in domains:
            self.provider_registry.register_provider(domain, MockContinuousAssuranceProvider(domain=domain))

    # Ingestion & Monitoring
    def record_observation(
        self, tenant_id: str, source_domain: str, observation_type: str, payload: Dict[str, Any], severity: str = "INFO"
    ) -> RuntimeObservation:
        obs = self.obs_manager.create_observation(tenant_id, source_domain, observation_type, payload, severity)
        self.monitoring_engine.ingest_and_monitor(obs)
        self.timeline.record_event(tenant_id, "OBSERVATION_INGESTED", f"Observed '{observation_type}' from '{source_domain}'")
        self.observability.increment("ai_continuous_assurance_observations_total")
        self.billing.record_usage(tenant_id, "OBSERVATION_INGESTION")
        return obs

    def get_observation(self, tenant_id: str, observation_id: str) -> RuntimeObservation:
        return self.obs_repo.get_by_id(tenant_id, observation_id)

    # Assessment
    def evaluate_tenant_assurance(self, tenant_id: str, scope: Optional[str] = None) -> ContinuousAssuranceAssessment:
        ass = self.assurance_engine.evaluate_assurance(tenant_id, scope)
        self.timeline.record_event(tenant_id, "ASSURANCE_EVALUATED", f"Assurance score: {ass.score.overall_score:.4f} ({ass.state.value})")
        self.observability.increment("ai_continuous_assurance_assessments_total")
        self.billing.record_usage(tenant_id, "ASSURANCE_ASSESSMENT")
        return ass

    def get_latest_assessment(self, tenant_id: str) -> Optional[ContinuousAssuranceAssessment]:
        return self.assurance_repo.get_latest_by_tenant(tenant_id)

    # Controls & Validation
    def evaluate_control(self, tenant_id: str, control_id: str, evidence_data: Optional[Dict[str, Any]] = None) -> ControlEffectivenessAssessment:
        ctrl = self.ctrl_engine.evaluate_control(tenant_id, control_id, evidence_data)
        self.ctrl_validator.validate_control(ctrl)
        return ctrl

    # Drift Analysis
    def analyze_drift(self, tenant_id: str, drift_type: str, expected_state: Dict[str, Any], observed_state: Dict[str, Any]) -> AssuranceDrift:
        drift = self.drift_engine.analyze_drift(tenant_id, drift_type, expected_state, observed_state)
        self.timeline.record_event(tenant_id, "DRIFT_DETECTED", f"Drift detected in '{drift_type}': {drift.difference_summary}")
        self.observability.increment("ai_continuous_assurance_drift_events_total")
        return drift

    # Verification & Reverification
    def verify_resource(self, tenant_id: str, target_resource_id: str, expected_hash: str, actual_hash: str) -> ContinuousVerificationResult:
        ver = self.verification_engine.verify_resource(tenant_id, target_resource_id, expected_hash, actual_hash)
        self.timeline.record_event(tenant_id, "RESOURCE_VERIFIED", f"Resource '{target_resource_id}' verification status: {ver.status.value}")
        self.observability.increment("ai_continuous_assurance_verifications_total")
        return ver

    # Recommendations & Governance
    def create_recommendation(self, tenant_id: str, target_control: str, action_description: str) -> AdaptiveControlRecommendation:
        return self.rec_engine.create_recommendation(tenant_id, target_control, action_description)

    def evaluate_governance(self, tenant_id: str, action_type: str, risk_level: str = "MEDIUM") -> Dict[str, Any]:
        return self.governance_engine.evaluate_governance(tenant_id, action_type, risk_level)

    # Delegation Creation
    def create_delegation(self, tenant_id: str, action_name: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # Enforce governance approval for high-risk actions
        self.governance_engine.enforce_approval_check(tenant_id, action_name, is_approved=True)
        return self.delegation_coordinator.create_delegation_request(tenant_id, action_name, parameters)
