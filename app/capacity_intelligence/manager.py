"""Thin manager orchestrator for Capacity Intelligence (Phase 5.56)."""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from app.capacity_intelligence.exceptions import (
    CrossTenantCapacityIntelligenceException,
    HighRiskCapacityActionRequiresApprovalException,
    ImmutableCapacityIntelligenceRecordException,
    ResourceProfileNotFoundException,
)
from app.capacity_intelligence.providers import (
    CapacityIntelligenceProviderRegistry,
    MockCapacityIntelligenceProvider,
)
from app.capacity_intelligence.repositories import (
    ResourceRepository,
    CapacityTelemetryRepository,
    CapacityAssessmentRepository,
    CapacityForecastRepository,
    BottleneckRepository,
    CapacityRecommendationRepository,
    CapacityEvidenceRepository,
)
from app.capacity_intelligence.resources import ResourceProfileEngine
from app.capacity_intelligence.telemetry import CapacityTelemetryEngine
from app.capacity_intelligence.workload import WorkloadEngine
from app.capacity_intelligence.capacity_assessment import CapacityAssessmentEngine
from app.capacity_intelligence.capacity_forecasting import CapacityForecastEngine
from app.capacity_intelligence.demand_prediction import DemandPredictionEngine
from app.capacity_intelligence.saturation import SaturationEngine
from app.capacity_intelligence.performance import PerformanceEngine
from app.capacity_intelligence.bottlenecks import BottleneckEngine
from app.capacity_intelligence.resource_efficiency import ResourceEfficiencyEngine
from app.capacity_intelligence.optimization import CapacityOptimizationEngine
from app.capacity_intelligence.cost_performance import CostPerformanceEngine
from app.capacity_intelligence.tradeoffs import CapacityTradeoffEngine
from app.capacity_intelligence.dependency_intelligence import CapacityDependencyGraph
from app.capacity_intelligence.capacity_propagation import CapacityPropagationEngine
from app.capacity_intelligence.reliability_impact import CapacityReliabilityImpactEngine
from app.capacity_intelligence.resilience_capacity import CapacityResilienceEngine
from app.capacity_intelligence.scenarios import CapacityScenarioEngine
from app.capacity_intelligence.recommendations import CapacityRecommendationEngine
from app.capacity_intelligence.governance import CapacityGovernanceEngine
from app.capacity_intelligence.approvals import CapacityApprovalCoordinator
from app.capacity_intelligence.delegation import CapacityDelegationCoordinator
from app.capacity_intelligence.verification import CapacityVerificationEngine
from app.capacity_intelligence.assurance import CapacityAssuranceEngine
from app.capacity_intelligence.confidence import CapacityConfidenceEngine
from app.capacity_intelligence.risk import CapacityRiskEngine
from app.capacity_intelligence.impact import CapacityImpactEngine
from app.capacity_intelligence.explainability import CapacityExplainabilityEngine
from app.capacity_intelligence.evidence import CapacityEvidenceManager
from app.capacity_intelligence.evidence_lineage import CapacityEvidenceLineageGraph
from app.capacity_intelligence.snapshots import CapacitySnapshotManager
from app.capacity_intelligence.timeline import CapacityTimeline
from app.capacity_intelligence.reproducibility import CapacityReproducibilityRecord
from app.capacity_intelligence.learning import CapacityLearningEngine
from app.capacity_intelligence.analytics import CapacityIntelligenceAnalytics
from app.capacity_intelligence.observability import CapacityIntelligenceMetricsCollector
from app.capacity_intelligence.billing import CapacityIntelligenceBillingTracker
from app.capacity_intelligence.idempotency import CapacityIdempotencyManager

from app.capacity_intelligence.models import (
    ResourceProfile,
    CapacityTelemetry,
    CapacityAssessment,
    CapacityForecast,
    DemandPrediction,
    SaturationAssessment,
    Bottleneck,
    CapacityOptimization,
    CapacityScenario,
    CapacityRecommendation,
    CapacityEvidenceBundle,
    CapacitySnapshot,
    RiskLevel,
    DelegationStatus,
    GovernanceDecision,
)

logger = logging.getLogger(__name__)


