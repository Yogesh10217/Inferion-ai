"""Custom exceptions for Enterprise AI Security Intelligence & Continuous Security Assurance Platform."""


class SecurityAssuranceException(Exception):
    """Base exception for all security assurance operations."""


class CrossTenantSecurityAssuranceException(SecurityAssuranceException):
    """Raised when cross-tenant access is attempted without authorization."""


class SecurityAssetNotFoundException(SecurityAssuranceException):
    """Raised when a security asset is not found."""


class SecurityThreatNotFoundException(SecurityAssuranceException):
    """Raised when a security threat is not found."""


class SecurityVulnerabilityNotFoundException(SecurityAssuranceException):
    """Raised when a vulnerability is not found."""


class SecurityIncidentNotFoundException(SecurityAssuranceException):
    """Raised when a security incident is not found."""


class SecurityInvestigationNotFoundException(SecurityAssuranceException):
    """Raised when a security investigation is not found."""


class HighRiskSecurityActionRequiresApprovalException(SecurityAssuranceException):
    """Raised when a high-risk security action requires human approval before execution."""


class ImmutableSecurityRecordException(SecurityAssuranceException):
    """Raised when attempting to modify an immutable evidence record or snapshot."""


class SecretsExposureException(SecurityAssuranceException):
    """Raised when raw secret material is detected in payload or logs."""


class InvalidSecurityPayloadException(SecurityAssuranceException):
    """Raised when a security payload is malformed or invalid."""
