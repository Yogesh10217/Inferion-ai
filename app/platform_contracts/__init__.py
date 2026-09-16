"""Enterprise AI Platform Shared Contracts & Primitives Exports (Phase 5.30)."""

from app.platform_contracts.adapters import (
    ApprovalReferenceAdapter,
    DelegationAdapter,
    EvidenceReferenceAdapter,
    GovernanceDecisionAdapter,
    PlatformContractAdapter,
    RiskReferenceAdapter,
    SnapshotAdapter,
    TrustAssessmentAdapter,
)
from app.platform_contracts.analytics import (
    AnalyticsDimension,
    AnalyticsMetric,
    AnalyticsPeriod,
    PlatformInsight,
    PlatformReport,
)
from app.platform_contracts.approvals import (
    ApprovalReference,
    ApprovalRequirement,
    ApprovalStatusReference,
)
from app.platform_contracts.audit import (
    AuditActorReference,
    AuditEventType,
    AuditReference,
    AuditResourceReference,
    PlatformAuditEvent,
)
from app.platform_contracts.delegation import (
    DelegationReference,
    DelegationRequest,
    DelegationResult,
    DelegationStatus,
    DelegationTarget,
)
from app.platform_contracts.evidence import (
    EvidenceIntegrity,
    EvidenceMetadata,
    EvidenceReference,
    EvidenceSourceReference,
    EvidenceStrength,
)
from app.platform_contracts.exceptions import (
    CircularDependencyException,
    ContractVersionException,
    CrossTenantAccessException,
    IdempotencyConflictException,
    ImmutableMutationException,
    InvalidLifecycleTransitionException,
    PlatformContractException,
)
from app.platform_contracts.fingerprinting import (
    CanonicalSerializer,
    Fingerprint,
    FingerprintAlgorithm,
    FingerprintGenerator,
    FingerprintValidationResult,
)
from app.platform_contracts.governance import (
    GovernanceDecision,
    GovernanceDecisionReason,
    GovernanceDecisionStatus,
    PolicyReference,
)
from app.platform_contracts.idempotency import (
    IdempotencyKey,
    IdempotencyManager,
    IdempotencyRecord,
    IdempotencyStatus,
)
from app.platform_contracts.immutability import (
    ImmutableResource,
    ImmutableResourceState,
    ImmutableResourceValidator,
)
from app.platform_contracts.lifecycle import (
    LifecycleMachine,
    LifecycleState,
    LifecycleTransition,
)
from app.platform_contracts.observability import (
    MetricNameValidator,
    SafeMetricLabelSanitizer,
)
from app.platform_contracts.redaction import (
    RedactionPolicy,
    RedactionResult,
    RedactionRule,
    SensitiveDataSanitizer,
)
from app.platform_contracts.repositories import (
    ImmutableRepository,
    Repository,
    TenantScopedRepository,
    VersionedRepository,
)
from app.platform_contracts.risk import (
    RiskAssessmentReference,
    RiskEvidenceReference,
    RiskReference,
)
from app.platform_contracts.snapshots import (
    PlatformSnapshot,
    SnapshotFactory,
    SnapshotMetadata,
    SnapshotReference,
    SnapshotValidator,
    SnapshotVersion,
)
from app.platform_contracts.tenant import (
    TenantAccessGuard,
    TenantContext,
    TenantIsolationValidator,
    TenantReference,
    TenantScopedResource,
)
from app.platform_contracts.trust import (
    TrustAssessment,
    TrustAssessmentVersion,
    TrustBand,
    TrustConfidence,
    TrustDimension,
    TrustEvidence,
)
from app.platform_contracts.validation import (
    CircularDependencyValidator,
    DependencyGraph,
)
from app.platform_contracts.versioning import (
    ContractCompatibility,
    ContractCompatibilityValidator,
    ContractVersion,
    ContractVersionRange,
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
