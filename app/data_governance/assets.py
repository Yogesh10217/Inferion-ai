"""Enterprise Data Asset Registry & Lifecycle Manager."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.data_governance.exceptions import DataAssetNotFoundException, CrossTenantDataAccessException


class DataAssetType(str, Enum):
    DATABASE = "DATABASE"
    TABLE = "TABLE"
    DOCUMENT = "DOCUMENT"
    DATASET = "DATASET"
    STREAM = "STREAM"
    API = "API"
    FILE = "FILE"
    VECTOR_COLLECTION = "VECTOR_COLLECTION"
    KNOWLEDGE_SOURCE = "KNOWLEDGE_SOURCE"
    MODEL_DATASET = "MODEL_DATASET"
    LOG = "LOG"
    EVENT_STREAM = "EVENT_STREAM"
    ANALYTICS_DATASET = "ANALYTICS_DATASET"


class DataAssetStatus(str, Enum):
    DISCOVERED = "DISCOVERED"
    REGISTERED = "REGISTERED"
    CLASSIFIED = "CLASSIFIED"
    GOVERNED = "GOVERNED"
    ACTIVE = "ACTIVE"
    RESTRICTED = "RESTRICTED"
    DEPRECATED = "DEPRECATED"
    ARCHIVED = "ARCHIVED"
    DELETED = "DELETED"


class DataDomain(str, Enum):
    CUSTOMER = "CUSTOMER"
    FINANCIAL = "FINANCIAL"
    OPERATIONS = "OPERATIONS"
    PRODUCT = "PRODUCT"
    ANALYTICS = "ANALYTICS"
    ENGINEERING = "ENGINEERING"
    COMPLIANCE = "COMPLIANCE"
    AI_KNOWLEDGE = "AI_KNOWLEDGE"
    GENERAL = "GENERAL"


class DataAssetOwner(BaseModel):
    owner_id: str
    owner_name: str
    owner_email: str
    role: str = "OWNER"
    department: Optional[str] = None


class DataAsset(BaseModel):
    """Enterprise Data Asset representation enforcing multi-tenancy."""

    tenant_id: str
    asset_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: DataAssetType
    owner: DataAssetOwner
    classification: str = "CONFIDENTIAL"
    domain: DataDomain = DataDomain.GENERAL
    status: DataAssetStatus = DataAssetStatus.REGISTERED
    source_reference: Dict[str, Any] = Field(default_factory=dict)
    schema_metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DataAssetManager:
    """Registry and manager for Enterprise Data Assets."""

    def __init__(self) -> None:
        self._assets: Dict[str, DataAsset] = {}

    def register_asset(
        self,
        tenant_id: str,
        name: str,
        asset_type: DataAssetType,
        owner: DataAssetOwner,
        classification: str = "CONFIDENTIAL",
        domain: DataDomain = DataDomain.GENERAL,
        source_reference: Optional[Dict[str, Any]] = None,
        asset_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> DataAsset:
        aid = asset_id or str(uuid.uuid4())
        asset = DataAsset(
            tenant_id=tenant_id,
            asset_id=aid,
            name=name,
            type=asset_type,
            owner=owner,
            classification=classification,
            domain=domain,
            status=DataAssetStatus.REGISTERED,
            source_reference=source_reference or {},
            tags=tags or [],
        )
        self._assets[aid] = asset
        return asset

    def get_asset(self, asset_id: str, tenant_id: str) -> DataAsset:
        asset = self._assets.get(asset_id)
        if not asset:
            raise DataAssetNotFoundException(asset_id=asset_id, tenant_id=tenant_id)
        if asset.tenant_id != tenant_id and tenant_id != "system":
            raise CrossTenantDataAccessException(request_tenant=tenant_id, target_tenant=asset.tenant_id, asset_id=asset_id)
        return asset

    def list_assets(
        self,
        tenant_id: str,
        domain: Optional[DataDomain] = None,
        asset_type: Optional[DataAssetType] = None,
        classification: Optional[str] = None,
        status: Optional[DataAssetStatus] = None,
    ) -> List[DataAsset]:
        results = [a for a in self._assets.values() if a.tenant_id == tenant_id]
        if domain:
            results = [a for a in results if a.domain == domain]
        if asset_type:
            results = [a for a in results if a.type == asset_type]
        if classification:
            results = [a for a in results if a.classification == classification]
        if status:
            results = [a for a in results if a.status == status]
        return results

    def update_asset_status(self, asset_id: str, tenant_id: str, new_status: DataAssetStatus) -> DataAsset:
        asset = self.get_asset(asset_id, tenant_id)
        asset.status = new_status
        asset.updated_at = datetime.now(timezone.utc)
        return asset

    def update_asset_classification(self, asset_id: str, tenant_id: str, classification: str) -> DataAsset:
        asset = self.get_asset(asset_id, tenant_id)
        asset.classification = classification
        asset.updated_at = datetime.now(timezone.utc)
        return asset
