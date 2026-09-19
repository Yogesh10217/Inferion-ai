"""Domain Exceptions for Enterprise AI Reliability Platform (Phase 5.31)."""

from app.platform_contracts.exceptions import CrossTenantAccessException, PlatformContractException


class ReliabilityPlatformException(PlatformContractException):
    """Base exception for all reliability platform errors."""

    def __init__(self, message: str, code: str = "RELIABILITY_ERROR"):
        super().__init__(message, code=code)


class ServiceNotFoundException(ReliabilityPlatformException):
    """Raised when a reliability service is not found."""

    def __init__(self, service_id: str):
        super().__init__(f"Reliability service '{service_id}' not found.", code="SERVICE_NOT_FOUND")


class SLONotFoundException(ReliabilityPlatformException):
    """Raised when an SLO definition is not found."""

    def __init__(self, slo_id: str):
        super().__init__(f"SLO definition '{slo_id}' not found.", code="SLO_NOT_FOUND")


class CrossTenantReliabilityAccessException(CrossTenantAccessException, ReliabilityPlatformException):
    """Raised on cross-tenant reliability access attempts."""

    def __init__(self, requester_tenant: str, owner_tenant: str):
        super().__init__(requester_tenant, owner_tenant)


class IncidentNotFoundException(ReliabilityPlatformException):
    """Raised when a reliability incident is not found."""

    def __init__(self, incident_id: str):
        super().__init__(f"Reliability incident '{incident_id}' not found.", code="INCIDENT_NOT_FOUND")


class RemediationException(ReliabilityPlatformException):
    """Raised when remediation execution or planning fails."""

    def __init__(self, message: str):
        super().__init__(message, code="REMEDIATION_ERROR")


class ImmutableReliabilityRecordException(ReliabilityPlatformException):
    """Raised when mutation is attempted on a closed incident timeline or finalized postmortem."""

    def __init__(self, record_id: str):
        super().__init__(
            f"Reliability record '{record_id}' is finalized and immutable.", code="IMMUTABLE_RECORD_MUTATION_DENIED"
        )


class SLOBreachException(ReliabilityPlatformException):
    """Raised when an SLO budget exhaustion threshold is breached."""

    def __init__(self, slo_id: str, current_error_budget: float):
        super().__init__(
            f"SLO '{slo_id}' error budget breached: remaining budget {current_error_budget}%.", code="SLO_BREACH"
        )
