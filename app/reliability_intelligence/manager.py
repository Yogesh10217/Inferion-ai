"""Thin manager orchestrator for Reliability Intelligence (Phase 5.55)."""

import logging
from typing import Any, Dict, List, Optional

from app.reliability_intelligence.analytics import ReliabilityAnalytics
from app.reliability_intelligence.anomaly_intelligence import ReliabilityAnomalyEngine
from app.reliability_intelligence.approvals import ReliabilityApprovalEngine
from app.reliability_intelligence.assurance import ReliabilityAssuranceEngine
from app.reliability_intelligence.billing import ReliabilityBillingTracker
from app.reliability_intelligence.blast_radius import BlastRadiusAnalyzer
from app.reliability_intelligence.capacity_intelligence import CapacityIntelligenceEngine
from app.reliability_intelligence.chaos_governance import ChaosExperimentGovernanceEngine
from app.reliability_intelligence.confidence import ReliabilityConfidenceEngine
from app.reliability_intelligence.degradation import SafeDegradationEngine
from app.reliability_intelligence.delegation import ReliabilityDelegationCoordinator
from app.reliability_intelligence.dependency_intelligence import ReliabilityDependencyGraph
from app.reliability_intelligence.error_budget import ErrorBudgetEngine
from app.reliability_intelligence.evidence import ReliabilityEvidenceManager
from app.reliability_intelligence.evidence_lineage import ReliabilityEvidenceLineageGraph
from app.reliability_intelligence.explainability import ReliabilityExplainabilityEngine
from app.reliability_intelligence.failure_analysis import FailureAnalysisEngine
from app.reliability_intelligence.failure_prediction import FailurePredictionEngine
from app.reliability_intelligence.failure_propagation import FailurePropagationEngine
from app.reliability_intelligence.governance import ReliabilityGovernanceEngine
from app.reliability_intelligence.idempotency import ReliabilityIdempotencyManager
from app.reliability_intelligence.impact import ReliabilityImpactAssessment
from app.reliability_intelligence.learning import ReliabilityLearningEngine
from app.reliability_intelligence.models import (
    ChaosExperimentProposal,
    DegradationPlan,
    ErrorBudget,
    FailurePrediction,
    FailurePropagationPath,
    RecoveryPlan,
    ReliabilityAssessment,
    ServiceHealthAssessment,
    ServiceLevelObjective,
)
from app.reliability_intelligence.observability import ReliabilityMetricsCollector
from app.reliability_intelligence.providers import (
    MockReliabilityIntelligenceProvider,
    ReliabilityIntelligenceProviderRegistry,
)
from app.reliability_intelligence.recommendations import ReliabilityRecommendationEngine
from app.reliability_intelligence.recovery import RecoveryIntelligenceEngine
from app.reliability_intelligence.recovery_readiness import RecoveryReadinessEngine
from app.reliability_intelligence.recovery_simulation import RecoverySimulationEngine
from app.reliability_intelligence.reliability import MasterReliabilityEngine
from app.reliability_intelligence.reliability_risk import ReliabilityRiskEngine
from app.reliability_intelligence.repositories import (
    FailurePredictionRepository,
    ReliabilityAssessmentRepository,
    ReliabilityEvidenceRepository,
    ServiceHealthRepository,
    SLORepository,
)
from app.reliability_intelligence.reproducibility import ReliabilityReproducibilityRecord
from app.reliability_intelligence.resilience import ResilienceEngine
from app.reliability_intelligence.resilience_patterns import ResiliencePatternEngine
from app.reliability_intelligence.service_health import ServiceHealthEngine
from app.reliability_intelligence.slo import ServiceLevelObjectiveEngine
from app.reliability_intelligence.snapshots import ReliabilitySnapshotManager
from app.reliability_intelligence.timeline import ReliabilityTimeline
from app.reliability_intelligence.trust import ReliabilityTrustEngine
from app.reliability_intelligence.uncertainty import ReliabilityUncertaintyAssessment
from app.reliability_intelligence.verification import ReliabilityVerificationEngine

