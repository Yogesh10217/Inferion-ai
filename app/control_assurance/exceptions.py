"""Enterprise AI Continuous Control Assurance Exceptions (Phase 5.38)."""

from app.platform_contracts.exceptions import (
    CrossTenantAccessException,
    ImmutableMutationException,
    InvalidLifecycleTransitionException,
    PlatformContractException,
)


class ControlAssuranceException(PlatformContractException):
    """Base exception for all Control Assurance domain errors."""

    def __init__(self, message: str, code: str = "CONTROL_ASSURANCE_ERROR"):
        super().__init__(message, code=code)


class CrossTenantControlAssuranceAccessException(CrossTenantAccessException):
    """Raised on cross-tenant access attempts in Control Assurance domain. Opaque error: zero metadata leaked."""

    def __init__(self, requested_tenant: str = "", owner_tenant: str = "") -> None:
        super().__init__(requested_tenant or "denied", owner_tenant or "denied")
        self.message = "Access denied or resource not found in tenant context."
        self.args = (self.message,)


class ControlNotFoundException(ControlAssuranceException):
    """Raised when requested control definition is not found."""

    def __init__(self, control_id: str):
        super().__init__(f"Control definition '{control_id}' not found.", code="CONTROL_NOT_FOUND")


class ControlEvaluationNotFoundException(ControlAssuranceException):
    """Raised when requested control evaluation is not found."""

    def __init__(self, evaluation_id: str):
        super().__init__(f"Control evaluation '{evaluation_id}' not found.", code="EVALUATION_NOT_FOUND")


class AssuranceViolationNotFoundException(ControlAssuranceException):
    """Raised when requested control violation is not found."""

    def __init__(self, violation_id: str):
        super().__init__(f"Control violation '{violation_id}' not found.", code="VIOLATION_NOT_FOUND")


class ControlEvidenceNotFoundException(ControlAssuranceException):
    """Raised when requested control evidence is not found."""

    def __init__(self, evidence_id: str):
        super().__init__(f"Control evidence '{evidence_id}' not found.", code="EVIDENCE_NOT_FOUND")


class InvalidControlTransitionException(InvalidLifecycleTransitionException):
    """Raised when illegal lifecycle transition is attempted in control assurance."""

    def __init__(self, current_state: str, target_state: str, reason: str = ""):
        msg = f"Invalid control transition from '{current_state}' to '{target_state}'."
        if reason:
            msg += f" Reason: {reason}"
        super().__init__(current_state, target_state)
        self.message = msg
        self.args = (msg,)


class ControlPolicyViolationException(ControlAssuranceException):
    """Raised when a control evaluation or operation violates policy constraints."""

    def __init__(self, control_id: str, reason: str):
        super().__init__(f"Control policy violation on '{control_id}': {reason}", code="POLICY_VIOLATION")


class ControlEvaluationBlockedException(ControlAssuranceException):
    """Raised when control evaluation cannot proceed."""

    def __init__(self, control_id: str, reason: str):
        super().__init__(f"Control evaluation for '{control_id}' blocked: {reason}", code="EVALUATION_BLOCKED")


class ControlRemediationBlockedException(ControlAssuranceException):
    """Raised when control remediation is blocked by governance or missing approval."""

    def __init__(self, plan_id: str, reason: str):
        super().__init__(f"Control remediation '{plan_id}' blocked: {reason}", code="REMEDIATION_BLOCKED")


class ImmutableAssuranceRecordException(ImmutableMutationException):
    """Raised when mutation is attempted on a finalized assurance record."""

    def __init__(self, record_id: str):
        super().__init__(record_id)
        self.message = f"Assurance record '{record_id}' is finalized and immutable."
        self.args = (self.message,)


class ControlIntegrityException(ControlAssuranceException):
    """Raised when control evidence or snapshot fingerprint verification fails."""

    def __init__(self, record_id: str, expected_fp: str, actual_fp: str):
        super().__init__(
            f"Control integrity verification failed for '{record_id}': expected '{expected_fp}', got '{actual_fp}'.",
            code="INTEGRITY_VERIFICATION_FAILED",
        )


class ControlAttestationException(ControlAssuranceException):
    """Raised when control attestation is invalid or fails criteria."""

    def __init__(self, attestation_id: str, reason: str):
        super().__init__(f"Control attestation '{attestation_id}' error: {reason}", code="ATTESTATION_ERROR")


class HighRiskControlOverrideRequiresApprovalException(ControlAssuranceException):
    """Raised when high-risk control override or exception requires human approval."""

    def __init__(self, control_id: str, risk_level: str):
        super().__init__(
            f"High-risk control override for '{control_id}' (risk: {risk_level}) requires explicit human approval.",
            code="HIGH_RISK_OVERRIDE_REQUIRES_APPROVAL",
        )
