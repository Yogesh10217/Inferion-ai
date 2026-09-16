"""
Exceptions for Autonomous Planning Subsystem
"""


class PlanningException(Exception):
    """Base exception for all planning errors."""


class GoalPlanningError(PlanningException):
    """Raised when goal decomposition or planning fails."""


class DependencyResolutionError(PlanningException):
    """Raised when circular dependencies or unresolvable task graphs are detected."""


class ResourcePlanningError(PlanningException):
    """Raised when resource allocation or budget limits block planning."""


class PlanExecutionError(PlanningException):
    """Raised when execution of a plan step fails."""


class PlanValidationError(PlanningException):
    """Raised when plan schema or constraint validation fails."""


class SimulationError(PlanningException):
    """Raised when execution simulation fails."""
