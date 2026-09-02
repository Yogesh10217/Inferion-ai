"""Tenant-safe exceptions for Operations Intelligence Platform (Phase 5.41)."""


class OperationsIntelligenceException(Exception):
    """Base exception for all Operations Intelligence errors."""
    def __init__(self, message: str = "Operations Intelligence error occurred.") -> None:
        super().__init__(message)
        self.message = message


class CrossTenantOperationsAccessException(OperationsIntelligenceException):
    """Exception raised when a cross-tenant boundary violation occurs.
    
    MUST leak ZERO metadata:
    - no tenant ID
    - no resource existence
    - no incident metadata
    - no infrastructure information
    - no service topology information
    """
    def __init__(self, message: str = "Access denied.") -> None:
        super().__init__("Access denied.")


class OperationalServiceNotFoundException(OperationsIntelligenceException):
    """Raised when operational service is not found."""
    def __init__(self, service_id: str) -> None:
        super().__init__(f"Operational service '{service_id}' not found.")
        self.service_id = service_id


class IncidentNotFoundException(OperationsIntelligenceException):
    """Raised when incident is not found."""
    def __init__(self, incident_id: str) -> None:
        super().__init__(f"Incident '{incident_id}' not found.")
        self.incident_id = incident_id


class ProblemNotFoundException(OperationsIntelligenceException):
    """Raised when problem record is not found."""
    def __init__(self, problem_id: str) -> None:
        super().__init__(f"Problem record '{problem_id}' not found.")
        self.problem_id = problem_id


class ChangeNotFoundException(OperationsIntelligenceException):
    """Raised when operational change is not found."""
    def __init__(self, change_id: str) -> None:
        super().__init__(f"Operational change '{change_id}' not found.")
        self.change_id = change_id


class MajorIncidentNotFoundException(OperationsIntelligenceException):
    """Raised when major incident is not found."""
    def __init__(self, major_incident_id: str) -> None:
        super().__init__(f"Major incident '{major_incident_id}' not found.")
        self.major_incident_id = major_incident_id


class OperationalActionBlockedException(OperationsIntelligenceException):
    """Raised when operational action is blocked by governance policy."""
    def __init__(self, action_name: str, reason: str) -> None:
        super().__init__(f"Operational action '{action_name}' blocked: {reason}")
        self.action_name = action_name
        self.reason = reason


class HighRiskOperationRequiresApprovalException(OperationsIntelligenceException):
    """Raised when high-risk operational action requires human approval."""
    def __init__(self, action_name: str, risk_score: float) -> None:
        super().__init__(f"High-risk operational action '{action_name}' (risk: {risk_score}) requires human approval.")
        self.action_name = action_name
        self.risk_score = risk_score


class RootCauseAnalysisException(OperationsIntelligenceException):
    """Raised when root cause analysis fails or is inconclusive."""
    def __init__(self, reason: str) -> None:
        super().__init__(f"Root cause analysis error: {reason}")
        self.reason = reason


class RemediationVerificationException(OperationsIntelligenceException):
    """Raised when remediation verification fails."""
    def __init__(self, remediation_id: str, reason: str) -> None:
        super().__init__(f"Remediation '{remediation_id}' verification failed: {reason}")
        self.remediation_id = remediation_id
        self.reason = reason


class InvalidAccessStateTransitionException(OperationsIntelligenceException):
    """Raised when an invalid state transition is attempted."""
    def __init__(self, current_state: str, target_state: str) -> None:
        super().__init__(f"Invalid state transition from '{current_state}' to '{target_state}'.")
        self.current_state = current_state
        self.target_state = target_state


class ImmutableOperationsRecordException(OperationsIntelligenceException):
    """Raised when attempting to mutate an immutable finalized operational record."""
    def __init__(self, record_id: str) -> None:
        super().__init__(f"Operational record '{record_id}' is finalized and immutable.")
        self.record_id = record_id
