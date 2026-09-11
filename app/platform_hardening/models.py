"""
Pure Python domain models for Platform Hardening, Audits & Certification.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class PlatformAuditSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class PlatformAuditStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class IntegrationHealthStatus(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
    UNKNOWN = "UNKNOWN"


class StubClassification(str, Enum):
    LEGITIMATE = "LEGITIMATE"
    TEST_ONLY = "TEST_ONLY"
    ABSTRACT = "ABSTRACT"
    OPTIONAL = "OPTIONAL"
    DEAD = "DEAD"
    PRODUCTION_STUB = "PRODUCTION_STUB"


class DeadCodeClassification(str, Enum):
    CONFIRMED_DEAD = "CONFIRMED_DEAD"
    LIKELY_DEAD = "LIKELY_DEAD"
    DYNAMICALLY_REFERENCED = "DYNAMICALLY_REFERENCED"
    TEST_ONLY = "TEST_ONLY"
    UNCERTAIN = "UNCERTAIN"


class PlatformCertificationStatus(str, Enum):
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    PARTIAL = "PARTIAL"
    CERTIFIED = "CERTIFIED"
    PRODUCTION_READY = "PRODUCTION_READY"


class ReleaseReadinessDecision(str, Enum):
    APPROVED = "APPROVED"
    CONDITIONALLY_APPROVED = "CONDITIONALLY_APPROVED"
    BLOCKED = "BLOCKED"


class CausalRelationshipStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    HYPOTHESIZED = "HYPOTHESIZED"
    SUPPORTED = "SUPPORTED"
    LIKELY = "LIKELY"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"


@dataclass
class PlatformAuditFinding:
    finding_id: str
    tenant_id: str
    rule_id: str
    title: str
    description: str
    severity: PlatformAuditSeverity
    subsystem: str
    affected_component: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    root_cause_hypothesis: Optional[str] = None
    remediation_suggestion: Optional[str] = None
    evidence_reference: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SubsystemIntegrationStatus:
    subsystem_name: str
    phase: str
    status: IntegrationHealthStatus
    provider_name: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)
    sdk_available: bool = True
    cli_available: bool = True
    api_route: Optional[str] = None
    health_score: float = 100.0
    error_message: Optional[str] = None


@dataclass
class ProviderIntegrationStatus:
    provider_id: str
    subsystem_name: str
    is_registered: bool
    is_healthy: bool
    response_time_ms: float
    timeout_protected: bool
    exception_isolated: bool
    contract_valid: bool
    confidence_degraded: bool = False
    freshness_seconds: float = 0.0
    error_detail: Optional[str] = None


@dataclass
class EngineConnectionStatus:
    engine_name: str
    subsystem_name: str
    is_instantiated: bool
    is_called: bool
    is_connected_to_pipeline: bool
    manager_bypass_detected: bool = False
    direct_repository_access_detected: bool = False
    status_label: str = "CONNECTED"  # CONNECTED, DEAD, UNUSED, BYPASSED


@dataclass
class TracePropagationResult:
    is_valid: bool
    trace_id: str
    phases_visited: List[str]
    trace_lost: bool = False
    trace_mutated: bool = False
    trace_collision: bool = False
    trace_leakage: bool = False
    broken_causation: bool = False
    broken_correlation: bool = False
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContextPropagationResult:
    is_valid: bool
    tenant_id_preserved: bool
    trace_id_preserved: bool
    correlation_id_preserved: bool
    causation_id_preserved: bool
    confidence_preserved: bool
    evidence_reference_preserved: bool
    missing_fields: List[str] = field(default_factory=list)


@dataclass
class LineageValidationResult:
    is_valid: bool
    edges_validated: int
    missing_parents: List[str] = field(default_factory=list)
    missing_children: List[str] = field(default_factory=list)
    orphans: List[str] = field(default_factory=list)
    cycles_detected: List[List[str]] = field(default_factory=list)


@dataclass
class GovernanceValidationResult:
    is_valid: bool
    gates_tested: List[str] = field(default_factory=list)
    approval_bypasses_detected: int = 0
    high_risk_gates_enforced: bool = True
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DelegationValidationResult:
    is_valid: bool
    auto_execute_false_enforced: bool = True
    direct_executions_detected: int = 0
    cross_tenant_delegations_detected: int = 0
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VerificationValidationResult:
    is_valid: bool
    closed_loop_verified: bool
    feedback_returned_to_assurance: bool
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RepositoryValidationResult:
    is_valid: bool
    tenant_isolation_verified: bool
    thread_safety_verified: bool
    cross_tenant_access_blocked: bool
    leaks_detected: int = 0


@dataclass
class ConcurrencyValidationResult:
    is_valid: bool
    concurrent_requests_tested: int
    race_conditions_detected: int = 0
    deadlocks_detected: int = 0
    lost_updates_detected: int = 0


@dataclass
class IdempotencyValidationResult:
    is_valid: bool
    repeated_requests_tested: int
    duplicate_executions_prevented: int
    idempotency_key_collisions: int = 0


@dataclass
class StubDetectionResult:
    total_files_scanned: int
    findings: List[PlatformAuditFinding] = field(default_factory=list)
    unclassified_stubs_count: int = 0
    classifications: Dict[str, int] = field(default_factory=dict)


@dataclass
class DeadCodeDetectionResult:
    total_symbols_analyzed: int
    findings: List[PlatformAuditFinding] = field(default_factory=list)
    classifications: Dict[str, int] = field(default_factory=dict)


@dataclass
class DuplicateDetectionResult:
    duplicates_found: int
    findings: List[PlatformAuditFinding] = field(default_factory=list)


@dataclass
class DependencyValidationResult:
    is_valid: bool
    circular_dependencies: List[List[str]] = field(default_factory=list)
    prohibited_imports: List[str] = field(default_factory=list)
    findings: List[PlatformAuditFinding] = field(default_factory=list)


@dataclass
class APIContractValidationResult:
    is_valid: bool
    rest_endpoints_count: int
    python_sdk_methods_count: int
    ts_sdk_methods_count: int
    go_sdk_methods_count: int
    java_sdk_methods_count: int
    cli_commands_count: int
    unmapped_endpoints: List[str] = field(default_factory=list)
    findings: List[PlatformAuditFinding] = field(default_factory=list)


@dataclass
class RemediationRecommendation:
    remediation_id: str
    tenant_id: str
    finding_id: str
    severity: PlatformAuditSeverity
    subsystem: str
    affected_component: str
    root_cause_hypothesis: str
    recommendation: str
    risk: str
    priority: str  # P0, P1, P2, P3
    requires_approval: bool = True
    auto_execute: bool = False  # Mandatory Invariant 6: ALWAYS False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ReleaseGateResult:
    decision: ReleaseReadinessDecision
    blocking_p0_count: int
    cross_tenant_leak_detected: bool
    direct_infra_mutation_detected: bool
    approval_bypass_detected: bool
    broken_evidence_chain_detected: bool
    reason: str
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class CertificationEvidence:
    evidence_id: str
    tenant_id: str
    audit_id: str
    sha256_hash: str
    previous_hash: Optional[str]
    sealed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_valid: bool = True


@dataclass
class PlatformCertification:
    certification_id: str
    tenant_id: str
    status: PlatformCertificationStatus
    release_decision: ReleaseReadinessDecision
    overall_score: float
    evidence: CertificationEvidence
    audited_phases_count: int = 8
    certified_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PlatformAuditResult:
    audit_id: str
    tenant_id: str
    status: PlatformAuditStatus
    findings: List[PlatformAuditFinding] = field(default_factory=list)
    remediations: List[RemediationRecommendation] = field(default_factory=list)
    certification: Optional[PlatformCertification] = None
    release_gate: Optional[ReleaseGateResult] = None
    readiness_score: float = 0.0
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None


@dataclass
class IntegrationHealth:
    subsystem_statuses: List[SubsystemIntegrationStatus]
    provider_statuses: List[ProviderIntegrationStatus]
    engine_statuses: List[EngineConnectionStatus]
    overall_health: IntegrationHealthStatus
    overall_health_score: float


@dataclass
class PlatformHealthSummary:
    tenant_id: str
    integration_health: IntegrationHealthStatus
    certification_status: PlatformCertificationStatus
    release_readiness: ReleaseReadinessDecision
    readiness_score: float
    total_findings: int
    critical_findings: int
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
