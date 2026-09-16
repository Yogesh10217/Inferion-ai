"""
Custom exceptions for Phase 5.53 Enterprise AI Autonomous Assurance Orchestration Platform.
All exceptions are tenant-safe and avoid leaking sensitive metadata.
"""


class AutonomousAssuranceException(Exception):
    """Base exception for all autonomous assurance operations."""


class CrossTenantAutonomousAssuranceException(AutonomousAssuranceException):
    """Raised when cross-tenant access is attempted without authorization (Zero Metadata Leakage)."""


class AutonomousWorkflowNotFoundException(AutonomousAssuranceException):
    """Raised when a requested workflow is not found."""


class AutonomousPlanNotFoundException(AutonomousAssuranceException):
    """Raised when a requested plan is not found."""


class AutonomousStepNotFoundException(AutonomousAssuranceException):
    """Raised when a requested workflow step is not found."""


class WorkflowStateTransitionException(AutonomousAssuranceException):
    """Raised when an invalid workflow state transition is attempted."""


class WorkflowExecutionBlockedException(AutonomousAssuranceException):
    """Raised when workflow execution is blocked by policy, limits, or boundaries."""


class HighRiskAutonomousActionRequiresApprovalException(AutonomousAssuranceException):
    """Raised when a high-risk action requires human approval before delegation."""


class DelegationCoordinationException(AutonomousAssuranceException):
    """Raised when delegation request creation or coordination fails."""


class DelegationVerificationException(AutonomousAssuranceException):
    """Raised when post-delegation verification fails."""


class RecoveryPlanningException(AutonomousAssuranceException):
    """Raised when recovery planning fails."""


class CompensationPlanningException(AutonomousAssuranceException):
    """Raised when step compensation planning fails."""


class ImmutableAutonomousAssuranceRecordException(AutonomousAssuranceException):
    """Raised when attempting to modify an immutable evidence record or snapshot."""


class AutonomousAssuranceGovernanceException(AutonomousAssuranceException):
    """Raised when governance policy evaluation yields a denial."""


class WorkflowConcurrencyConflictException(AutonomousAssuranceException):
    """Raised when concurrent workflows attempt conflicting coordination on the same resource."""


class WorkflowLimitExceededException(AutonomousAssuranceException):
    """Raised when workflow budget or step limits are exceeded."""


class WorkflowBoundaryViolationException(AutonomousAssuranceException):
    """Raised when a workflow attempts a prohibited action boundary."""


InvalidWorkflowStateTransitionException = WorkflowStateTransitionException
ProhibitedAutonomousActionException = WorkflowBoundaryViolationException


class DependencyCycleException(AutonomousAssuranceException):
    """Raised when a cyclic step dependency is detected."""
