"""FinOps Domain Exceptions Hierarchy."""

from typing import Dict, Any, Optional
from app.core.exceptions import AppException


class FinOpsException(AppException):
    """Base exception for all FinOps domain errors."""

    def __init__(self, message: str, code: str = "FINOPS_ERROR", status_code: int = 400, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, code=code, status_code=status_code, details=details)


class BudgetExceededException(FinOpsException):
    def __init__(self, budget_id: str, limit: str, current_usage: str) -> None:
        super().__init__(
            message=f"Budget '{budget_id}' exceeded: Limit = ${limit}, Current Usage = ${current_usage}",
            code="BUDGET_EXCEEDED",
            status_code=429,
        )


class BudgetNotFoundException(FinOpsException):
    def __init__(self, budget_id: str) -> None:
        super().__init__(message=f"Budget '{budget_id}' not found", code="BUDGET_NOT_FOUND", status_code=404)


class CostLedgerException(FinOpsException):
    def __init__(self, message: str) -> None:
        super().__init__(message=message, code="COST_LEDGER_ERROR", status_code=400)


class OptimizationFailedException(FinOpsException):
    def __init__(self, recommendation_id: str, reason: str) -> None:
        super().__init__(message=f"Optimization '{recommendation_id}' failed: {reason}", code="OPTIMIZATION_FAILED", status_code=422)


class PricingNotFoundException(FinOpsException):
    def __init__(self, provider: str, model_id: str) -> None:
        super().__init__(message=f"Pricing for provider '{provider}' and model '{model_id}' not found", code="PRICING_NOT_FOUND", status_code=404)


class CapacityExceededException(FinOpsException):
    def __init__(self, resource: str, current: float, max_capacity: float) -> None:
        super().__init__(message=f"Capacity for '{resource}' exceeded: Current = {current}, Max = {max_capacity}", code="CAPACITY_EXCEEDED", status_code=429)
