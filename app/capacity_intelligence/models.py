"""Pure Python domain models for Capacity Intelligence (Phase 5.56)."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class CapacityLifecycleState(str, Enum):
    RESOURCE_PROFILING = "RESOURCE_PROFILING"
    TELEMETRY_INGESTION = "TELEMETRY_INGESTION"
    WORKLOAD_ANALYSIS = "WORKLOAD_ANALYSIS"
    CAPACITY_ASSESSMENT = "CAPACITY_ASSESSMENT"
    FORECASTING = "FORECASTING"
    DEMAND_PREDICTION = "DEMAND_PREDICTION"
    SATURATION_ANALYSIS = "SATURATION_ANALYSIS"
    BOTTLENECK_DETECTION = "BOTTLENECK_DETECTION"
    EFFICIENCY_EVALUATION = "EFFICIENCY_EVALUATION"
    OPTIMIZATION_ANALYSIS = "OPTIMIZATION_ANALYSIS"
    GOVERNANCE_EVALUATION = "GOVERNANCE_EVALUATION"
    REQUIRES_APPROVAL = "REQUIRES_APPROVAL"
    APPROVED = "APPROVED"
    DELEGATION_CREATED = "DELEGATION_CREATED"
    VERIFICATION = "VERIFICATION"
    CLOSED = "CLOSED"


class CapacityStatus(str, Enum):
    HEALTHY = "HEALTHY"
    WATCH = "WATCH"
    CONSTRAINED = "CONSTRAINED"
    SATURATED = "SATURATED"
    CRITICAL = "CRITICAL"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DelegationStatus(str, Enum):
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXECUTING = "EXECUTING"
    EXECUTED = "EXECUTED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class GovernanceDecision(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    ADVISORY_ONLY = "ADVISORY_ONLY"


class WorkloadPattern(str, Enum):
    STEADY = "STEADY"
    INCREASING = "INCREASING"
    DECREASING = "DECREASING"
    BURSTY = "BURSTY"
    PERIODIC = "PERIODIC"
    SEASONAL = "SEASONAL"
    UNPREDICTABLE = "UNPREDICTABLE"


class BottleneckType(str, Enum):
    CPU = "CPU"
    MEMORY = "MEMORY"
    STORAGE = "STORAGE"
    NETWORK = "NETWORK"
    DATABASE = "DATABASE"
    CACHE = "CACHE"
    QUEUE = "QUEUE"
    APPLICATION = "APPLICATION"
    MODEL = "MODEL"
    DEPENDENCY = "DEPENDENCY"


class OptimizationType(str, Enum):
    RIGHT_SIZING = "RIGHT_SIZING"
    LOAD_BALANCING = "LOAD_BALANCING"
    RESOURCE_CONSOLIDATION = "RESOURCE_CONSOLIDATION"
    CACHE_OPTIMIZATION = "CACHE_OPTIMIZATION"
    WORKLOAD_SCHEDULING = "WORKLOAD_SCHEDULING"
    CAPACITY_EXPANSION = "CAPACITY_EXPANSION"
    COST_OPTIMIZATION = "COST_OPTIMIZATION"


class CapacityGovernanceOutcome(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    ADVISORY_ONLY = "ADVISORY_ONLY"


@dataclass
class ResourceProfile:
    tenant_id: str
    resource_id: str
    resource_type: str  # COMPUTE, CPU, MEMORY, STORAGE, NETWORK, DATABASE, GPU, etc.
    total_capacity: float
    unit: str = "cores"
    profile_id: str = field(default_factory=lambda: f"prof-{uuid.uuid4().hex[:12]}")
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    name: str = ""
    capacity_unit: str = "units"
    registered_at: Optional[datetime] = None


@dataclass
class CapacityTelemetry:
    tenant_id: str
    resource_id: str
    metric_name: str
    metric_value: float
    unit: str = "percentage"
    telemetry_id: str = field(default_factory=lambda: f"tel-{uuid.uuid4().hex[:12]}")
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def value(self) -> float:
        return self.metric_value


@dataclass
class WorkloadProfile:
    tenant_id: str
    service_id: str
    pattern: WorkloadPattern
    growth_rate_pct: float
    request_qps: float
    workload_id: str = field(default_factory=lambda: f"work-{uuid.uuid4().hex[:12]}")
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class CapacityAssessment:
    tenant_id: str
    resource_id: str
    status: CapacityStatus
    consumed_percentage: float
    headroom_percentage: float
    saturation_risk_score: float
    assessment_id: str = field(default_factory=lambda: f"cap-{uuid.uuid4().hex[:12]}")
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    utilization_rate: float = 0.65
    health_status: str = "HEALTHY"
    assessed_at: Optional[datetime] = None


@dataclass
class CapacityForecast:
    tenant_id: str
    resource_id: str
    forecast_horizon_days: int
    predicted_utilization_pct: float
    estimated_exhaustion_days: Optional[int]
    confidence_score: float
    forecast_id: str = field(default_factory=lambda: f"fc-{uuid.uuid4().hex[:12]}")
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    horizon_days: int = 30
    predicted_utilization: float = 0.85
    exhaustion_predicted: bool = False


@dataclass
class DemandPrediction:
    tenant_id: str
    service_id: str
    expected_qps_growth: float
    predicted_demand_units: float
    prediction_id: str = field(default_factory=lambda: f"dem-{uuid.uuid4().hex[:12]}")
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    workload_type: str = ""
    time_horizon_hours: int = 24
    predicted_growth_rate: float = 0.15
    confidence_score: float = 0.91
    predicted_at: Optional[datetime] = None


@dataclass
class SaturationAssessment:
    tenant_id: str
    resource_id: str
    is_saturated: bool
    saturation_probability: float
    time_to_saturation_hours: float
    assessment_id: str = field(default_factory=lambda: f"sat-{uuid.uuid4().hex[:12]}")
    saturation_level: float = 0.75
    headroom_percent: float = 25.0
    analyzed_at: Optional[datetime] = None

    @property
    def analysis_id(self) -> str:
        return self.assessment_id


@dataclass
class PerformanceAssessment:
    tenant_id: str
    service_id: str
    latency_p99_ms: float
    throughput_qps: float
    error_rate: float
    efficiency_score: float
    assessment_id: str = field(default_factory=lambda: f"perf-{uuid.uuid4().hex[:12]}")


@dataclass
class Bottleneck:
    tenant_id: str
    resource_id: str
    bottleneck_type: BottleneckType
    severity: str
    description: str = "Capacity bottleneck detected"
    bottleneck_id: str = field(default_factory=lambda: f"bot-{uuid.uuid4().hex[:12]}")
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    impact_description: str = ""


@dataclass
class ResourceEfficiencyAssessment:
    tenant_id: str
    resource_id: str
    is_overprovisioned: bool
    is_underprovisioned: bool
    efficiency_score: float
    potential_savings_usd: float
    assessment_id: str = field(default_factory=lambda: f"eff-{uuid.uuid4().hex[:12]}")


@dataclass
class CapacityOptimization:
    tenant_id: str
    target_resource_id: str
    optimization_type: OptimizationType
    recommended_action: str
    estimated_cost_impact_usd: float
    optimization_id: str = field(default_factory=lambda: f"opt-{uuid.uuid4().hex[:12]}")
    auto_execute: bool = False  # Strictly False invariant
    resource_id: str = ""
    objective: str = "COST_PERFORMANCE"
    recommendations: List[Any] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def plan_id(self) -> str:
        return self.optimization_id


@dataclass
class CapacityTradeoffAnalysis:
    tenant_id: str
    scenario_name: str
    cost_score: float
    performance_score: float
    reliability_score: float
    tradeoff_id: str = field(default_factory=lambda: f"trade-{uuid.uuid4().hex[:12]}")


@dataclass
class CapacityScenario:
    tenant_id: str
    scenario_name: str
    workload_multiplier: float
    simulated_headroom_pct: float
    is_feasible: bool
    scenario_id: str = field(default_factory=lambda: f"scen-{uuid.uuid4().hex[:12]}")
    bottleneck_predicted: bool = False


@dataclass
class CapacityRecommendation:
    tenant_id: str
    target_resource_id: str
    recommendation_type: str
    action_description: str
    recommendation_id: str = field(default_factory=lambda: f"crec-{uuid.uuid4().hex[:12]}")
    priority: str = "HIGH"
    reason: str = "Predictive capacity optimization"
    confidence: float = 0.92
    auto_execute: bool = False  # Strictly False invariant
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class CapacityAssuranceScore:
    tenant_id: str
    assurance_score: float
    status: str  # HEALTHY, WATCH, CONSTRAINED, SATURATED, CRITICAL
    component_scores: Dict[str, float]
    score_id: str = field(default_factory=lambda: f"cass-{uuid.uuid4().hex[:12]}")
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class CapacityRiskProfile:
    tenant_id: str
    resource_id: str
    overall_risk_score: float
    risk_level: str
    risk_profile_id: str = field(default_factory=lambda: f"crisk-{uuid.uuid4().hex[:12]}")


@dataclass
class CapacityEvidenceBundle:
    tenant_id: str
    assessment_id: str
    integrity_hash: str
    evidence_id: str = field(default_factory=lambda: f"cevd-{uuid.uuid4().hex[:12]}")
    is_sealed: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def evidence_hash(self) -> str:
        return self.integrity_hash

    @property
    def bundle_id(self) -> str:
        return self.evidence_id

    @property
    def sealed(self) -> bool:
        return self.is_sealed

    @property
    def records(self) -> list:
        return []


@dataclass
class CapacitySnapshot:
    tenant_id: str
    assessment: CapacityAssessment
    snapshot_id: str = field(default_factory=lambda: f"csnap-{uuid.uuid4().hex[:12]}")
    snapshot_fingerprint: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def captured_at(self) -> datetime:
        return self.created_at

    @property
    def records_count(self) -> int:
        return 1

    @property
    def integrity_hash(self) -> str:
        return self.snapshot_fingerprint or "hash-csnap"
