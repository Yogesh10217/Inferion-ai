"""Tenant-safe exceptions for FinOps Intelligence Platform (Phase 5.42)."""


class FinOpsIntelligenceException(Exception):
    """Base exception for all FinOps Intelligence errors."""

    def __init__(self, message: str = "FinOps Intelligence error occurred.") -> None:
        super().__init__(message)
        self.message = message


class CrossTenantFinOpsIntelligenceException(FinOpsIntelligenceException):
    """Exception raised when a cross-tenant boundary violation occurs.

    MUST leak ZERO metadata:
    - no tenant ID
    - no resource existence
    - no cost amounts
    - no budget information
    - no usage information
    - no provider information
    - no optimization details
    """

    def __init__(self, message: str = "Access denied.") -> None:
        super().__init__("Access denied.")


class CostRecordNotFoundException(FinOpsIntelligenceException):
    """Raised when cost record is not found."""

    def __init__(self, record_id: str) -> None:
        super().__init__(f"Cost record '{record_id}' not found.")
        self.record_id = record_id


class BudgetNotFoundException(FinOpsIntelligenceException):
    """Raised when budget is not found."""

    def __init__(self, budget_id: str) -> None:
        super().__init__(f"Budget '{budget_id}' not found.")
        self.budget_id = budget_id


class AllocationNotFoundException(FinOpsIntelligenceException):
    """Raised when cost allocation is not found."""

    def __init__(self, allocation_id: str) -> None:
        super().__init__(f"Cost allocation '{allocation_id}' not found.")
        self.allocation_id = allocation_id


class OptimizationNotFoundException(FinOpsIntelligenceException):
    """Raised when optimization recommendation is not found."""

    def __init__(self, optimization_id: str) -> None:
        super().__init__(f"Optimization recommendation '{optimization_id}' not found.")
        self.optimization_id = optimization_id


class ForecastNotFoundException(FinOpsIntelligenceException):
    """Raised when forecast record is not found."""

    def __init__(self, forecast_id: str) -> None:
        super().__init__(f"Forecast record '{forecast_id}' not found.")
        self.forecast_id = forecast_id


class BudgetExceededException(FinOpsIntelligenceException):
    """Raised when hard budget limit is exceeded."""

    def __init__(self, budget_id: str, limit: float, current: float) -> None:
        super().__init__(f"Budget '{budget_id}' exceeded hard limit {limit} with current spend {current}.")
        self.budget_id = budget_id
        self.limit = limit
        self.current = current


class HighRiskOptimizationRequiresApprovalException(FinOpsIntelligenceException):
    """Raised when high-risk optimization action requires human approval."""

    def __init__(self, action_name: str, estimated_savings: float) -> None:
        super().__init__(
            f"High-risk optimization action '{action_name}' (estimated savings: ${estimated_savings}) requires human approval."
        )
        self.action_name = action_name
        self.estimated_savings = estimated_savings


class CostActionBlockedException(FinOpsIntelligenceException):
    """Raised when a financial action is blocked by governance policy."""

    def __init__(self, action_name: str, reason: str) -> None:
        super().__init__(f"Financial action '{action_name}' blocked: {reason}")
        self.action_name = action_name
        self.reason = reason


class FinancialGovernanceException(FinOpsIntelligenceException):
    """Raised when financial governance evaluation fails."""

    def __init__(self, reason: str) -> None:
        super().__init__(f"Financial governance error: {reason}")
        self.reason = reason


class ImmutableFinOpsRecordException(FinOpsIntelligenceException):
    """Raised when attempting to mutate an immutable finalized financial record."""

    def __init__(self, record_id: str) -> None:
        super().__init__(f"Financial record '{record_id}' is finalized and immutable.")
        self.record_id = record_id
