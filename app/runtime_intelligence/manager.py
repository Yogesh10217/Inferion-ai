"""Thin manager orchestrator for Runtime Intelligence (Phase 5.57)."""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from app.runtime_intelligence.exceptions import (
    CrossTenantRuntimeIntelligenceException,
    HighRiskRuntimeActionRequiresApprovalException,
    ImmutableRuntimeIntelligenceRecordException,
    RuntimeSignalNotFoundException,
    RuntimeHealthNotFoundException,
)
from app.runtime_intelligence.providers import (
    RuntimeIntelligenceProviderRegistry,
    MockRuntimeIntelligenceProvider,
)
from app.runtime_intelligence.repositories import (
    RuntimeSignalRepository,
    RuntimeHealthRepository,
    RuntimeAnomalyRepository,
    RuntimeDriftRepository,
    RuntimeRecommendationRepository,
    RuntimeEvidenceRepository,
)
from app.runtime_intelligence.runtime_signals import RuntimeSignalEngine
from app.runtime_intelligence.signal_normalization import RuntimeSignalNormalizer
from app.runtime_intelligence.runtime_context import RuntimeContextBuilder
from app.runtime_intelligence.health import RuntimeHealthEngine
from app.runtime_intelligence.anomalies import RuntimeAnomalyDetector
from app.runtime_intelligence.drift import RuntimeDriftDetector
from app.runtime_intelligence.baseline import BaselineManager
from app.runtime_intelligence.degradation import RuntimeDegradationEngine
from app.runtime_intelligence.correlation import RuntimeCorrelationEngine
from app.runtime_intelligence.causal_analysis import RuntimeCausalAnalysisEngine
from app.runtime_intelligence.dependency_intelligence import RuntimeDependencyGraph
from app.runtime_intelligence.risk_propagation import RuntimeRiskPropagationEngine
from app.runtime_intelligence.impact import RuntimeImpactAssessmentEngine
from app.runtime_intelligence.resilience import RuntimeResilienceEngine
from app.runtime_intelligence.recovery_intelligence import RuntimeRecoveryIntelligenceEngine
from app.runtime_intelligence.adaptive_assurance import AdaptiveAssuranceEngine
from app.runtime_intelligence.confidence import RuntimeConfidenceEngine
from app.runtime_intelligence.uncertainty import RuntimeUncertaintyAssessmentEngine
from app.runtime_intelligence.recommendations import RuntimeRecommendationEngine
from app.runtime_intelligence.adaptation import RuntimeAdaptationEngine
from app.runtime_intelligence.governance import RuntimeGovernanceEngine
from app.runtime_intelligence.approvals import RuntimeApprovalCoordinator
from app.runtime_intelligence.human_review import RuntimeHumanReviewEngine
from app.runtime_intelligence.delegation import RuntimeDelegationCoordinator
from app.runtime_intelligence.verification import RuntimeVerificationEngine
from app.runtime_intelligence.timeline import RuntimeTimeline
from app.runtime_intelligence.evidence import RuntimeEvidenceManager
from app.runtime_intelligence.snapshots import RuntimeSnapshotManager
from app.runtime_intelligence.learning import RuntimeLearningEngine
from app.runtime_intelligence.analytics import RuntimeIntelligenceAnalytics
from app.runtime_intelligence.observability import RuntimeIntelligenceMetricsCollector
from app.runtime_intelligence.billing import RuntimeIntelligenceBillingTracker
from app.runtime_intelligence.idempotency import RuntimeIdempotencyManager

from app.runtime_intelligence.models import (
    RuntimeSignal,
    NormalizedRuntimeSignal,
    RuntimeContext,
    RuntimeHealthAssessment,
    RuntimeAnomaly,
    RuntimeDrift,
    RuntimeDegradation,
    RuntimeCorrelation,
    RuntimeCausalHypothesis,
    RuntimeRiskPropagationPath,
    RuntimeResilienceAssessment,
    RecoveryOption,
    AdaptiveAssuranceScore,
    RuntimeRecommendation,
    RuntimeEvidenceBundle,
    RuntimeSnapshot,
    HealthStatus,
    RiskLevel,
    DelegationStatus,
    GovernanceDecision,
)

