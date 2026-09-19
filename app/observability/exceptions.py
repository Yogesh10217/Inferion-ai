"""Domain exceptions for the Enterprise AI Observability subsystem."""

from app.core.exceptions import AppException

# Alias for backward compatibility
LLMEngineException = AppException


class ObservabilityException(AppException):
    """Base exception for all observability subsystem errors."""

    def __init__(
        self, message: str, status_code: int = 500, details: dict | None = None, code: str = "observability_error"
    ) -> None:
        super().__init__(status_code=status_code, code=code, message=message, details=details)


class TraceNotFoundException(ObservabilityException):
    """Raised when a requested trace ID cannot be found."""

    def __init__(self, trace_id: str) -> None:
        super().__init__(
            message=f"Trace with ID '{trace_id}' was not found.",
            status_code=404,
            code="trace_not_found",
            details={"trace_id": trace_id},
        )


class SpanNotFoundException(ObservabilityException):
    """Raised when a requested span ID cannot be found."""

    def __init__(self, span_id: str) -> None:
        super().__init__(
            message=f"Span with ID '{span_id}' was not found.",
            status_code=404,
            code="span_not_found",
            details={"span_id": span_id},
        )


class ExecutionNotFoundException(ObservabilityException):
    """Raised when a requested execution ID cannot be found."""

    def __init__(self, execution_id: str) -> None:
        super().__init__(
            message=f"Execution with ID '{execution_id}' was not found.",
            status_code=404,
            code="execution_not_found",
            details={"execution_id": execution_id},
        )


class ReplayNotAvailableException(ObservabilityException):
    """Raised when an execution cannot be replayed due to missing snapshot or restrictions."""

    def __init__(self, execution_id: str, reason: str) -> None:
        super().__init__(
            message=f"Replay for execution '{execution_id}' is not available: {reason}",
            status_code=400,
            code="replay_not_available",
            details={"execution_id": execution_id, "reason": reason},
        )


class MetricsCollectionException(ObservabilityException):
    """Raised when metrics collection or computation fails."""

    def __init__(self, reason: str) -> None:
        super().__init__(
            message=f"Metrics collection failed: {reason}",
            status_code=500,
            code="metrics_collection_failed",
            details={"reason": reason},
        )


class LogAggregationException(ObservabilityException):
    """Raised when log aggregation or query fails."""

    def __init__(self, reason: str) -> None:
        super().__init__(
            message=f"Log aggregation failed: {reason}",
            status_code=500,
            code="log_aggregation_failed",
            details={"reason": reason},
        )


class AlertConfigurationException(ObservabilityException):
    """Raised when an alert rule configuration is invalid."""

    def __init__(self, reason: str) -> None:
        super().__init__(
            message=f"Alert configuration error: {reason}",
            status_code=400,
            code="alert_configuration_error",
            details={"reason": reason},
        )


class AnomalyDetectionException(ObservabilityException):
    """Raised when anomaly detection processing fails."""

    def __init__(self, reason: str) -> None:
        super().__init__(
            message=f"Anomaly detection failed: {reason}",
            status_code=500,
            code="anomaly_detection_failed",
            details={"reason": reason},
        )


class SLAValidationException(ObservabilityException):
    """Raised when SLA/SLO definition or validation fails."""

    def __init__(self, reason: str) -> None:
        super().__init__(
            message=f"SLA validation error: {reason}",
            status_code=400,
            code="sla_validation_error",
            details={"reason": reason},
        )
