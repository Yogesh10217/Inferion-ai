"""Domain Exceptions for Enterprise AI Security Intelligence Platform (Phase 5.32)."""

from app.platform_contracts.exceptions import CrossTenantAccessException, PlatformContractException


class SecurityIntelligenceException(PlatformContractException):
    """Base exception for all security intelligence platform errors."""

    def __init__(self, message: str, code: str = "SECURITY_INTELLIGENCE_ERROR"):
        super().__init__(message, code=code)


class CrossTenantSecurityAccessException(CrossTenantAccessException, SecurityIntelligenceException):
    """Raised on unauthorized cross-tenant security access attempts."""

    def __init__(self, requester_tenant: str, owner_tenant: str):
        super().__init__(requester_tenant, owner_tenant)


class ImmutableSecurityRecordException(SecurityIntelligenceException):
    """Raised when mutation is attempted on a finalized security evidence bundle or investigation snapshot."""

    def __init__(self, record_id: str):
        super().__init__(
            f"Security record '{record_id}' is finalized and immutable.",
            code="IMMUTABLE_SECURITY_RECORD_MUTATION_DENIED",
        )


class SecurityThreatNotFoundException(SecurityIntelligenceException):
    """Raised when a security threat record is not found."""

    def __init__(self, threat_id: str):
        super().__init__(f"Security threat '{threat_id}' not found.", code="SECURITY_THREAT_NOT_FOUND")


class SecurityIncidentNotFoundException(SecurityIntelligenceException):
    """Raised when a security incident record is not found."""

    def __init__(self, incident_id: str):
        super().__init__(f"Security incident '{incident_id}' not found.", code="SECURITY_INCIDENT_NOT_FOUND")


class VulnerabilityNotFoundException(SecurityIntelligenceException):
    """Raised when a vulnerability record is not found."""

    def __init__(self, vuln_id: str):
        super().__init__(f"Vulnerability '{vuln_id}' not found.", code="VULNERABILITY_NOT_FOUND")


class AttackPathNotFoundException(SecurityIntelligenceException):
    """Raised when an attack path is not found."""

    def __init__(self, path_id: str):
        super().__init__(f"Attack path '{path_id}' not found.", code="ATTACK_PATH_NOT_FOUND")


class InvalidSecurityIncidentTransitionException(SecurityIntelligenceException):
    """Raised when an invalid security incident state transition is requested."""

    def __init__(self, current_status: str, target_status: str):
        super().__init__(
            f"Invalid security incident transition from '{current_status}' to '{target_status}'.",
            code="INVALID_SECURITY_INCIDENT_TRANSITION",
        )


class SecurityPolicyViolationException(SecurityIntelligenceException):
    """Raised when an action violates security policy constraints."""

    def __init__(self, message: str):
        super().__init__(message, code="SECURITY_POLICY_VIOLATION")


class SecurityRemediationBlockedException(SecurityIntelligenceException):
    """Raised when remediation execution is blocked by policy or missing approval."""

    def __init__(self, message: str):
        super().__init__(message, code="SECURITY_REMEDIATION_BLOCKED")


class SecurityEvidenceIntegrityException(SecurityIntelligenceException):
    """Raised when security evidence SHA-256 integrity verification fails."""

    def __init__(self, message: str):
        super().__init__(message, code="SECURITY_EVIDENCE_INTEGRITY_ERROR")


class SecuritySignalValidationException(SecurityIntelligenceException):
    """Raised when security signal validation fails."""

    def __init__(self, message: str):
        super().__init__(message, code="SECURITY_SIGNAL_VALIDATION_ERROR")


class HighRiskSecurityActionRequiresApprovalException(SecurityIntelligenceException):
    """Raised when high or critical risk remediation actions are executed without human approval."""

    def __init__(self, action_id: str):
        super().__init__(
            f"High-risk remediation action '{action_id}' requires explicit human approval.",
            code="HIGH_RISK_SECURITY_ACTION_APPROVAL_REQUIRED",
        )
