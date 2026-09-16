"""
Exceptions for Enterprise Multi-Agent Collaboration Subsystem
"""


class MultiAgentException(Exception):
    """Base exception for all multi-agent platform errors."""


class TeamNotFoundException(MultiAgentException):
    """Raised when a requested agent team is not found."""


class RolePermissionDenied(MultiAgentException):
    """Raised when an agent role lacks permissions for an operation."""


class DelegationError(MultiAgentException):
    """Raised when task delegation fails or no suitable agent matches."""


class HandoffError(MultiAgentException):
    """Raised when state handoff between agents fails."""


class ConsensusFailedError(MultiAgentException):
    """Raised when consensus agreement cannot be reached."""


class NegotiationFailedError(MultiAgentException):
    """Raised when multi-agent negotiation fails or deadlocks."""


class SupervisorEscalationError(MultiAgentException):
    """Raised when supervisor escalates execution failure for human approval."""

    def __init__(self, message: str, team_id: str, reason: str):
        super().__init__(message)
        self.team_id = team_id
        self.reason = reason


class BlackboardError(MultiAgentException):
    """Raised when blackboard operation fails or violates tenant boundary."""
