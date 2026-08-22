"""
Exceptions for Autonomous Planning Subsystem
"""

class PlanningException(Exception):
    """Base exception for all planning errors."""
    pass

class GoalPlanningError(PlanningException):
    """Raised when goal decomposition or planning fails."""
    pass

class DependencyResolutionError(PlanningException):
    """Raised when circular dependencies or unresolvable task graphs are detected."""
    pass

class ResourcePlanningError(PlanningException):
    """Raised when resource allocation or budget limits block planning."""
    pass

class PlanExecutionError(PlanningException):
    """Raised when execution of a plan step fails."""
    pass

class PlanValidationError(PlanningException):
    """Raised when plan schema or constraint validation fails."""
    pass

class SimulationError(PlanningException):
    """Raised when execution simulation fails."""
    pass
