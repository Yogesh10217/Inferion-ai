"""Pure Python domain models for Continuous Assurance (Phase 5.54)."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional
import uuid


class RuntimeObservationType(str, Enum):
    SECURITY_EVENT = "SECURITY_EVENT"
    IDENTITY_EVENT = "IDENTITY_EVENT"
    POLICY_EVENT = "POLICY_EVENT"
    CONTROL_EVENT = "CONTROL_EVENT"
    RISK_EVENT = "RISK_EVENT"
    TRUST_EVENT = "TRUST_EVENT"
    OPERATIONAL_EVENT = "OPERATIONAL_EVENT"
    DECISION_EVENT = "DECISION_EVENT"
    WORKFLOW_EVENT = "WORKFLOW_EVENT"
    DELEGATION_EVENT = "DELEGATION_EVENT"
    VERIFICATION_EVENT = "VERIFICATION_EVENT"


class RuntimeObservationSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RuntimeObservationStatus(str, Enum):
    UNPROCESSED = "UNPROCESSED"
    NORMALIZED = "NORMALIZED"
    EVALUATED = "EVALUATED"
    ARCHIVED = "ARCHIVED"


class AssuranceLifecycleState(str, Enum):
    INITIALIZING = "INITIALIZING"
    MONITORING = "MONITORING"
    STABLE = "STABLE"
    DEGRADED = "DEGRADED"
    AT_RISK = "AT_RISK"
    CRITICAL = "CRITICAL"
    RECOVERING = "RECOVERING"
    VERIFYING = "VERIFYING"
    RESTORED = "RESTORED"
    CLOSED = "CLOSED"


class ControlEffectivenessStatus(str, Enum):
    EFFECTIVE = "EFFECTIVE"
    PARTIALLY_EFFECTIVE = "PARTIALLY_EFFECTIVE"
    INEFFECTIVE = "INEFFECTIVE"
    DEGRADED = "DEGRADED"
    UNKNOWN = "UNKNOWN"


class DriftType(str, Enum):
    POLICY = "POLICY"
    RISK = "RISK"
    TRUST = "TRUST"
    CONTROL = "CONTROL"
    ASSURANCE = "ASSURANCE"
    CONFIGURATION = "CONFIGURATION"
    BEHAVIOR = "BEHAVIOR"
    RUNTIME = "RUNTIME"


class DriftSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DriftStatus(str, Enum):
    DETECTED = "DETECTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    REMEDIATING = "REMEDIATING"
    RESOLVED = "RESOLVED"
    IGNORED = "IGNORED"


class VerificationStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    VERIFIED = "VERIFIED"
    PARTIALLY_VERIFIED = "PARTIALLY_VERIFIED"
    FAILED = "FAILED"
    INCONCLUSIVE = "INCONCLUSIVE"
    BLOCKED = "BLOCKED"


class GovernanceDecisionOutcome(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    ADVISORY_ONLY = "ADVISORY_ONLY"


class HumanReviewState(str, Enum):
    PENDING = "PENDING"
    IN_REVIEW = "IN_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ESCALATED = "ESCALATED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


@dataclass
class RuntimeObservation:
    tenant_id: str
    source_domain: str
    observation_type: RuntimeObservationType
    severity: RuntimeObservationSeverity
    payload: Dict[str, Any]
    observation_id: str = field(default_factory=lambda: f"obs_{uuid.uuid4().hex[:12]}")
    status: RuntimeObservationStatus = RuntimeObservationStatus.UNPROCESSED
    observed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class NormalizedRuntimeObservation:
    observation_id: str
    tenant_id: str
    source_domain: str
    normalized_type: str
    severity: str
    clean_payload: Dict[str, Any]
    confidence: float = 1.0
    normalized_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ContinuousAssuranceScore:
    overall_score: float
    security_score: float
    identity_score: float
    operations_score: float
    policy_score: float
    control_score: float
    risk_score: float
    trust_score: float
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ContinuousAssuranceAssessment:
    tenant_id: str
    score: ContinuousAssuranceScore
    state: AssuranceLifecycleState
    assessment_id: str = field(default_factory=lambda: f"ass_{uuid.uuid4().hex[:12]}")
    findings: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ControlEffectivenessAssessment:
    tenant_id: str
    control_id: str
    status: ControlEffectivenessStatus
    score: float
    assessment_id: str = field(default_factory=lambda: f"ctrl_{uuid.uuid4().hex[:12]}")
    evidence_references: List[str] = field(default_factory=list)
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class AssuranceDrift:
    tenant_id: str
    drift_type: DriftType
    severity: DriftSeverity
    expected_state: Dict[str, Any]
    observed_state: Dict[str, Any]
    difference_summary: str
    drift_id: str = field(default_factory=lambda: f"drift_{uuid.uuid4().hex[:12]}")
    confidence: float = 0.95
    status: DriftStatus = DriftStatus.DETECTED
    evidence_references: List[str] = field(default_factory=list)
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ContinuousVerificationResult:
    tenant_id: str
    target_resource_id: str
    status: VerificationStatus
    verification_id: str = field(default_factory=lambda: f"ver_{uuid.uuid4().hex[:12]}")
    expected_hash: str = ""
    observed_hash: str = ""
    verification_details: Dict[str, Any] = field(default_factory=dict)
    verified_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class AdaptiveControlRecommendation:
    tenant_id: str
    target_control: str
    action_description: str
    recommendation_id: str = field(default_factory=lambda: f"rec_{uuid.uuid4().hex[:12]}")
    priority: str = "HIGH"
    reason: str = "Control effectiveness degraded"
    confidence: float = 0.90
    risk_level: str = "MEDIUM"
    auto_execute: bool = False  # Strictly False invariant
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ContinuousAssuranceRemediationPlan:
    tenant_id: str
    drift_id: str
    steps: List[Dict[str, Any]]
    plan_id: str = field(default_factory=lambda: f"rem_{uuid.uuid4().hex[:12]}")
    status: str = "PROPOSED"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ContinuousAssuranceEvidenceBundle:
    tenant_id: str
    observation_ids: List[str]
    assessment_id: str
    integrity_hash: str
    evidence_id: str = field(default_factory=lambda: f"ev_{uuid.uuid4().hex[:12]}")
    is_sealed: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ContinuousAssuranceSnapshot:
    tenant_id: str
    assessment: ContinuousAssuranceAssessment
    drift_events: List[AssuranceDrift]
    snapshot_id: str = field(default_factory=lambda: f"snap_{uuid.uuid4().hex[:12]}")
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
