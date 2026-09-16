"""Tenant-safe exceptions for Enterprise AI Data Intelligence Platform (Phase 5.43)."""


class DataIntelligenceException(Exception):
    """Base exception for all Data Intelligence errors."""

    def __init__(self, message: str = "Data Intelligence error occurred.") -> None:
        super().__init__(message)
        self.message = message


class CrossTenantDataIntelligenceException(DataIntelligenceException):
    """Exception raised when a cross-tenant boundary violation occurs.

    MUST leak ZERO metadata:
    - no dataset existence
    - no tenant identifiers
    - no table names
    - no schema information
    - no pipeline identifiers
    - no data source metadata
    - no quality results
    - no lineage details
    """

    def __init__(self, message: str = "Access denied.") -> None:
        super().__init__("Access denied.")


class DatasetNotFoundException(DataIntelligenceException):
    """Raised when dataset reference is not found."""

    def __init__(self, dataset_id: str) -> None:
        super().__init__(f"Dataset reference '{dataset_id}' not found.")
        self.dataset_id = dataset_id


class DataSourceNotFoundException(DataIntelligenceException):
    """Raised when data source is not found."""

    def __init__(self, source_id: str) -> None:
        super().__init__(f"Data source '{source_id}' not found.")
        self.source_id = source_id


class DataQualityRuleNotFoundException(DataIntelligenceException):
    """Raised when data quality rule is not found."""

    def __init__(self, rule_id: str) -> None:
        super().__init__(f"Data quality rule '{rule_id}' not found.")
        self.rule_id = rule_id


class DataQualityEvaluationException(DataIntelligenceException):
    """Raised when data quality evaluation fails."""

    def __init__(self, reason: str) -> None:
        super().__init__(f"Data quality evaluation failed: {reason}")
        self.reason = reason


class DataAnomalyNotFoundException(DataIntelligenceException):
    """Raised when data anomaly is not found."""

    def __init__(self, anomaly_id: str) -> None:
        super().__init__(f"Data anomaly '{anomaly_id}' not found.")
        self.anomaly_id = anomaly_id


class DataIncidentNotFoundException(DataIntelligenceException):
    """Raised when data incident is not found."""

    def __init__(self, incident_id: str) -> None:
        super().__init__(f"Data incident '{incident_id}' not found.")
        self.incident_id = incident_id


class DataLineageNotFoundException(DataIntelligenceException):
    """Raised when data lineage is not found."""

    def __init__(self, lineage_id: str) -> None:
        super().__init__(f"Data lineage '{lineage_id}' not found.")
        self.lineage_id = lineage_id


class SchemaEvolutionException(DataIntelligenceException):
    """Raised when schema evolution fails or violates compatibility."""

    def __init__(self, reason: str) -> None:
        super().__init__(f"Schema evolution error: {reason}")
        self.reason = reason


class DataDriftException(DataIntelligenceException):
    """Raised when data drift processing fails."""

    def __init__(self, reason: str) -> None:
        super().__init__(f"Data drift error: {reason}")
        self.reason = reason


class DatasetTrustException(DataIntelligenceException):
    """Raised when dataset trust evaluation fails."""

    def __init__(self, reason: str) -> None:
        super().__init__(f"Dataset trust evaluation error: {reason}")
        self.reason = reason


class DataRemediationBlockedException(DataIntelligenceException):
    """Raised when data remediation action is blocked."""

    def __init__(self, action_name: str, reason: str) -> None:
        super().__init__(f"Data remediation action '{action_name}' blocked: {reason}")
        self.action_name = action_name
        self.reason = reason


class HighRiskDataActionRequiresApprovalException(DataIntelligenceException):
    """Raised when high-risk data action requires human approval."""

    def __init__(self, action_name: str, reason: str = "High-risk data action requires human approval.") -> None:
        super().__init__(f"High-risk data action '{action_name}' requires human approval: {reason}")
        self.action_name = action_name
        self.reason = reason


class ImmutableDataRecordException(DataIntelligenceException):
    """Raised when attempting to mutate an immutable finalized data record."""

    def __init__(self, record_id: str) -> None:
        super().__init__(f"Data record '{record_id}' is finalized and immutable.")
        self.record_id = record_id
