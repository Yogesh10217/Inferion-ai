"""Data Fabric Domain Exception Hierarchy."""

from typing import Any, Dict, Optional

from app.core.exceptions import AppException


class DataFabricException(AppException):
    """Base exception for all Data Fabric domain errors."""

    def __init__(
        self,
        message: str,
        code: str = "DATA_FABRIC_ERROR",
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message=message, code=code, status_code=status_code, details=details)


class DataSourceNotFoundException(DataFabricException):
    def __init__(self, source_id: str) -> None:
        super().__init__(message=f"Data source '{source_id}' not found", code="DATA_SOURCE_NOT_FOUND", status_code=404)


class ConnectorNotFoundException(DataFabricException):
    def __init__(self, connector_type: str) -> None:
        super().__init__(
            message=f"Connector for type '{connector_type}' not found or unregistered",
            code="CONNECTOR_NOT_FOUND",
            status_code=404,
        )


class ConnectorAuthenticationError(DataFabricException):
    def __init__(self, connector_type: str, reason: str) -> None:
        super().__init__(
            message=f"Authentication failed for connector '{connector_type}': {reason}",
            code="CONNECTOR_AUTH_ERROR",
            status_code=401,
        )


class ConnectorConfigurationError(DataFabricException):
    def __init__(self, message: str) -> None:
        super().__init__(message=message, code="CONNECTOR_CONFIG_ERROR", status_code=400)


class DataIngestionError(DataFabricException):
    def __init__(self, source_id: str, reason: str) -> None:
        super().__init__(
            message=f"Ingestion failed for data source '{source_id}': {reason}",
            code="DATA_INGESTION_ERROR",
            status_code=500,
        )


class DataSynchronizationError(DataFabricException):
    def __init__(self, sync_job_id: str, reason: str) -> None:
        super().__init__(
            message=f"Synchronization job '{sync_job_id}' failed: {reason}", code="DATA_SYNC_ERROR", status_code=500
        )


class SchemaDiscoveryError(DataFabricException):
    def __init__(self, source_id: str, reason: str) -> None:
        super().__init__(
            message=f"Schema discovery failed for data source '{source_id}': {reason}",
            code="SCHEMA_DISCOVERY_ERROR",
            status_code=500,
        )


class DataGovernanceError(DataFabricException):
    def __init__(self, message: str) -> None:
        super().__init__(message=message, code="DATA_GOVERNANCE_ERROR", status_code=403)


class DataAccessDenied(DataFabricException):
    def __init__(self, tenant_id: str, resource_id: str, reason: str = "Access denied by policy") -> None:
        super().__init__(
            message=f"Tenant '{tenant_id}' denied access to data resource '{resource_id}': {reason}",
            code="DATA_ACCESS_DENIED",
            status_code=403,
        )


class DataQualityError(DataFabricException):
    def __init__(self, asset_id: str, score: float, threshold: float) -> None:
        super().__init__(
            message=f"Data asset '{asset_id}' quality score ({score:.2f}) below threshold ({threshold:.2f})",
            code="DATA_QUALITY_ERROR",
            status_code=422,
        )


class LineageError(DataFabricException):
    def __init__(self, message: str) -> None:
        super().__init__(message=message, code="LINEAGE_ERROR", status_code=400)


class ChangeDataCaptureError(DataFabricException):
    def __init__(self, source_id: str, reason: str) -> None:
        super().__init__(
            message=f"CDC processing failed for source '{source_id}': {reason}", code="CDC_ERROR", status_code=500
        )