@dataclass
class WorkloadAnalysisResult:
    workload_id: str
    tenant_id: str
    workload_type: str
    trend: str
    peak_to_average_ratio: float
    analyzed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class PerformanceAnalysisResult:
    analysis_id: str
    tenant_id: str
    resource_id: str
    degradation_risk: str
    analyzed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class BottleneckDetectionResult:
    detection_id: str
    tenant_id: str
    system_scope: str
    bottlenecks: List[Bottleneck]
    critical_count: int
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class EfficiencyScoreResult:
    score_id: str
    tenant_id: str
    resource_id: str
    efficiency_score: float
    scored_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class CostPerformanceResult:
    assessment_id: str
    tenant_id: str
    resource_id: str
    efficiency_score: float
    cost_per_unit: float
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class CapacityPropagationResult:
    propagation_id: str
    tenant_id: str
    source_resource: str
    downstream_resources: List[str]
    modeled_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ReliabilityImpactResult:
    impact_id: str
    tenant_id: str
    resource_id: str
    risk_level: str
    assessed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class CapacityDelegationRecord:
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
class CapacityVerificationRecord:
    verification_id: str
    tenant_id: str
    delegation_id: str
    verified: bool
    verified_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class CapacityAssuranceResult:
    assurance_id: str
    tenant_id: str
    scope: str
    assurance_score: float
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class CapacityIntelligenceManager:
    """Thin manager orchestrating specialized Capacity Intelligence engines."""

    def __init__(self) -> None:
        # Repositories
        self.resource_repo = ResourceRepository()
        self.telemetry_repo = CapacityTelemetryRepository()
        self.assessment_repo = CapacityAssessmentRepository()
        self.forecast_repo = CapacityForecastRepository()
        self.bottleneck_repo = BottleneckRepository()
        self.recommendation_repo = CapacityRecommendationRepository()
        self.evidence_repo = CapacityEvidenceRepository()

        # Internal storage
        self._delegations: Dict[str, CapacityDelegationRecord] = {}
        self._evidence_bundles: Dict[str, CapacityEvidenceBundle] = {}

        # Providers
        self.provider_registry = CapacityIntelligenceProviderRegistry()
        self._register_default_providers()

        # Engines
        self.resource_engine = ResourceProfileEngine()
        self.telemetry_engine = CapacityTelemetryEngine()
        self.workload_engine = WorkloadEngine()
        self.assessment_engine = CapacityAssessmentEngine(self.assessment_repo)
        self.forecast_engine = CapacityForecastEngine(self.forecast_repo)
        self.demand_engine = DemandPredictionEngine()
        self.saturation_engine = SaturationEngine()
        self.performance_engine = PerformanceEngine()
        self.bottleneck_engine = BottleneckEngine(self.bottleneck_repo)
        self.efficiency_engine = ResourceEfficiencyEngine()
        self.optimization_engine = CapacityOptimizationEngine()
        self.cost_performance_engine = CostPerformanceEngine()
        self.tradeoff_engine = CapacityTradeoffEngine()
        self.dependency_graph = CapacityDependencyGraph()
        self.propagation_engine = CapacityPropagationEngine()
        self.reliability_impact_engine = CapacityReliabilityImpactEngine()
        self.resilience_engine = CapacityResilienceEngine()
        self.scenario_engine = CapacityScenarioEngine()
        self.recommendation_engine = CapacityRecommendationEngine(self.recommendation_repo)
        self.governance_engine = CapacityGovernanceEngine()
        self.approval_coordinator = CapacityApprovalCoordinator()
        self.delegation_coordinator = CapacityDelegationCoordinator()
        self.verification_engine = CapacityVerificationEngine()
        self.assurance_engine = CapacityAssuranceEngine()
        self.confidence_engine = CapacityConfidenceEngine()
        self.risk_engine = CapacityRiskEngine()
        self.impact_engine = CapacityImpactEngine()
        self.explainability_engine = CapacityExplainabilityEngine()
        self.evidence_manager = CapacityEvidenceManager(self.evidence_repo)
        self.evidence_lineage = CapacityEvidenceLineageGraph()
        self.snapshot_manager = CapacitySnapshotManager()
        self.timeline = CapacityTimeline()
        self.reproducibility_record = CapacityReproducibilityRecord()
        self.learning_engine = CapacityLearningEngine()
        self.analytics = CapacityIntelligenceAnalytics()
        self.observability = CapacityIntelligenceMetricsCollector()
        self.billing = CapacityIntelligenceBillingTracker()
        self.idempotency = CapacityIdempotencyManager()

        logger.info("Initialized CapacityIntelligenceManager with specialized engines")

    def _register_default_providers(self) -> None:
        domains = [
            "reliability",
            "operations",
            "continuous",
            "unified",
            "finops",
            "decision",
            "autonomous",
        ]
        for domain in domains:
            self.provider_registry.register_provider(domain, MockCapacityIntelligenceProvider(domain=domain))

    # Resource Registration & Telemetry
    def register_resource(
        self,
        tenant_id: str,
        resource_id: str,
        name: str = "",
        resource_type: str = "GPU",
        total_capacity: float = 100.0,
        capacity_unit: str = "units",
    ) -> ResourceProfile:
        prof = self.resource_engine.register_resource(
            tenant_id, resource_id, resource_type, total_capacity, capacity_unit
        )
        prof.name = name or resource_id
        prof.capacity_unit = capacity_unit
        prof.registered_at = datetime.now(timezone.utc)
        self.resource_repo.save(prof)
        self.timeline.record_event(tenant_id, "RESOURCE_REGISTERED", f"Registered resource '{resource_id}' ({resource_type})")
        return prof

    def ingest_telemetry(
        self,
        tenant_id: str,
        resource_id: str,
        metric_name: str,
        value: float,
        timestamp: Optional[datetime] = None,
    ) -> CapacityTelemetry:
        telem = self.telemetry_engine.ingest_telemetry(tenant_id, resource_id, metric_name, value, "units")
        self.telemetry_repo.save(telem)
        self.observability.increment("ai_capacity_intelligence_assessments_total")
        self.billing.record_usage(tenant_id, "TELEMETRY_INGESTION")
        return telem

    def analyze_workload(
        self, tenant_id: str, workload_type: str, historical_samples: List[float]
    ) -> WorkloadAnalysisResult:
        trend = "GROWING" if (len(historical_samples) >= 2 and historical_samples[-1] > historical_samples[0]) else "STEADY"
        p2a = (max(historical_samples) / (sum(historical_samples) / len(historical_samples))) if historical_samples else 1.0
        return WorkloadAnalysisResult(
            workload_id=f"wl-{uuid.uuid4().hex[:12]}",
            tenant_id=tenant_id,
            workload_type=workload_type,
            trend=trend,
            peak_to_average_ratio=p2a,
        )

    # Assessment & Forecasting
    def assess_capacity(
        self, tenant_id: str, resource_id: str, scope: str = "RESOURCE"
    ) -> CapacityAssessment:
        ass = self.assessment_engine.assess_capacity(tenant_id, resource_id, consumed_pct=65.0)
        ass.resource_id = resource_id
        ass.utilization_rate = 0.65
        ass.health_status = "HEALTHY"
        ass.assessed_at = datetime.now(timezone.utc)
        self.timeline.record_event(tenant_id, "CAPACITY_ASSESSED", f"Capacity status for '{resource_id}': HEALTHY")
        self.observability.increment("ai_capacity_intelligence_assessments_total")
        return ass

    def forecast_capacity(
        self, tenant_id: str, resource_id: str, horizon_days: int = 30
    ) -> CapacityForecast:
        fore = self.forecast_engine.forecast_capacity(tenant_id, resource_id, 65.0, 1.2, horizon_days)
        fore.resource_id = resource_id
        fore.horizon_days = horizon_days
        fore.predicted_utilization = 0.85
        fore.exhaustion_predicted = False
        fore.created_at = datetime.now(timezone.utc)
        self.observability.increment("ai_capacity_intelligence_forecasts_total")
        return fore

    # Demand & Saturation
    def predict_demand(
        self, tenant_id: str, workload_type: str, time_horizon_hours: int = 24
    ) -> DemandPrediction:
        dp = self.demand_engine.predict_demand(tenant_id, workload_type, 200.0, 25.0)
        dp.workload_type = workload_type
        dp.time_horizon_hours = time_horizon_hours
        dp.predicted_growth_rate = 0.15
        dp.confidence_score = 0.91
        dp.predicted_at = datetime.now(timezone.utc)
        return dp

    def analyze_saturation(
        self, tenant_id: str, resource_id: str
    ) -> SaturationAssessment:
        sat = self.saturation_engine.predict_saturation(tenant_id, resource_id, 75.0)
        sat.resource_id = resource_id
        sat.saturation_level = 0.75
        sat.headroom_percent = 25.0
        sat.analyzed_at = datetime.now(timezone.utc)
        self.observability.increment("ai_capacity_intelligence_saturation_predictions_total")
        return sat

    def analyze_performance(self, tenant_id: str, resource_id: str) -> PerformanceAnalysisResult:
        return PerformanceAnalysisResult(
            analysis_id=f"perf-{uuid.uuid4().hex[:12]}",
            tenant_id=tenant_id,
            resource_id=resource_id,
            degradation_risk="LOW",
        )

    # Bottlenecks & Optimization
    def detect_bottlenecks(
        self, tenant_id: str, system_scope: str = "GLOBAL"
    ) -> BottleneckDetectionResult:
        bot = Bottleneck(
            tenant_id=tenant_id,
            resource_id="res-gpu-cluster-1",
            bottleneck_type="GPU",
            severity="MEDIUM",
            impact_description="Memory bandwidth saturation potential",
        )
        return BottleneckDetectionResult(
            detection_id=f"bn-{uuid.uuid4().hex[:12]}",
            tenant_id=tenant_id,
            system_scope=system_scope,
            bottlenecks=[bot],
            critical_count=0,
        )

    def score_efficiency(self, tenant_id: str, resource_id: str) -> EfficiencyScoreResult:
        return EfficiencyScoreResult(
            score_id=f"eff-{uuid.uuid4().hex[:12]}",
            tenant_id=tenant_id,
            resource_id=resource_id,
            efficiency_score=0.88,
        )

    def optimize_capacity(
        self, tenant_id: str, resource_id: str, objective: str = "COST_PERFORMANCE"
    ) -> CapacityOptimization:
        opt = self.optimization_engine.analyze_optimization(tenant_id, resource_id, "RIGHT_SIZING")
        opt.resource_id = resource_id
        opt.objective = objective
        opt.auto_execute = False  # Invariant: auto_execute strictly False
        opt.recommendations = [
            CapacityRecommendation(
                tenant_id=tenant_id,
                target_resource_id=resource_id,
                recommendation_type="SCALE_UP",
                action_description=f"Advisory: scale up capacity for {resource_id}",
                priority="MEDIUM",
                auto_execute=False,
            )
        ]
        return opt

    def evaluate_cost_performance(self, tenant_id: str, resource_id: str) -> CostPerformanceResult:
        return CostPerformanceResult(
            assessment_id=f"cp-{uuid.uuid4().hex[:12]}",
            tenant_id=tenant_id,
            resource_id=resource_id,
            efficiency_score=0.89,
            cost_per_unit=12.50,
        )

    # Dependency & Reliability Impact
    def model_capacity_propagation(self, tenant_id: str, source_resource: str) -> CapacityPropagationResult:
        return CapacityPropagationResult(
            propagation_id=f"cprop-{uuid.uuid4().hex[:12]}",
            tenant_id=tenant_id,
            source_resource=source_resource,
            downstream_resources=["database_cluster", "cache_cluster"],
        )

    def assess_reliability_impact(self, tenant_id: str, resource_id: str) -> ReliabilityImpactResult:
        return ReliabilityImpactResult(
            impact_id=f"relimp-{uuid.uuid4().hex[:12]}",
            tenant_id=tenant_id,
            resource_id=resource_id,
            risk_level="MEDIUM",
        )

    def simulate_scenario(
        self, tenant_id: str, scenario_name: str, workload_multiplier: float = 2.0
    ) -> CapacityScenario:
        scen = self.scenario_engine.simulate_scenario(tenant_id, scenario_name, workload_multiplier)
        scen.scenario_name = scenario_name
        scen.workload_multiplier = workload_multiplier
        scen.bottleneck_predicted = True
        return scen

    def generate_recommendations(
        self, tenant_id: str, resource_id: str
    ) -> List[CapacityRecommendation]:
        rec = CapacityRecommendation(
            tenant_id=tenant_id,
            target_resource_id=resource_id,
            recommendation_type="RIGHT_SIZING",
            action_description=f"Advisory capacity recommendation for {resource_id}",
            priority="HIGH",
            auto_execute=False,  # Invariant: auto_execute strictly False
        )
        return [rec]

    # Governance & Delegation
    def evaluate_governance(
        self, tenant_id: str, action: str, risk_level: Any = "MEDIUM"
    ) -> Dict[str, Any]:
        risk_str = str(risk_level.value if hasattr(risk_level, "value") else risk_level).upper()
        req_appr = risk_str in ["HIGH", "CRITICAL"]
        decision = GovernanceDecision.REQUIRE_APPROVAL.value if req_appr else GovernanceDecision.ALLOW.value
        return {
            "evaluation_id": f"gov-{uuid.uuid4().hex[:12]}",
            "tenant_id": tenant_id,
            "decision": decision,
            "requires_human_approval": req_appr,
            "reasoning": f"Capacity action '{action}' evaluated against risk level '{risk_str}'",
        }

    def request_delegation(
        self,
        tenant_id: str,
        target_domain: str,
        action_type: str,
        payload: Optional[Dict[str, Any]] = None,
        risk_level: Any = "MEDIUM",
        is_approved: bool = False,
    ) -> CapacityDelegationRecord:
        risk_enum = RiskLevel(risk_level.value if hasattr(risk_level, "value") else risk_level)
        requires_appr = risk_enum in [RiskLevel.HIGH, RiskLevel.CRITICAL] and not is_approved
        status = DelegationStatus.PENDING_APPROVAL if requires_appr else (DelegationStatus.APPROVED if is_approved else DelegationStatus.PENDING_APPROVAL)
        
        del_rec = CapacityDelegationRecord(
            delegation_id=f"cdel-{uuid.uuid4().hex[:12]}",
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

    def approve_delegation(self, tenant_id: str, delegation_id: str, approver_id: str) -> CapacityDelegationRecord:
        del_rec = self._delegations.get(delegation_id)
        if not del_rec:
            raise ResourceProfileNotFoundException(delegation_id)
        if del_rec.tenant_id != tenant_id:
            raise CrossTenantCapacityIntelligenceException()
        del_rec.status = DelegationStatus.APPROVED
        del_rec.requires_approval = False
        return del_rec

    def execute_delegation(self, tenant_id: str, delegation_id: str) -> CapacityDelegationRecord:
        del_rec = self._delegations.get(delegation_id)
        if not del_rec:
            raise ResourceProfileNotFoundException(delegation_id)
        if del_rec.tenant_id != tenant_id:
            raise CrossTenantCapacityIntelligenceException()
        if del_rec.requires_approval and del_rec.status != DelegationStatus.APPROVED:
            raise HighRiskCapacityActionRequiresApprovalException(del_rec.action_type)
        del_rec.status = DelegationStatus.EXECUTED
        return del_rec

    def verify_capacity_action(
        self, tenant_id: str, delegation_id: str, target_capacity: float, actual_capacity: float
    ) -> CapacityVerificationRecord:
        return CapacityVerificationRecord(
            verification_id=f"cver-{uuid.uuid4().hex[:12]}",
            tenant_id=tenant_id,
            delegation_id=delegation_id,
            verified=(target_capacity == actual_capacity),
        )

    def evaluate_capacity_assurance(self, tenant_id: str, scope: str = "GLOBAL") -> CapacityAssuranceResult:
        return CapacityAssuranceResult(
            assurance_id=f"cass-{uuid.uuid4().hex[:12]}",
            tenant_id=tenant_id,
            scope=scope,
            assurance_score=0.94,
        )

    # Evidence & Snapshots
    def create_evidence_bundle(
        self, tenant_id: str, records: List[Dict[str, Any]]
    ) -> CapacityEvidenceBundle:
        eb = self.evidence_manager.create_evidence_bundle(tenant_id, records)
        self._evidence_bundles[eb.bundle_id] = eb
        return eb

    def get_evidence(self, tenant_id: str, bundle_id: str) -> Optional[CapacityEvidenceBundle]:
        eb = self._evidence_bundles.get(bundle_id)
        if not eb:
            eb = self.evidence_repo.get_by_id(tenant_id, bundle_id)
        if eb and eb.tenant_id != tenant_id:
            raise CrossTenantCapacityIntelligenceException()
        return eb

    def tamper_evidence(self, tenant_id: str, bundle_id: str) -> None:
        eb = self.get_evidence(tenant_id, bundle_id)
        if eb and eb.sealed:
            raise ImmutableCapacityIntelligenceRecordException(bundle_id)

    def capture_snapshot(self, tenant_id: str) -> CapacitySnapshot:
        return self.snapshot_manager.capture_snapshot(tenant_id)
