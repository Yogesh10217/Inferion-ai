"""Domain exceptions for Enterprise AI Compliance, Controls, Audit & Assurance Platform."""


class ComplianceException(Exception):
    """Base exception for all compliance platform errors."""
    def __init__(self, message: str, tenant_id: str = "global", details: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.tenant_id = tenant_id
        self.details = details or {}


class ComplianceFrameworkNotFoundException(ComplianceException):
    def __init__(self, framework_id: str, tenant_id: str = "global") -> None:
        super().__init__(f"Compliance framework '{framework_id}' not found for tenant '{tenant_id}'.", tenant_id=tenant_id)


class ComplianceRequirementNotFoundException(ComplianceException):
    def __init__(self, requirement_id: str, tenant_id: str = "global") -> None:
        super().__init__(f"Compliance requirement '{requirement_id}' not found for tenant '{tenant_id}'.", tenant_id=tenant_id)


class ControlNotFoundException(ComplianceException):
    def __init__(self, control_id: str, tenant_id: str = "global") -> None:
        super().__init__(f"Compliance control '{control_id}' not found for tenant '{tenant_id}'.", tenant_id=tenant_id)


class ControlMappingException(ComplianceException):
    pass


class EvidenceNotFoundException(ComplianceException):
    def __init__(self, evidence_id: str, tenant_id: str = "global") -> None:
        super().__init__(f"Compliance evidence '{evidence_id}' not found for tenant '{tenant_id}'.", tenant_id=tenant_id)


class EvidenceIntegrityException(ComplianceException):
    pass


class EvidenceCollectionException(ComplianceException):
    pass


class ImmutableEvidenceBundleException(ComplianceException):
    def __init__(self, bundle_id: str, tenant_id: str = "global") -> None:
        super().__init__(f"Immutability Violation: Finalized evidence bundle/package '{bundle_id}' cannot be modified.", tenant_id=tenant_id)


class ComplianceAssessmentException(ComplianceException):
    pass


class ComplianceFindingException(ComplianceException):
    pass


class ComplianceRemediationException(ComplianceException):
    pass


class CompliancePolicyViolationException(ComplianceException):
    pass


class AttestationExpiredException(ComplianceException):
    def __init__(self, attestation_id: str, tenant_id: str = "global") -> None:
        super().__init__(f"Attestation '{attestation_id}' has expired.", tenant_id=tenant_id)


class CrossTenantComplianceAccessException(ComplianceException):
    def __init__(self, request_tenant: str, target_tenant: str, resource_id: str) -> None:
        super().__init__(
            f"Access Denied: Tenant '{request_tenant}' cannot access compliance resource '{resource_id}' owned by tenant '{target_tenant}'.",
            tenant_id=request_tenant,
        )


class AuditTrailIntegrityException(ComplianceException):
    pass


class ImmutableAssuranceReportException(ComplianceException):
    def __init__(self, report_id: str, tenant_id: str = "global") -> None:
        super().__init__(f"Immutability Violation: Finalized assurance report '{report_id}' cannot be modified.", tenant_id=tenant_id)
