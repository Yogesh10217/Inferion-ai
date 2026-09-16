"""Tenant-safe exceptions for Access Intelligence Platform (Phase 5.39)."""


class AccessIntelligenceException(Exception):
    """Base exception for all Access Intelligence errors."""

    def __init__(self, message: str = "Access Intelligence error occurred.") -> None:
        super().__init__(message)
        self.message = message


class CrossTenantAccessIntelligenceException(AccessIntelligenceException):
    """Exception raised when a cross-tenant boundary violation occurs.

    MUST leak ZERO metadata:
    - no resource existence
    - no tenant identifier
    - no resource metadata
    - no access graph details
    """

    def __init__(self, message: str = "Access denied.") -> None:
        super().__init__("Access denied.")


class IdentityNotFoundException(AccessIntelligenceException):
    """Raised when identity is not found."""

    def __init__(self, identity_id: str) -> None:
        super().__init__(f"Identity '{identity_id}' not found.")
        self.identity_id = identity_id


class AccessRelationshipNotFoundException(AccessIntelligenceException):
    """Raised when relationship is not found."""

    def __init__(self, relationship_id: str) -> None:
        super().__init__(f"Access relationship '{relationship_id}' not found.")
        self.relationship_id = relationship_id


class EntitlementNotFoundException(AccessIntelligenceException):
    """Raised when entitlement is not found."""

    def __init__(self, entitlement_id: str) -> None:
        super().__init__(f"Entitlement '{entitlement_id}' not found.")
        self.entitlement_id = entitlement_id


class PrivilegedAccessNotFoundException(AccessIntelligenceException):
    """Raised when privileged access request is not found."""

    def __init__(self, request_id: str) -> None:
        super().__init__(f"Privileged access request '{request_id}' not found.")
        self.request_id = request_id


class AccessReviewNotFoundException(AccessIntelligenceException):
    """Raised when access review is not found."""

    def __init__(self, review_id: str) -> None:
        super().__init__(f"Access review '{review_id}' not found.")
        self.review_id = review_id


class AccessCertificationNotFoundException(AccessIntelligenceException):
    """Raised when access certification is not found."""

    def __init__(self, certification_id: str) -> None:
        super().__init__(f"Access certification '{certification_id}' not found.")
        self.certification_id = certification_id


class InvalidAccessStateTransitionException(AccessIntelligenceException):
    """Raised when an invalid lifecycle state transition is attempted."""

    def __init__(self, current_state: str, target_state: str) -> None:
        super().__init__(f"Invalid state transition from '{current_state}' to '{target_state}'.")
        self.current_state = current_state
        self.target_state = target_state


class AccessPolicyViolationException(AccessIntelligenceException):
    """Raised when access policy is violated."""

    def __init__(self, policy_id: str, reason: str) -> None:
        super().__init__(f"Access policy '{policy_id}' violated: {reason}")
        self.policy_id = policy_id
        self.reason = reason


class PrivilegedActionBlockedException(AccessIntelligenceException):
    """Raised when a privileged action is blocked by governance."""

    def __init__(self, action: str, reason: str) -> None:
        super().__init__(f"Privileged action '{action}' blocked: {reason}")
        self.action = action
        self.reason = reason


class AccessRiskThresholdExceededException(AccessIntelligenceException):
    """Raised when access risk score exceeds threshold."""

    def __init__(self, score: float, threshold: float) -> None:
        super().__init__(f"Access risk score {score} exceeded threshold {threshold}.")
        self.score = score
        self.threshold = threshold


class ImmutableAccessRecordException(AccessIntelligenceException):
    """Raised when attempting to mutate an immutable access record."""

    def __init__(self, record_id: str) -> None:
        super().__init__(f"Access record '{record_id}' is finalized and immutable.")
        self.record_id = record_id


class AccessEvidenceIntegrityException(AccessIntelligenceException):
    """Raised when evidence verification fails."""

    def __init__(self, bundle_id: str, reason: str) -> None:
        super().__init__(f"Evidence bundle '{bundle_id}' integrity check failed: {reason}")
        self.bundle_id = bundle_id
        self.reason = reason


class AccessDelegationBlockedException(AccessIntelligenceException):
    """Raised when delegation request generation fails or is blocked."""

    def __init__(self, reason: str) -> None:
        super().__init__(f"Access delegation blocked: {reason}")
        self.reason = reason


class HighRiskAccessRequiresApprovalException(AccessIntelligenceException):
    """Raised when a high-risk access request requires explicit human approval."""

    def __init__(self, request_id: str, risk_score: float) -> None:
        super().__init__(f"High-risk access request '{request_id}' (risk: {risk_score}) requires human approval.")
        self.request_id = request_id
        self.risk_score = risk_score
