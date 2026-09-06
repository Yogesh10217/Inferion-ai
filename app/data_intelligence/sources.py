"""Enterprise data source intelligence (Phase 5.43)."""

import uuid
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.data_intelligence.exceptions import DataSourceNotFoundException, CrossTenantDataIntelligenceException
from app.platform_contracts.redaction import SensitiveDataSanitizer


class DataSourceType(str, Enum):
    DATABASE = "DATABASE"
    DATA_WAREHOUSE = "DATA_WAREHOUSE"
    OBJECT_STORAGE = "OBJECT_STORAGE"
    STREAMING = "STREAMING"
    API = "API"
    SAAS = "SAAS"
    AI_DATASET_STORE = "AI_DATASET_STORE"
    FEATURE_STORE = "FEATURE_STORE"


class DataSourceStatus(str, Enum):
    CONNECTED = "CONNECTED"
    DISCONNECTED = "DISCONNECTED"
    DEGRADED = "DEGRADED"
    UNREACHABLE = "UNREACHABLE"


class DataSourceCapability(str, Enum):
    READ = "READ"
    PROFILE = "PROFILE"
    LINEAGE_EXTRACTION = "LINEAGE_EXTRACTION"
    SCHEMA_INSPECTION = "SCHEMA_INSPECTION"
    DRIFT_DETECTION = "DRIFT_DETECTION"


class DataSource(BaseModel):
    """Reference to enterprise data source (zero credentials / secrets stored)."""
    source_id: str
    name: str
    tenant_id: str
    source_type: DataSourceType
    status: DataSourceStatus = DataSourceStatus.CONNECTED
    connection_endpoint: str
    capabilities: List[DataSourceCapability] = Field(default_factory=lambda: [DataSourceCapability.READ, DataSourceCapability.PROFILE])
    sanitized_metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DataSourceManager:
    """Manages references to data sources without storing raw secrets."""

    def __init__(self) -> None:
        self._sources: Dict[str, DataSource] = {}
        self._sanitizer = SensitiveDataSanitizer()

    def register_source(
        self,
        name: str,
        tenant_id: str,
        source_type: DataSourceType,
        connection_endpoint: str,
        capabilities: Optional[List[DataSourceCapability]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        source_id: Optional[str] = None,
    ) -> DataSource:
        sid = source_id or f"src-{uuid.uuid4().hex[:8]}"
        sanitized_meta = self._sanitizer.sanitize(metadata or {})
        clean_endpoint = str(self._sanitizer.sanitize(connection_endpoint))

        src = DataSource(
            source_id=sid,
            name=name,
            tenant_id=tenant_id,
            source_type=source_type,
            connection_endpoint=clean_endpoint,
            capabilities=capabilities or [DataSourceCapability.READ, DataSourceCapability.PROFILE],
            sanitized_metadata=sanitized_meta if isinstance(sanitized_meta, dict) else {},
        )
        self._sources[sid] = src
        return src

    def get_source(self, source_id: str, tenant_id: str) -> DataSource:
        src = self._sources.get(source_id)
        if not src:
            raise DataSourceNotFoundException(source_id)
        if src.tenant_id != tenant_id:
            raise CrossTenantDataIntelligenceException()
        return src

    def list_sources(self, tenant_id: str) -> List[DataSource]:
        return [s for s in self._sources.values() if s.tenant_id == tenant_id]