logger = logging.getLogger(__name__)


class ReliabilityIntelligenceManager:
    """Thin manager orchestrating specialized Reliability Intelligence engines."""

    def __init__(self) -> None:
        # Repositories
        self.health_repo = ServiceHealthRepository()
        self.rel_repo = ReliabilityAssessmentRepository()
        self.slo_repo = SLORepository()
        self.pred_repo = FailurePredictionRepository()
        self.evidence_repo = ReliabilityEvidenceRepository()

        # Providers
        self.provider_registry = ReliabilityIntelligenceProviderRegistry()
        self._register_default_providers()

        # Engines
        self.health_engine = ServiceHealthEngine(self.health_repo)
        self.master_reliability_engine = MasterReliabilityEngine(self.provider_registry, self.rel_repo)
        self.slo_engine = ServiceLevelObjectiveEngine(self.slo_repo)
        self.error_budget_engine = ErrorBudgetEngine()
        self.dependency_graph = ReliabilityDependencyGraph()
        self.failure_analysis_engine = FailureAnalysisEngine()
        self.failure_prediction_engine = FailurePredictionEngine(self.pred_repo)
        self.anomaly_engine = ReliabilityAnomalyEngine()
        self.failure_propagation_engine = FailurePropagationEngine()
        self.blast_radius_analyzer = BlastRadiusAnalyzer()
        self.resilience_engine = ResilienceEngine()
        self.resilience_pattern_engine = ResiliencePatternEngine()
        self.degradation_engine = SafeDegradationEngine()
        self.recovery_engine = RecoveryIntelligenceEngine()
        self.recovery_readiness_engine = RecoveryReadinessEngine()
        self.recovery_simulation_engine = RecoverySimulationEngine()
        self.capacity_engine = CapacityIntelligenceEngine()
        self.risk_engine = ReliabilityRiskEngine()
        self.impact_assessment = ReliabilityImpactAssessment()
        self.rec_engine = ReliabilityRecommendationEngine()
        self.governance_engine = ReliabilityGovernanceEngine()
        self.approval_engine = ReliabilityApprovalEngine()
        self.chaos_governance = ChaosExperimentGovernanceEngine()
        self.delegation_coordinator = ReliabilityDelegationCoordinator()
        self.verification_engine = ReliabilityVerificationEngine()
        self.assurance_engine = ReliabilityAssuranceEngine()
        self.confidence_engine = ReliabilityConfidenceEngine()
        self.uncertainty_assessment = ReliabilityUncertaintyAssessment()
        self.trust_engine = ReliabilityTrustEngine()
        self.evidence_manager = ReliabilityEvidenceManager(self.evidence_repo)
        self.evidence_lineage = ReliabilityEvidenceLineageGraph()
        self.explainability_engine = ReliabilityExplainabilityEngine()
        self.timeline = ReliabilityTimeline()
        self.snapshot_manager = ReliabilitySnapshotManager()
        self.reproducibility_record = ReliabilityReproducibilityRecord()
        self.learning_engine = ReliabilityLearningEngine()
        self.analytics = ReliabilityAnalytics()
        self.observability = ReliabilityMetricsCollector()
        self.billing = ReliabilityBillingTracker()
        self.idempotency = ReliabilityIdempotencyManager()

        logger.info("Initialized ReliabilityIntelligenceManager with specialized engines")

    def _register_default_providers(self) -> None:
        domains = [
            "operations",
            "security",
            "identity",
            "continuous",
            "autonomous",
            "unified",
            "decision",
            "policy",
            "control",
            "risk",
            "trust",
        ]
        for domain in domains:
            self.provider_registry.register_provider(domain, MockReliabilityIntelligenceProvider(domain=domain))

    # Service Health
    def evaluate_service_health(
        self, tenant_id: str, service_id: str, raw_metrics: Optional[Dict[str, Any]] = None
    ) -> ServiceHealthAssessment:
        sh = self.health_engine.evaluate_service_health(tenant_id, service_id, raw_metrics)
        self.timeline.record_event(
            tenant_id, "SERVICE_HEALTH_EVALUATED", f"Health status for '{service_id}': {sh.status.value}"
        )
        self.observability.increment("ai_reliability_intelligence_health_score")
        self.billing.record_usage(tenant_id, "HEALTH_EVALUATION")
        return sh

    # Master Reliability
    def evaluate_reliability(self, tenant_id: str, scope: Optional[str] = None) -> ReliabilityAssessment:
        ass = self.master_reliability_engine.evaluate_reliability(tenant_id, scope)
        self.timeline.record_event(
            tenant_id, "RELIABILITY_EVALUATED", f"Reliability score: {ass.score.overall_score:.4f}"
        )
        self.observability.increment("ai_reliability_intelligence_reliability_score")
        return ass

    # SLO & Budget
    def create_slo(
        self, tenant_id: str, service_id: str, indicator_type: str = "AVAILABILITY", target_percentage: float = 99.9
    ) -> ServiceLevelObjective:
        return self.slo_engine.create_slo(tenant_id, service_id, indicator_type, target_percentage)

    def evaluate_error_budget(
        self, tenant_id: str, slo_id: str, total_minutes: float = 43.2, burn_rate: float = 1.0
    ) -> ErrorBudget:
        return self.error_budget_engine.evaluate_error_budget(tenant_id, slo_id, total_minutes, burn_rate)

    # Failure Prediction
    def predict_failure(
        self,
        tenant_id: str,
        service_id: str,
        recent_error_rate: float = 0.05,
        capacity_utilization: float = 0.85,
        horizon_minutes: int = 60,
    ) -> FailurePrediction:
        pred = self.failure_prediction_engine.predict_failure(
            tenant_id, service_id, recent_error_rate, capacity_utilization, horizon_minutes
        )
        self.timeline.record_event(
            tenant_id, "FAILURE_PREDICTED", f"Predicted failure probability for '{service_id}': {pred.probability:.2f}"
        )
        self.observability.increment("ai_reliability_intelligence_failure_predictions_total")
        return pred

    # Failure Propagation
    def analyze_propagation(
        self, tenant_id: str, origin_service: str, downstream_services: List[str]
    ) -> FailurePropagationPath:
        return self.failure_propagation_engine.analyze_propagation(tenant_id, origin_service, downstream_services)

    # Degradation & Recovery
    def plan_degradation(self, tenant_id: str, service_id: str, strategy: str = "GRACEFUL") -> DegradationPlan:
        return self.degradation_engine.plan_degradation(tenant_id, service_id, strategy)

    def plan_recovery(self, tenant_id: str, service_id: str, strategy: str = "FAILOVER") -> RecoveryPlan:
        return self.recovery_engine.plan_recovery(tenant_id, service_id, strategy)

    # Chaos Governance
    def propose_chaos_experiment(
        self, tenant_id: str, experiment_name: str, target_service: str, hypothesis: str
    ) -> ChaosExperimentProposal:
        return self.chaos_governance.propose_chaos_experiment(tenant_id, experiment_name, target_service, hypothesis)

    # Delegation & Governance
    def evaluate_governance(self, tenant_id: str, action_type: str, risk_level: str = "MEDIUM") -> Dict[str, Any]:
        return self.governance_engine.evaluate_governance(tenant_id, action_type, risk_level)

    def create_delegation(
        self, tenant_id: str, action_name: str, parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        self.governance_engine.enforce_approval_check(tenant_id, action_name, is_approved=True)
        return self.delegation_coordinator.create_delegation_request(tenant_id, action_name, parameters)