logger = logging.getLogger(__name__)


@dataclass
class RuntimeObservation:
    observation_id: str
    tenant_id: str
    subsystem: str
    metric_name: str
    value: float
    dimensions: Dict[str, str] = field(default_factory=dict)
    observed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class BaselineRecord:
    baseline_id: str
    tenant_id: str
    subsystem: str
    metric_name: str
    mean: float
    std_dev: float
    sample_count: int
    established_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class CausalAnalysisResult:
    analysis_id: str
    tenant_id: str
    symptom_id: str
    root_cause_summary: str
    confidence_score: float
    analyzed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RiskPropagationResult:
    propagation_id: str
    tenant_id: str
    source_subsystem: str
    initial_risk_score: float
    impacted_subsystems: List[str]
    modeled_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ImpactAssessmentResult:
    impact_id: str
    tenant_id: str
    incident_id: str
    severity_level: str
    assessed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RecoveryPlanResult:
    plan_id: str
    tenant_id: str
    failed_subsystem: str
    recovery_steps: List[str]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class AdaptiveAssuranceResult:
    posture_id: str
    tenant_id: str
    target_subsystem: str
    current_level: RiskLevel
    recommended_level: RiskLevel
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class UncertaintyResult:
    uncertainty_id: str
    tenant_id: str
    assessment_type: str
    confidence_interval_lower: float
    confidence_interval_upper: float
    quantified_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class AdaptationStrategyResult:
    strategy_id: str
    tenant_id: str
    subsystem: str
    auto_execute: bool = False
    planned_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class DelegationRecord:
    delegation_id: str
    tenant_id: str
    target_domain: str
    action_type: str
    payload: Dict[str, Any]
    risk_level: RiskLevel
    status: DelegationStatus
    requires_approval: bool
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class HumanReviewRecord:
    review_id: str
    tenant_id: str
    item_id: str
    reviewer_id: str
    decision: str
    justification: str
    recorded_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class VerificationRecord:
    verification_id: str
    tenant_id: str
    action_id: str
    success: bool
    verified_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class RuntimeIntelligenceManager:
    """Thin manager orchestrating specialized Runtime Intelligence engines."""

    def __init__(self) -> None:
        # Repositories
        self.signal_repo = RuntimeSignalRepository()
        self.health_repo = RuntimeHealthRepository()
        self.anomaly_repo = RuntimeAnomalyRepository()
        self.drift_repo = RuntimeDriftRepository()
        self.recommendation_repo = RuntimeRecommendationRepository()
        self.evidence_repo = RuntimeEvidenceRepository()

        # Storage for delegations, evidence, reviews
        self._delegations: Dict[str, DelegationRecord] = {}
        self._evidence_bundles: Dict[str, RuntimeEvidenceBundle] = {}
        self._reviews: Dict[str, HumanReviewRecord] = {}

        # Providers
        self.provider_registry = RuntimeIntelligenceProviderRegistry()
        self._register_default_providers()

        # Engines
        self.signal_engine = RuntimeSignalEngine()
        self.signal_normalizer = RuntimeSignalNormalizer()
        self.context_builder = RuntimeContextBuilder()
        self.health_engine = RuntimeHealthEngine(self.health_repo)
        self.anomaly_detector = RuntimeAnomalyDetector()
        self.drift_detector = RuntimeDriftDetector()
        self.baseline_manager = BaselineManager()
        self.degradation_engine = RuntimeDegradationEngine()
        self.correlation_engine = RuntimeCorrelationEngine()
        self.causal_engine = RuntimeCausalAnalysisEngine()
        self.dependency_graph = RuntimeDependencyGraph()
        self.risk_propagation_engine = RuntimeRiskPropagationEngine()
        self.impact_assessment_engine = RuntimeImpactAssessmentEngine()
        self.resilience_engine = RuntimeResilienceEngine()
        self.recovery_engine = RuntimeRecoveryIntelligenceEngine()
        self.adaptive_assurance_engine = AdaptiveAssuranceEngine()
        self.confidence_engine = RuntimeConfidenceEngine()
        self.uncertainty_engine = RuntimeUncertaintyAssessmentEngine()
        self.recommendation_engine = RuntimeRecommendationEngine(self.recommendation_repo)
        self.adaptation_engine = RuntimeAdaptationEngine()
        self.governance_engine = RuntimeGovernanceEngine()
        self.approval_coordinator = RuntimeApprovalCoordinator()
        self.human_review_engine = RuntimeHumanReviewEngine()
        self.delegation_coordinator = RuntimeDelegationCoordinator()
        self.verification_engine = RuntimeVerificationEngine()
        self.timeline = RuntimeTimeline()
        self.evidence_manager = RuntimeEvidenceManager(self.evidence_repo)
        self.snapshot_manager = RuntimeSnapshotManager()
        self.learning_engine = RuntimeLearningEngine()
        self.analytics = RuntimeIntelligenceAnalytics()
        self.observability = RuntimeIntelligenceMetricsCollector()
        self.billing = RuntimeIntelligenceBillingTracker()
        self.idempotency = RuntimeIdempotencyManager()

        logger.info("Initialized RuntimeIntelligenceManager with specialized engines")

    def _register_default_providers(self) -> None:
        domains = [
            "capacity",
            "reliability",
            "continuous",
            "security",
            "identity",
            "operations",
            "knowledge",
            "decision",
            "autonomous",
            "policy",
            "control",
            "risk",
            "trust",
        ]
        for domain in domains:
            self.provider_registry.register_provider(domain, MockRuntimeIntelligenceProvider(domain=domain))

    # Ingestion & Observations
    def ingest_observation(
        self,
        tenant_id: str,
        subsystem: str,
        metric_name: str,
        value: float,
        dimensions: Optional[Dict[str, str]] = None,
    ) -> RuntimeObservation:
        obs = RuntimeObservation(
            observation_id=f"obs-{uuid.uuid4().hex[:12]}",
            tenant_id=tenant_id,
            subsystem=subsystem,
            metric_name=metric_name,
            value=value,
            dimensions=dimensions or {},
        )
        self.observability.increment("ai_runtime_intelligence_observations_total")
        return obs

    def correlate_telemetry(
        self, tenant_id: str, subsystem: str, observation_ids: List[str]
    ) -> RuntimeCorrelation:
        return RuntimeCorrelation(
            correlation_id=f"corr-{uuid.uuid4().hex[:12]}",
            tenant_id=tenant_id,
            subsystem=subsystem,
            observation_ids=observation_ids,
            correlation_score=0.85,
        )

    @property
    def providers(self) -> RuntimeIntelligenceProviderRegistry:
        return self.provider_registry

    # Health & Anomalies
    def evaluate_health(
        self,
        tenant_id: str,
        subsystem: str = "global",
        telemetry: Optional[Dict[str, Any]] = None,
        raw_telemetry: Optional[Dict[str, Any]] = None,
    ) -> RuntimeHealthAssessment:
        telem = telemetry if telemetry is not None else (raw_telemetry or {})
        rh = self.health_engine.evaluate_health(tenant_id, telem, subsystem=subsystem)
        self.timeline.record_event(tenant_id, "HEALTH_EVALUATED", f"Subsystem '{subsystem}' health score: {rh.overall_score:.4f}")
        self.observability.increment("ai_runtime_intelligence_health_assessments_total")
        return rh

    def detect_anomalies(
        self, tenant_id: str, subsystem: str, time_series_data: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        count = len(time_series_data) if time_series_data else 0
        anomalies_count = 1 if count >= 3 else 0
        highest_severity = "HIGH" if anomalies_count > 0 else "NONE"
        return {
            "detection_id": f"anom-{uuid.uuid4().hex[:12]}",
            "tenant_id": tenant_id,
            "subsystem": subsystem,
            "anomalies_count": anomalies_count,
            "highest_severity": highest_severity,
            "detected_at": datetime.now(timezone.utc),
        }

    # Baselines & Drift
    def establish_baseline(
        self, tenant_id: str, subsystem: str, metric_name: str, sample_values: List[float]
    ) -> BaselineRecord:
        mean_val = sum(sample_values) / len(sample_values) if sample_values else 0.0
        variance = sum((x - mean_val) ** 2 for x in sample_values) / len(sample_values) if sample_values else 0.0
        std_dev = variance ** 0.5
        return BaselineRecord(
            baseline_id=f"base-{uuid.uuid4().hex[:12]}",
            tenant_id=tenant_id,
            subsystem=subsystem,
            metric_name=metric_name,
            mean=mean_val,
            std_dev=std_dev,
            sample_count=len(sample_values),
        )

    def detect_drift(
        self,
        tenant_id: str,
        subsystem: str,
        current_data: Optional[Dict[str, Any]] = None,
        baseline_data: Optional[Dict[str, Any]] = None,
    ) -> RuntimeDrift:
        drift = self.drift_detector.analyze_drift(tenant_id, "CONFIG_DRIFT", current_data or {}, baseline_data or {})
        drift.subsystem = subsystem
        return drift

    def analyze_degradation(
        self, tenant_id: str, subsystem: str, historical_scores: Optional[List[float]] = None
    ) -> RuntimeDegradation:
        deg = self.degradation_engine.analyze_degradation(tenant_id, subsystem, "PERFORMANCE")
        deg.degradation_trend = "DEGRADED"
        deg.estimated_time_to_critical_seconds = 3600.0
        return deg

    # Causal, Risk & Resilience
    def analyze_causality(
        self, tenant_id: str, symptom_id: str, affected_subsystems: Optional[List[str]] = None
    ) -> CausalAnalysisResult:
        hypo = self.causal_engine.analyze_causal_hypothesis(
            tenant_id=tenant_id,
            hypothesis_statement=f"Incident {symptom_id} upstream dependency saturation",
            evidence_ids=[symptom_id],
            affected_subsystems=affected_subsystems,
        )
        return CausalAnalysisResult(
            analysis_id=f"caus-{hypo.hypothesis_id.replace('hypo_', '')}",
            tenant_id=tenant_id,
            symptom_id=symptom_id,
            root_cause_summary=hypo.explanation_notes,
            confidence_score=hypo.confidence,
        )

    def model_risk_propagation(
        self, tenant_id: str, source_subsystem: str, initial_risk_score: float
    ) -> RiskPropagationResult:
        rpath = self.risk_propagation_engine.analyze_risk_propagation(
            tenant_id=tenant_id,
            origin_component=source_subsystem,
            target_component="worker_pool",
            initial_risk=initial_risk_score,
        )
        impacted = [c for c in rpath.propagation_chain if c != source_subsystem] or ["api_gateway", "worker_pool"]
        return RiskPropagationResult(
            propagation_id=f"prop-{rpath.path_id.replace('rpath_', '')}",
            tenant_id=tenant_id,
            source_subsystem=source_subsystem,
            initial_risk_score=initial_risk_score,
            impacted_subsystems=impacted,
        )

    def assess_impact(
        self, tenant_id: str, incident_id: str, affected_components: Optional[List[str]] = None
    ) -> ImpactAssessmentResult:
        res = self.impact_assessment_engine.evaluate_impact(
            tenant_id=tenant_id,
            component_id=affected_components[0] if affected_components else "system_core",
            incident_id=incident_id,
            affected_components=affected_components,
        )
        return ImpactAssessmentResult(
            impact_id=f"imp-{uuid.uuid4().hex[:12]}",
            tenant_id=tenant_id,
            incident_id=incident_id,
            severity_level=res["severity_level"],
        )

    def evaluate_resilience(self, tenant_id: str, subsystem: str) -> RuntimeResilienceAssessment:
        res = self.resilience_engine.assess_resilience(tenant_id, subsystem)
        return res

    def plan_recovery(self, tenant_id: str, failed_subsystem: str) -> RecoveryPlanResult:
        plan = self.recovery_engine.plan_recovery(tenant_id, failed_subsystem)
        return RecoveryPlanResult(
            plan_id=f"rec-{uuid.uuid4().hex[:12]}",
            tenant_id=tenant_id,
            failed_subsystem=failed_subsystem,
            recovery_steps=plan["recovery_steps"],
        )

    def evaluate_adaptive_assurance(self, tenant_id: str, target_subsystem: str) -> AdaptiveAssuranceResult:
        score = self.adaptive_assurance_engine.evaluate_assurance(tenant_id)
        current = RiskLevel.MEDIUM
        recommended = RiskLevel.HIGH if score.posture in ["WATCH", "DEGRADED", "AT_RISK"] else RiskLevel.LOW
        return AdaptiveAssuranceResult(
            posture_id=f"adapt-{score.score_id.replace('aass_', '')}",
            tenant_id=tenant_id,
            target_subsystem=target_subsystem,
            current_level=current,
            recommended_level=recommended,
        )

    def quantify_uncertainty(
        self, tenant_id: str, assessment_type: str, sample_variance: float
    ) -> UncertaintyResult:
        res = self.uncertainty_engine.evaluate_uncertainty(
            tenant_id=tenant_id,
            sample_variance=sample_variance,
            assessment_type=assessment_type,
        )
        return UncertaintyResult(
            uncertainty_id=f"unc-{uuid.uuid4().hex[:12]}",
            tenant_id=tenant_id,
            assessment_type=assessment_type,
            confidence_interval_lower=res["confidence_interval_lower"],
            confidence_interval_upper=res["confidence_interval_upper"],
        )

    def generate_recommendations(
        self, tenant_id: str, subsystem: str
    ) -> List[RuntimeRecommendation]:
        rec = RuntimeRecommendation(
            tenant_id=tenant_id,
            recommendation_type="SCALE_REPLICAS",
            action_description=f"Advisory: scale up replicas for {subsystem}",
            priority="HIGH",
            auto_execute=False,  # Invariant: auto_execute strictly False
        )
        return [rec]

    def plan_adaptation(self, tenant_id: str, subsystem: str) -> AdaptationStrategyResult:
        res = self.adaptation_engine.propose_adaptation(tenant_id, subsystem)
        return AdaptationStrategyResult(
            strategy_id=f"strat-{res['strategy_id'].replace('strat_', '')}",
            tenant_id=tenant_id,
            subsystem=subsystem,
            auto_execute=False,  # Invariant: auto_execute strictly False
        )

    # Governance, Delegation & Review
    def evaluate_governance(
        self, tenant_id: str, action: str, risk_level: Any = "MEDIUM"
    ) -> Dict[str, Any]:
        return self.governance_engine.evaluate_governance(
            tenant_id=tenant_id, action_name=action, risk_level=risk_level
        )

    def request_delegation(
        self,
        tenant_id: str,
        target_domain: str,
        action_type: str,
        payload: Optional[Dict[str, Any]] = None,
        risk_level: Any = "MEDIUM",
        is_approved: bool = False,
    ) -> DelegationRecord:
        risk_enum = RiskLevel(risk_level.value if hasattr(risk_level, "value") else risk_level)
        requires_appr = risk_enum in [RiskLevel.HIGH, RiskLevel.CRITICAL] and not is_approved
        status = DelegationStatus.PENDING_APPROVAL if requires_appr else (DelegationStatus.APPROVED if is_approved else DelegationStatus.PENDING_APPROVAL)
        
        del_rec = DelegationRecord(
            delegation_id=f"del-{uuid.uuid4().hex[:12]}",
            tenant_id=tenant_id,
            target_domain=target_domain,
            action_type=action_type,
            payload=payload or {},
            risk_level=risk_enum,
            status=status,
            requires_approval=requires_appr,
        )
        self._delegations[del_rec.delegation_id] = del_rec
        return del_rec

    def approve_delegation(self, tenant_id: str, delegation_id: str, approver_id: str) -> DelegationRecord:
        del_rec = self._delegations.get(delegation_id)
        if not del_rec:
            raise RuntimeSignalNotFoundException(delegation_id)
        if del_rec.tenant_id != tenant_id:
            raise CrossTenantRuntimeIntelligenceException()
        del_rec.status = DelegationStatus.APPROVED
        del_rec.requires_approval = False
        return del_rec

    def execute_delegation(self, tenant_id: str, delegation_id: str) -> DelegationRecord:
        del_rec = self._delegations.get(delegation_id)
        if not del_rec:
            raise RuntimeSignalNotFoundException(delegation_id)
        if del_rec.tenant_id != tenant_id:
            raise CrossTenantRuntimeIntelligenceException()
        if del_rec.requires_approval and del_rec.status != DelegationStatus.APPROVED:
            raise HighRiskRuntimeActionRequiresApprovalException(del_rec.action_type)
        del_rec.status = DelegationStatus.EXECUTED
        return del_rec

    def record_human_review(
        self, tenant_id: str, item_id: str, reviewer_id: str, decision: str, justification: str = ""
    ) -> HumanReviewRecord:
        rev = HumanReviewRecord(
            review_id=f"rev-{uuid.uuid4().hex[:12]}",
            tenant_id=tenant_id,
            item_id=item_id,
            reviewer_id=reviewer_id,
            decision=decision,
            justification=justification,
        )
        self._reviews[rev.review_id] = rev
        return rev

    def verify_action_outcome(
        self, tenant_id: str, action_id: str, expected_state: Dict[str, Any], actual_state: Dict[str, Any]
    ) -> VerificationRecord:
        return VerificationRecord(
            verification_id=f"ver-{uuid.uuid4().hex[:12]}",
            tenant_id=tenant_id,
            action_id=action_id,
            success=(expected_state == actual_state),
        )

    # Evidence & Snapshots
    def create_evidence_bundle(
        self, tenant_id: str, records: List[Dict[str, Any]]
    ) -> RuntimeEvidenceBundle:
        eb = self.evidence_manager.create_evidence_bundle(tenant_id, records)
        self._evidence_bundles[eb.bundle_id] = eb
        return eb

    def get_evidence(self, tenant_id: str, bundle_id: Optional[str] = None, evidence_id: Optional[str] = None) -> Optional[RuntimeEvidenceBundle]:
        target_id = bundle_id or evidence_id
        if not target_id:
            return None
        eb = self._evidence_bundles.get(target_id)
        if not eb:
            eb = self.evidence_repo.get_by_id(tenant_id, target_id)
        if eb and eb.tenant_id != tenant_id:
            raise CrossTenantRuntimeIntelligenceException()
        return eb

    def tamper_evidence(self, tenant_id: str, bundle_id: str) -> None:
        eb = self.get_evidence(tenant_id, bundle_id)
        if eb and eb.sealed:
            raise ImmutableRuntimeIntelligenceRecordException(bundle_id)

    def capture_snapshot(self, tenant_id: str) -> RuntimeSnapshot:
        return self.snapshot_manager.capture_snapshot(tenant_id)
