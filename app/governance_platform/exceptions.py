"""Governance Platform Domain Exceptions Hierarchy."""

from typing import Any, Dict, Optional

from app.core.exceptions import AppException


class GovernancePlatformException(AppException):
    """Base exception for all Governance Platform domain errors."""

    def __init__(self, message: str, code: str = "GOVERNANCE_ERROR", status_code: int = 400, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, code=code, status_code=status_code, details=details)


class PolicyViolationException(GovernancePlatformException):
    def __init__(self, policy_id: str, reason: str) -> None:
        super().__init__(message=f"Governance policy '{policy_id}' violated: {reason}", code="POLICY_VIOLATION", status_code=403)


class RiskExceededException(GovernancePlatformException):
    def __init__(self, score: float, threshold: float) -> None:
        super().__init__(message=f"Risk score {score:.1f} exceeds threshold {threshold:.1f}", code="RISK_EXCEEDED", status_code=422)


class ComplianceBreachException(GovernancePlatformException):
    def __init__(self, framework_id: str, control_id: str) -> None:
        super().__init__(message=f"Compliance control breach on '{framework_id}' ({control_id})", code="COMPLIANCE_BREACH", status_code=422)


class EvidenceNotFoundException(GovernancePlatformException):
    def __init__(self, evidence_id: str) -> None:
        super().__init__(message=f"Evidence record '{evidence_id}' not found", code="EVIDENCE_NOT_FOUND", status_code=404)
