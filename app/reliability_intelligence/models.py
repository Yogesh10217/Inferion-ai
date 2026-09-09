"""Pure Python domain models for Reliability Intelligence (Phase 5.55)."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional
import uuid


class ReliabilityLifecycleState(str, Enum):
    OBSERVING = "OBSERVING"
    HEALTH_ASSESSMENT = "HEALTH_ASSESSMENT"
    DEPENDENCY_ANALYSIS = "DEPENDENCY_ANALYSIS"
    ANOMALY_ANALYSIS = "ANOMALY_ANALYSIS"
    FAILURE_PREDICTION = "FAILURE_PREDICTION"
    FAILURE_PROPAGATION_ANALYSIS = "FAILURE_PROPAGATION_ANALYSIS"
    RELIABILITY_ASSESSMENT = "RELIABILITY_ASSESSMENT"
    RESILIENCE_ANALYSIS = "RESILIENCE_ANALYSIS"
    RECOVERY_READINESS = "RECOVERY_READINESS"
    DEGRADATION_PLANNING = "DEGRADATION_PLANNING"
    GOVERNANCE_EVALUATION = "GOVERNANCE_EVALUATION"
    REQUIRES_APPROVAL = "REQUIRES_APPROVAL"
    APPROVED = "APPROVED"
    DELEGATION_CREATED = "DELEGATION_CREATED"
    OUTCOME_VERIFICATION = "OUTCOME_VERIFICATION"
    RELIABILITY_REASSESSMENT = "RELIABILITY_REASSESSMENT"
    LEARNING = "LEARNING"
    CLOSED = "CLOSED"
    # Terminal / error states
    RESOLVED = "RESOLVED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    BLOCKED = "BLOCKED"
    ESCALATED = "ESCALATED"


class ServiceHealthStatus(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class ServiceHealthDimension(str, Enum):
    AVAILABILITY = "AVAILABILITY"
    LATENCY = "LATENCY"
    ERROR_RATE = "ERROR_RATE"
    THROUGHPUT = "THROUGHPUT"
    DEPENDENCY = "DEPENDENCY"
    CAPACITY = "CAPACITY"
    RESOURCE = "RESOURCE"
    SECURITY = "SECURITY"
    DATA = "DATA"
    MODEL = "MODEL"


class FailureClassification(str, Enum):
    TRANSIENT = "TRANSIENT"
    PERMANENT = "PERMANENT"
    INTERMITTENT = "INTERMITTENT"
    DEPENDENCY = "DEPENDENCY"
    CAPACITY = "CAPACITY"
    CONFIGURATION = "CONFIGURATION"
    SECURITY = "SECURITY"
    DATA = "DATA"
    MODEL = "MODEL"
    UNKNOWN = "UNKNOWN"


class ErrorBudgetStatus(str, Enum):
    HEALTHY = "HEALTHY"
    CONSUMING = "CONSUMING"
    AT_RISK = "AT_RISK"
    EXHAUSTED = "EXHAUSTED"
    UNKNOWN = "UNKNOWN"


class DegradationStrategy(str, Enum):
    GRACEFUL = "GRACEFUL"
    PARTIAL_SERVICE = "PARTIAL_SERVICE"
    READ_ONLY = "READ_ONLY"
    FEATURE_REDUCTION = "FEATURE_REDUCTION"
    LOAD_SHEDDING = "LOAD_SHEDDING"
    TRAFFIC_LIMITING = "TRAFFIC_LIMITING"
    FALLBACK = "FALLBACK"
    MANUAL = "MANUAL"
    DELEGATED = "DELEGATED"


class RecoveryStrategy(str, Enum):
    RETRY = "RETRY"
    FAILOVER = "FAILOVER"
    ROLLBACK = "ROLLBACK"
    RESTART = "RESTART"
    RESTORE = "RESTORE"
    REBUILD = "REBUILD"
    ISOLATE = "ISOLATE"
    MANUAL = "MANUAL"
    DELEGATED = "DELEGATED"


class GovernanceOutcome(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    ADVISORY_ONLY = "ADVISORY_ONLY"


class ReliabilityHumanReviewState(str, Enum):
    PENDING = "PENDING"
    IN_REVIEW = "IN_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ESCALATED = "ESCALATED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


@dataclass
class ServiceHealthAssessment:
    tenant_id: str
    service_id: str
    status: ServiceHealthStatus
    overall_score: float
    assessment_id: str = field(default_factory=lambda: f"sh_{uuid.uuid4().hex[:12]}")
    dimensions: Dict[str, float] = field(default_factory=dict)
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ReliabilityScore:
    overall_score: float
    availability_score: float
    resilience_score: float
    recoverability_score: float
    dependency_score: float
    capacity_score: float
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ReliabilityAssessment:
    tenant_id: str
    score: ReliabilityScore
    state: ReliabilityLifecycleState
    assessment_id: str = field(default_factory=lambda: f"rel_{uuid.uuid4().hex[:12]}")
    findings: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ServiceLevelObjective:
    slo_id: str
    tenant_id: str
    service_id: str
    target_percentage: float
    indicator_type: str  # AVAILABILITY, LATENCY, ERROR_RATE
    current_percentage: float = 99.9
    is_breached: bool = False


@dataclass
class ErrorBudget:
    slo_id: str
    tenant_id: str
    total_budget_minutes: float
    remaining_budget_minutes: float
    status: ErrorBudgetStatus
    burn_rate: float = 1.0


@dataclass
class FailurePrediction:
    tenant_id: str
    service_id: str
    predicted_failure_type: FailureClassification
    probability: float
    confidence: float
    prediction_id: str = field(default_factory=lambda: f"pred_{uuid.uuid4().hex[:12]}")
    evidence: List[str] = field(default_factory=list)
    explanation: str = ""
    horizon_minutes: int = 60
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class FailurePropagationPath:
    tenant_id: str
    origin_service: str
    affected_nodes: List[str]
    propagation_probability: float
    blast_radius_score: float
    path_id: str = field(default_factory=lambda: f"path_{uuid.uuid4().hex[:12]}")


@dataclass
class ResilienceAssessment:
    tenant_id: str
    service_id: str
    score: float
    redundancy_level: str
    circuit_breaker_active: bool
    assessment_id: str = field(default_factory=lambda: f"res_{uuid.uuid4().hex[:12]}")


@dataclass
class DegradationPlan:
    tenant_id: str
    service_id: str
    strategy: DegradationStrategy
    steps: List[Dict[str, Any]]
    plan_id: str = field(default_factory=lambda: f"deg_{uuid.uuid4().hex[:12]}")
    requires_approval: bool = True


@dataclass
class RecoveryPlan:
    tenant_id: str
    service_id: str
    strategy: RecoveryStrategy
    steps: List[Dict[str, Any]]
    plan_id: str = field(default_factory=lambda: f"rec_{uuid.uuid4().hex[:12]}")
    estimated_rto_minutes: float = 15.0


@dataclass
class ReliabilityRecommendation:
    tenant_id: str
    target_service: str
    action_description: str
    recommendation_id: str = field(default_factory=lambda: f"rec_{uuid.uuid4().hex[:12]}")
    priority: str = "HIGH"
    reason: str = "Predictive reliability optimization"
    confidence: float = 0.92
    auto_execute: bool = False  # Strictly False invariant
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ChaosExperimentProposal:
    tenant_id: str
    experiment_name: str
    target_service: str
    hypothesis: str
    proposal_id: str = field(default_factory=lambda: f"chaos_{uuid.uuid4().hex[:12]}")
    risk_level: str = "HIGH"
    requires_approval: bool = True
    auto_execute: bool = False


@dataclass
class ReliabilityEvidenceBundle:
    tenant_id: str
    assessment_id: str
    integrity_hash: str
    evidence_id: str = field(default_factory=lambda: f"ev_{uuid.uuid4().hex[:12]}")
    is_sealed: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def evidence_hash(self) -> str:
        return self.integrity_hash


@dataclass
class ReliabilitySnapshot:
    tenant_id: str
    assessment: ReliabilityAssessment
    snapshot_id: str = field(default_factory=lambda: f"snap_{uuid.uuid4().hex[:12]}")
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
