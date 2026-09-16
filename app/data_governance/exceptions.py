"""Domain exceptions for Enterprise AI Data Governance Platform."""


class DataGovernanceException(Exception):
    """Base exception for all data governance errors."""

    def __init__(self, message: str, tenant_id: str = "global", details: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.tenant_id = tenant_id
        self.details = details or {}


class DataAssetNotFoundException(DataGovernanceException):
    """Raised when a requested data asset cannot be found."""

    def __init__(self, asset_id: str, tenant_id: str = "global") -> None:
        super().__init__(f"Data asset '{asset_id}' not found for tenant '{tenant_id}'.", tenant_id=tenant_id, details={"asset_id": asset_id})


class DataAccessDeniedException(DataGovernanceException):
    """Raised when access to a data asset is denied."""

    def __init__(self, reason: str, tenant_id: str = "global", asset_id: str | None = None) -> None:
        super().__init__(f"Data access denied: {reason}", tenant_id=tenant_id, details={"asset_id": asset_id, "reason": reason})


class DataClassificationViolationException(DataGovernanceException):
    """Raised when a classification rule or monotonicity invariant is violated."""


class DataContractViolationException(DataGovernanceException):
    """Raised when data fails a contract specification or schema compatibility check."""


class DataQualityViolationException(DataGovernanceException):
    """Raised when data quality checks fail critical thresholds."""


class DataLineageException(DataGovernanceException):
    """Raised when a lineage operation or cross-tenant lineage access fails."""


class ConsentViolationException(DataGovernanceException):
    """Raised when processing lacks valid consent or consent was withdrawn."""


class RetentionPolicyViolationException(DataGovernanceException):
    """Raised when retention policy or legal hold prevents/violates lifecycle execution."""


class DataSharingViolationException(DataGovernanceException):
    """Raised when cross-tenant or unapproved data sharing is attempted."""


class DataTrustViolationException(DataGovernanceException):
    """Raised when data trust score is insufficient for requested operation."""


class CrossTenantDataAccessException(DataAccessDeniedException):
    """Raised when cross-tenant access is attempted without explicit authorization."""

    def __init__(self, request_tenant: str, target_tenant: str, asset_id: str) -> None:
        super().__init__(
            reason=f"Tenant '{request_tenant}' cannot access asset '{asset_id}' belonging to tenant '{target_tenant}'.",
            tenant_id=request_tenant,
            asset_id=asset_id,
        )
