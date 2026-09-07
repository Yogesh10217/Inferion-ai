"""
Custom exceptions for Phase 5.53 Enterprise AI Autonomous Assurance Orchestration Platform.
All exceptions are tenant-safe and avoid leaking sensitive metadata.
"""


class AutonomousAssuranceException(Exception):
    """Base exception for all autonomous assurance operations."""
    pass


class CrossTenantAutonomousAssuranceException(AutonomousAssuranceException):
    """Raised when cross-tenant access is attempted without authorization (Zero Metadata Leakage)."""
    pass


class AutonomousWorkflowNotFoundException(AutonomousAssuranceException):
    """Raised when a requested workflow is not found."""
    pass


class AutonomousPlanNotFoundException(AutonomousAssuranceException):
    """Raised when a requested plan is not found."""
    pass


class AutonomousStepNotFoundException(AutonomousAssuranceException):
    """Raised when a requested workflow step is not found."""
    pass


class WorkflowStateTransitionException(AutonomousAssuranceException):
    """Raised when an invalid workflow state transition is attempted."""
    pass


class WorkflowExecutionBlockedException(AutonomousAssuranceException):
    """Raised when workflow execution is blocked by policy, limits, or boundaries."""
    pass


class HighRiskAutonomousActionRequiresApprovalException(AutonomousAssuranceException):
    """Raised when a high-risk action requires human approval before delegation."""
    pass


class DelegationCoordinationException(AutonomousAssuranceException):
    """Raised when delegation request creation or coordination fails."""
    pass


class DelegationVerificationException(AutonomousAssuranceException):
    """Raised when post-delegation verification fails."""
    pass


class RecoveryPlanningException(AutonomousAssuranceException):
    """Raised when recovery planning fails."""
    pass


class CompensationPlanningException(AutonomousAssuranceException):
    """Raised when step compensation planning fails."""
    pass


class ImmutableAutonomousAssuranceRecordException(AutonomousAssuranceException):
    """Raised when attempting to modify an immutable evidence record or snapshot."""
    pass


class AutonomousAssuranceGovernanceException(AutonomousAssuranceException):
    """Raised when governance policy evaluation yields a denial."""
    pass


class WorkflowConcurrencyConflictException(AutonomousAssuranceException):
    """Raised when concurrent workflows attempt conflicting coordination on the same resource."""
    pass


class WorkflowLimitExceededException(AutonomousAssuranceException):
    """Raised when workflow budget or step limits are exceeded."""
    pass


class WorkflowBoundaryViolationException(AutonomousAssuranceException):
    """Raised when a workflow attempts a prohibited action boundary."""
    pass


InvalidWorkflowStateTransitionException = WorkflowStateTransitionException
ProhibitedAutonomousActionException = WorkflowBoundaryViolationException


class DependencyCycleException(AutonomousAssuranceException):
    """Raised when a cyclic step dependency is detected."""
    pass
