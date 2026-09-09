"""Pure Python domain models for Runtime Intelligence (Phase 5.54)."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional
import uuid


class RuntimeLifecycleState(str, Enum):
    OBSERVING = "OBSERVING"
    SIGNAL_INGESTION = "SIGNAL_INGESTION"
    NORMALIZATION = "NORMALIZATION"
    CONTEXT_FUSION = "CONTEXT_FUSION"
    HEALTH_ANALYSIS = "HEALTH_ANALYSIS"
    ANOMALY_DETECTION = "ANOMALY_DETECTION"
    DRIFT_DETECTION = "DRIFT_DETECTION"
    DEGRADATION_ANALYSIS = "DEGRADATION_ANALYSIS"
    CORRELATION = "CORRELATION"
    CAUSAL_ANALYSIS = "CAUSAL_ANALYSIS"
    RISK_PROPAGATION = "RISK_PROPAGATION"
    RESILIENCE_ASSESSMENT = "RESILIENCE_ASSESSMENT"
    ADAPTIVE_ASSURANCE = "ADAPTIVE_ASSURANCE"
    RECOMMENDATION = "RECOMMENDATION"
    GOVERNANCE_EVALUATION = "GOVERNANCE_EVALUATION"
    REQUIRES_APPROVAL = "REQUIRES_APPROVAL"
    APPROVED = "APPROVED"
    DELEGATION_CREATED = "DELEGATION_CREATED"
    VERIFICATION = "VERIFICATION"
    CLOSED = "CLOSED"


class RuntimeHealthStatus(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNSTABLE = "UNSTABLE"
    AT_RISK = "AT_RISK"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


HealthStatus = RuntimeHealthStatus


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


class RuntimeDriftSeverity(str, Enum):
    NONE = "NONE"
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RuntimeAnomalySeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RuntimeSignalSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RuntimeSignalType(str, Enum):
    HEALTH = "HEALTH"
    PERFORMANCE = "PERFORMANCE"
    SECURITY = "SECURITY"
    IDENTITY = "IDENTITY"
    POLICY = "POLICY"
    CONTROL = "CONTROL"
    WORKFLOW = "WORKFLOW"
    MODEL = "MODEL"
    DATA = "DATA"
    KNOWLEDGE = "KNOWLEDGE"
    COST = "COST"
    CAPACITY = "CAPACITY"
    DEPENDENCY = "DEPENDENCY"
    LATENCY = "LATENCY"
    ERROR = "ERROR"
    AVAILABILITY = "AVAILABILITY"


class RuntimeGovernanceOutcome(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    ADVISORY_ONLY = "ADVISORY_ONLY"


class RuntimeHumanReviewState(str, Enum):
    PENDING = "PENDING"
    IN_REVIEW = "IN_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ESCALATED = "ESCALATED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


@dataclass
class RuntimeSignalMetadata:
    source_domain: str
    component_id: str
    environment: str = "production"
    version: str = "1.0.0"
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class RuntimeSignal:
    tenant_id: str
    signal_type: RuntimeSignalType
    severity: RuntimeSignalSeverity
    payload: Dict[str, Any]
    signal_id: str = field(default_factory=lambda: f"sig_{uuid.uuid4().hex[:12]}")
    metadata: Optional[RuntimeSignalMetadata] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class NormalizedRuntimeSignal:
    tenant_id: str
    signal_id: str
    normalized_type: str
    normalized_severity: str
    source_domain: str
    raw_payload: Dict[str, Any]
    fingerprint: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RuntimeContext:
    tenant_id: str
    signals: List[NormalizedRuntimeSignal]
    context_fingerprint: str
    bounded_window_minutes: int = 60
    context_id: str = field(default_factory=lambda: f"ctx_{uuid.uuid4().hex[:12]}")
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RuntimeHealthAssessment:
    tenant_id: str
    overall_status: RuntimeHealthStatus
    overall_score: float
    dimensions: Dict[str, float]
    subsystem: str = "global"
    assessment_id: str = field(default_factory=lambda: f"rh_{uuid.uuid4().hex[:12]}")
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def overall_health(self) -> RuntimeHealthStatus:
        return self.overall_status

    @property
    def status(self) -> RuntimeHealthStatus:
        return self.overall_status


@dataclass
class RuntimeAnomaly:
    tenant_id: str
    anomaly_type: str
    severity: RuntimeAnomalySeverity
    description: str
    metric_name: str
    observed_value: float
    expected_value: float
    anomaly_id: str = field(default_factory=lambda: f"anom_{uuid.uuid4().hex[:12]}")
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RuntimeDrift:
    tenant_id: str
    drift_type: str
    severity: RuntimeDriftSeverity
    expected_state: Dict[str, Any]
    actual_state: Dict[str, Any]
    difference_summary: str
    subsystem: str = "global"
    drift_score: float = 0.50
    drift_id: str = field(default_factory=lambda: f"drift_{uuid.uuid4().hex[:12]}")
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def drift_detected(self) -> bool:
        return self.severity != RuntimeDriftSeverity.NONE


@dataclass
class RuntimeBaseline:
    tenant_id: str
    metric_name: str
    expected_mean: float
    std_dev: float
    confidence_band_lower: float
    confidence_band_upper: float
    baseline_id: str = field(default_factory=lambda: f"base_{uuid.uuid4().hex[:12]}")
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RuntimeDegradation:
    tenant_id: str
    service_id: str
    degradation_type: str
    impact_score: float
    affected_features: List[str]
    degradation_id: str = field(default_factory=lambda: f"deg_{uuid.uuid4().hex[:12]}")
    degradation_trend: str = "DEGRADED"
    estimated_time_to_critical_seconds: float = 3600.0
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def analysis_id(self) -> str:
        return self.degradation_id


@dataclass
class RuntimeCorrelation:
    tenant_id: str
    correlation_type: str = "TELEMETRY_CORRELATION"
    primary_event_id: str = ""
    correlated_event_ids: List[str] = field(default_factory=list)
    correlation_coefficient: float = 0.85
    explanation: str = "Telemetry correlation analysis"
    subsystem: str = "global"
    observation_ids: List[str] = field(default_factory=list)
    correlation_score: float = 0.85
    correlation_id: str = field(default_factory=lambda: f"corr_{uuid.uuid4().hex[:12]}")
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RuntimeCausalHypothesis:
    tenant_id: str
    hypothesis_statement: str
    status: str  # HYPOTHESIZED, SUPPORTED, LIKELY, CONFIRMED, REJECTED
    confidence: float
    evidence_ids: List[str]
    explanation_notes: str
    hypothesis_id: str = field(default_factory=lambda: f"hypo_{uuid.uuid4().hex[:12]}")
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RuntimeRiskPropagationPath:
    tenant_id: str
    origin_component: str
    target_component: str
    propagation_chain: List[str]
    risk_score: float
    business_impact: str
    path_id: str = field(default_factory=lambda: f"rpath_{uuid.uuid4().hex[:12]}")


@dataclass
class RuntimeResilienceAssessment:
    tenant_id: str
    resilience_score: float
    recovery_capability: float
    redundancy_level: str
    rollback_available: bool
    assessment_id: str = field(default_factory=lambda: f"res_{uuid.uuid4().hex[:12]}")
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RecoveryOption:
    strategy_type: str  # RETRY, FAILOVER, ROLLBACK, COMPENSATE, DEGRADE_GRACEFULLY, MANUAL_INTERVENTION, DELEGATE
    description: str
    estimated_rto_seconds: int
    risk_level: str
    requires_approval: bool = True


@dataclass
class AdaptiveAssuranceScore:
    tenant_id: str
    assurance_score: float
    posture: str  # ASSURED, WATCH, DEGRADED, AT_RISK, CRITICAL
    component_scores: Dict[str, float]
    score_id: str = field(default_factory=lambda: f"aass_{uuid.uuid4().hex[:12]}")
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RuntimeRecommendation:
    tenant_id: str
    recommendation_type: str
    action_description: str
    recommendation_id: str = field(default_factory=lambda: f"rec_{uuid.uuid4().hex[:12]}")
    priority: str = "HIGH"
    reason: str = "Runtime adaptive optimization"
    confidence: float = 0.90
    auto_execute: bool = False  # Strictly False invariant
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RuntimeEvidenceBundle:
    tenant_id: str
    assessment_id: str
    integrity_hash: str
    evidence_id: str = field(default_factory=lambda: f"ev_{uuid.uuid4().hex[:12]}")
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
class RuntimeSnapshot:
    tenant_id: str
    health: RuntimeHealthAssessment
    snapshot_id: str = field(default_factory=lambda: f"snap_{uuid.uuid4().hex[:12]}")
    snapshot_fingerprint: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
