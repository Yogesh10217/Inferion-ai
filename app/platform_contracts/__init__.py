"""Enterprise AI Platform Shared Contracts & Primitives Exports (Phase 5.30)."""

from app.platform_contracts.exceptions import (
    PlatformContractException,
    CrossTenantAccessException,
    ImmutableMutationException,
    IdempotencyConflictException,
    InvalidLifecycleTransitionException,
    CircularDependencyException,
    ContractVersionException,
)

from app.platform_contracts.versioning import (
    ContractVersion,
    ContractCompatibility,
    ContractVersionRange,
    ContractCompatibilityValidator,
)

from app.platform_contracts.tenant import (
    TenantScopedResource,
    TenantContext,
    TenantReference,
    TenantIsolationValidator,
    TenantAccessGuard,
)

from app.platform_contracts.immutability import (
    ImmutableResource,
    ImmutableResourceState,
    ImmutableResourceValidator,
)

from app.platform_contracts.fingerprinting import (
    Fingerprint,
    FingerprintAlgorithm,
    FingerprintGenerator,
    CanonicalSerializer,
    FingerprintValidationResult,
)

from app.platform_contracts.snapshots import (
    PlatformSnapshot,
    SnapshotReference,
    SnapshotVersion,
    SnapshotMetadata,
    SnapshotFactory,
    SnapshotValidator,
)

from app.platform_contracts.idempotency import (
    IdempotencyKey,
    IdempotencyRecord,
    IdempotencyStatus,
    IdempotencyManager,
)

from app.platform_contracts.redaction import (
    RedactionPolicy,
    RedactionRule,
    RedactionResult,
    SensitiveDataSanitizer,
)

from app.platform_contracts.evidence import (
    EvidenceReference,
    EvidenceMetadata,
    EvidenceIntegrity,
    EvidenceStrength,
    EvidenceSourceReference,
)

from app.platform_contracts.trust import (
    TrustAssessment,
    TrustDimension,
    TrustEvidence,
    TrustBand,
    TrustConfidence,
    TrustAssessmentVersion,
)

from app.platform_contracts.risk import (
    RiskReference,
    RiskAssessmentReference,
    RiskEvidenceReference,
)

from app.platform_contracts.governance import (
    GovernanceDecision,
    GovernanceDecisionStatus,
    GovernanceDecisionReason,
    PolicyReference,
)

from app.platform_contracts.approvals import (
    ApprovalReference,
    ApprovalRequirement,
    ApprovalStatusReference,
)

from app.platform_contracts.delegation import (
    DelegationRequest,
    DelegationTarget,
    DelegationStatus,
    DelegationResult,
    DelegationReference,
)

from app.platform_contracts.lifecycle import (
    LifecycleState,
    LifecycleTransition,
    LifecycleMachine,
)

from app.platform_contracts.adapters import (
    PlatformContractAdapter,
    TrustAssessmentAdapter,
    SnapshotAdapter,
    GovernanceDecisionAdapter,
    RiskReferenceAdapter,
    ApprovalReferenceAdapter,
    EvidenceReferenceAdapter,
    DelegationAdapter,
)

from app.platform_contracts.audit import (
    PlatformAuditEvent,
    AuditEventType,
    AuditReference,
    AuditActorReference,
    AuditResourceReference,
)

from app.platform_contracts.analytics import (
    PlatformReport,
    PlatformInsight,
    AnalyticsMetric,
    AnalyticsDimension,
    AnalyticsPeriod,
)

from app.platform_contracts.observability import (
    MetricNameValidator,
    SafeMetricLabelSanitizer,
)

from app.platform_contracts.validation import (
    CircularDependencyValidator,
    DependencyGraph,
)

from app.platform_contracts.repositories import (
    Repository,
    TenantScopedRepository,
    ImmutableRepository,
    VersionedRepository,
)

__all__ = [
    "PlatformContractException",
    "CrossTenantAccessException",
    "ImmutableMutationException",
    "IdempotencyConflictException",
    "InvalidLifecycleTransitionException",
    "CircularDependencyException",
    "ContractVersionException",
    "ContractVersion",
    "ContractCompatibility",
    "ContractVersionRange",
    "ContractCompatibilityValidator",
    "TenantScopedResource",
    "TenantContext",
    "TenantReference",
    "TenantIsolationValidator",
    "TenantAccessGuard",
    "ImmutableResource",
    "ImmutableResourceState",
    "ImmutableResourceValidator",
    "Fingerprint",
    "FingerprintAlgorithm",
    "FingerprintGenerator",
    "CanonicalSerializer",
    "FingerprintValidationResult",
    "PlatformSnapshot",
    "SnapshotReference",
    "SnapshotVersion",
    "SnapshotMetadata",
    "SnapshotFactory",
    "SnapshotValidator",
    "IdempotencyKey",
    "IdempotencyRecord",
    "IdempotencyStatus",
    "IdempotencyManager",
    "RedactionPolicy",
    "RedactionRule",
    "RedactionResult",
    "SensitiveDataSanitizer",
    "EvidenceReference",
    "EvidenceMetadata",
    "EvidenceIntegrity",
    "EvidenceStrength",
    "EvidenceSourceReference",
    "TrustAssessment",
    "TrustDimension",
    "TrustEvidence",
    "TrustBand",
    "TrustConfidence",
    "TrustAssessmentVersion",
    "RiskReference",
    "RiskAssessmentReference",
    "RiskEvidenceReference",
    "GovernanceDecision",
    "GovernanceDecisionStatus",
    "GovernanceDecisionReason",
    "PolicyReference",
    "ApprovalReference",
    "ApprovalRequirement",
    "ApprovalStatusReference",
    "DelegationRequest",
    "DelegationTarget",
    "DelegationStatus",
    "DelegationResult",
    "DelegationReference",
    "LifecycleState",
    "LifecycleTransition",
    "LifecycleMachine",
    "PlatformContractAdapter",
    "TrustAssessmentAdapter",
    "SnapshotAdapter",
    "GovernanceDecisionAdapter",
    "RiskReferenceAdapter",
    "ApprovalReferenceAdapter",
    "EvidenceReferenceAdapter",
    "DelegationAdapter",
    "PlatformAuditEvent",
    "AuditEventType",
    "AuditReference",
    "AuditActorReference",
    "AuditResourceReference",
    "PlatformReport",
    "PlatformInsight",
    "AnalyticsMetric",
    "AnalyticsDimension",
    "AnalyticsPeriod",
    "MetricNameValidator",
    "SafeMetricLabelSanitizer",
    "CircularDependencyValidator",
    "DependencyGraph",
    "Repository",
    "TenantScopedRepository",
    "ImmutableRepository",
    "VersionedRepository",
]
