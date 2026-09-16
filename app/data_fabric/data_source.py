"""Data Source Registry & Management Subsystem."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.data_fabric.exceptions import DataSourceNotFoundException

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class DataSourceType(str, Enum):
    # Relational & NoSQL
    POSTGRES = "POSTGRES"
    MYSQL = "MYSQL"
    MONGODB = "MONGODB"
    REDIS = "REDIS"
    ELASTICSEARCH = "ELASTICSEARCH"

    # Cloud Storage
    S3 = "S3"
    AZURE_BLOB = "AZURE_BLOB"
    GCS = "GCS"

    # Productivity & Knowledge
    GOOGLE_DRIVE = "GOOGLE_DRIVE"
    ONEDRIVE = "ONEDRIVE"
    DROPBOX = "DROPBOX"

    # Enterprise Apps & Messaging
    SLACK = "SLACK"
    NOTION = "NOTION"
    CONFLUENCE = "CONFLUENCE"

    # Developer Platform
    GITHUB = "GITHUB"
    GITLAB = "GITLAB"

    # Web & API
    REST_API = "REST_API"
    GRAPHQL = "GRAPHQL"

    # Formats & Files
    CSV = "CSV"
    JSON = "JSON"
    PARQUET = "PARQUET"

    CUSTOM = "CUSTOM"


class DataSourceStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    PAUSED = "PAUSED"
    ERROR = "ERROR"
    SYNCING = "SYNCING"


class DataSource(BaseModel):
    """Enterprise Data Source definition."""

    id: str = Field(default_factory=lambda: f"ds_{uuid.uuid4().hex[:10]}")
    tenant_id: str = "global"
    organization_id: Optional[str] = None
    workspace_id: Optional[str] = None

    name: str
    description: str = ""

    source_type: DataSourceType
    connector_type: str

    status: DataSourceStatus = DataSourceStatus.ACTIVE
    configuration: Dict[str, Any] = Field(default_factory=dict)
    secret_reference: Optional[str] = None  # Reference ID to SecretManager, NEVER plain text secrets

    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)
    last_sync_at: Optional[datetime] = None


class DataSourceManager:
    """Manages creation, deletion, validation, tenant scoping, and status tracking for data sources."""

    def __init__(self) -> None:
        self._sources: Dict[str, DataSource] = {}

    def create_source(
        self,
        name: str,
        source_type: DataSourceType,
        connector_type: str,
        tenant_id: str = "global",
        organization_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        description: str = "",
        configuration: Optional[Dict[str, Any]] = None,
        secret_reference: Optional[str] = None,
    ) -> DataSource:
        ds = DataSource(
            name=name,
            source_type=source_type,
            connector_type=connector_type,
            tenant_id=tenant_id,
            organization_id=organization_id,
            workspace_id=workspace_id,
            description=description,
            configuration=configuration or {},
            secret_reference=secret_reference,
        )
        self._sources[ds.id] = ds
        logger.info(f"[DATA FABRIC] Created data source '{ds.name}' (ID: {ds.id}, Type: {ds.source_type.value}, Tenant: {tenant_id})")
        return ds

    def get_source(self, source_id: str) -> DataSource:
        ds = self._sources.get(source_id)
        if not ds:
            raise DataSourceNotFoundException(source_id)
        return ds

    def list_sources(
        self,
        tenant_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        source_type: Optional[DataSourceType] = None,
    ) -> List[DataSource]:
        res = list(self._sources.values())
        if tenant_id:
            res = [s for s in res if s.tenant_id == tenant_id]
        if organization_id:
            res = [s for s in res if s.organization_id == organization_id]
        if workspace_id:
            res = [s for s in res if s.workspace_id == workspace_id]
        if source_type:
            res = [s for s in res if s.source_type == source_type]
        return res

    def update_source(self, source_id: str, **updates) -> DataSource:
        ds = self.get_source(source_id)
        for k, v in updates.items():
            if hasattr(ds, k) and v is not None:
                setattr(ds, k, v)
        ds.updated_at = _now()
        logger.info(f"[DATA FABRIC] Updated data source '{ds.name}' (ID: {ds.id})")
        return ds

    def delete_source(self, source_id: str) -> None:
        ds = self.get_source(source_id)
        del self._sources[source_id]
        logger.info(f"[DATA FABRIC] Deleted data source '{ds.name}' (ID: {ds.id})")

    def update_sync_timestamp(self, source_id: str) -> None:
        ds = self.get_source(source_id)
        ds.last_sync_at = _now()
        ds.updated_at = _now()
