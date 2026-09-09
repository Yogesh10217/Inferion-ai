"""Tenant-safe exception hierarchy for Continuous Assurance (Phase 5.54)."""

class ContinuousAssuranceException(Exception):
    """Base exception for all Continuous Assurance operations."""
    def __init__(self, message: str = "Continuous assurance operation failed"):
        super().__init__(message)


class CrossTenantContinuousAssuranceException(ContinuousAssuranceException):
    """Raised when cross-tenant access is attempted. Exposes zero metadata."""
    def __init__(self, message: str = "Access denied"):
        super().__init__(message)


class ContinuousAssuranceRecordNotFoundException(ContinuousAssuranceException):
    """Raised when an assurance record is not found."""
    def __init__(self, record_id: str = "Record not found"):
        super().__init__(f"Assurance record not found: {record_id}")


class RuntimeObservationNotFoundException(ContinuousAssuranceException):
    """Raised when a runtime observation is not found."""
    def __init__(self, obs_id: str = "Observation not found"):
        super().__init__(f"Runtime observation not found: {obs_id}")


class AssuranceEvaluationNotFoundException(ContinuousAssuranceException):
    """Raised when an assurance evaluation is not found."""
    def __init__(self, eval_id: str = "Evaluation not found"):
        super().__init__(f"Assurance evaluation not found: {eval_id}")


class ControlEffectivenessNotFoundException(ContinuousAssuranceException):
    """Raised when control effectiveness assessment is not found."""
    def __init__(self, ctrl_id: str = "Control assessment not found"):
        super().__init__(f"Control effectiveness assessment not found: {ctrl_id}")


class AssuranceDriftNotFoundException(ContinuousAssuranceException):
    """Raised when a drift record is not found."""
    def __init__(self, drift_id: str = "Drift record not found"):
        super().__init__(f"Assurance drift record not found: {drift_id}")


class PolicyDriftException(ContinuousAssuranceException):
    """Raised when policy drift detection fails."""
    pass


class RiskDriftException(ContinuousAssuranceException):
    """Raised when risk drift detection fails."""
    pass


class TrustDriftException(ContinuousAssuranceException):
    """Raised when trust drift detection fails."""
    pass


class ControlDriftException(ContinuousAssuranceException):
    """Raised when control drift detection fails."""
    pass


class VerificationFailureException(ContinuousAssuranceException):
    """Raised when continuous verification fails."""
    pass


class AdaptiveControlException(ContinuousAssuranceException):
    """Raised when an adaptive control operation fails."""
    pass


class ContinuousAssuranceGovernanceException(ContinuousAssuranceException):
    """Raised when governance evaluation blocks an action."""
    pass


class HighRiskContinuousAssuranceActionRequiresApprovalException(ContinuousAssuranceGovernanceException):
    """Raised when a high-risk adaptive action requires human approval."""
    def __init__(self, action_id: str = "Action requires human approval"):
        super().__init__(f"High-risk continuous assurance action requires approval: {action_id}")


class ImmutableContinuousAssuranceRecordException(ContinuousAssuranceException):
    """Raised when an attempt is made to modify a sealed, immutable assurance record."""
    def __init__(self, record_id: str = "Record is immutable"):
        super().__init__(f"Cannot modify immutable assurance record: {record_id}")


class RuntimeMonitoringException(ContinuousAssuranceException):
    """Raised when runtime monitoring fails."""
    pass


class FeedbackLoopException(ContinuousAssuranceException):
    """Raised when feedback loop bounds or execution parameters are violated."""
    pass


class InvalidContinuousAssuranceStateTransitionException(ContinuousAssuranceException):
    """Raised when an invalid state transition is attempted in the assurance lifecycle."""
    def __init__(self, current: str, target: str):
        super().__init__(f"Invalid continuous assurance state transition from '{current}' to '{target}'")
