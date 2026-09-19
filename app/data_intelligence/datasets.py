"""Enterprise dataset intelligence registry (Phase 5.43)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.data_intelligence.exceptions import CrossTenantDataIntelligenceException, DatasetNotFoundException


class DatasetType(str, Enum):
    TABLE = "TABLE"
    VIEW = "VIEW"
    FILE = "FILE"
    STREAM = "STREAM"
    FEATURE_STORE = "FEATURE_STORE"
    AI_DATASET = "AI_DATASET"
    VECTOR_INDEX = "VECTOR_INDEX"
    KNOWLEDGE_BASE = "KNOWLEDGE_BASE"


class DatasetStatus(str, Enum):
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"
    ARCHIVED = "ARCHIVED"
    STALE = "STALE"
    QUARANTINED = "QUARANTINED"


class DatasetClassificationReference(BaseModel):
    """Reference to existing platform data classification."""

    classification_id: str
    tier: str = "CONFIDENTIAL"
    contains_pii: bool = False
    contains_phi: bool = False
    sensitivity_score: float = 0.5


class DatasetMetadata(BaseModel):
    """Metadata reference for dataset."""

    description: str = ""
    domain: str = "general"
    owner_id: str = "system"
    source_id: Optional[str] = None
    row_count_estimate: Optional[int] = None
    size_bytes_estimate: Optional[int] = None
    tags: List[str] = Field(default_factory=list)
    custom_attributes: Dict[str, Any] = Field(default_factory=dict)


class DatasetProfile(BaseModel):
    """Profile reference for dataset state."""

    profile_id: str = Field(default_factory=lambda: f"prof-{uuid.uuid4().hex[:8]}")
    dataset_id: str
    tenant_id: str
    column_count: int = 0
    row_count: int = 0
    null_ratio: float = 0.0
    duplicate_ratio: float = 0.0
    completeness_score: float = 1.0
    uniqueness_score: float = 1.0
    analyzed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DatasetReference(BaseModel):
    """Enterprise reference to existing platform dataset (no storage duplication)."""

    dataset_id: str
    name: str
    tenant_id: str
    dataset_type: DatasetType = DatasetType.TABLE
    status: DatasetStatus = DatasetStatus.ACTIVE
    source_id: Optional[str] = None
    external_uri: Optional[str] = None
    classification: DatasetClassificationReference = Field(
        default_factory=lambda: DatasetClassificationReference(classification_id="class-default")
    )
    metadata: DatasetMetadata = Field(default_factory=DatasetMetadata)
    version: str = "1.0.0"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DatasetIntelligenceManager:
    """Manages references to enterprise datasets."""

    def __init__(self) -> None:
        self._datasets: Dict[str, DatasetReference] = {}

    def register_dataset(
        self,
        name: str,
        tenant_id: str,
        dataset_type: DatasetType = DatasetType.TABLE,
        source_id: Optional[str] = None,
        external_uri: Optional[str] = None,
        classification: Optional[DatasetClassificationReference] = None,
        metadata: Optional[DatasetMetadata] = None,
        dataset_id: Optional[str] = None,
    ) -> DatasetReference:
        did = dataset_id or f"ds-{uuid.uuid4().hex[:8]}"
        ref = DatasetReference(
            dataset_id=did,
            name=name,
            tenant_id=tenant_id,
            dataset_type=dataset_type,
            source_id=source_id,
            external_uri=external_uri,
            classification=classification or DatasetClassificationReference(classification_id=f"class-{did}"),
            metadata=metadata or DatasetMetadata(),
        )
        self._datasets[did] = ref
        return ref

    def get_dataset(self, dataset_id: str, tenant_id: str) -> DatasetReference:
        ds = self._datasets.get(dataset_id)
        if not ds:
            raise DatasetNotFoundException(dataset_id)
        if ds.tenant_id != tenant_id:
            raise CrossTenantDataIntelligenceException()
        return ds

    def list_datasets(self, tenant_id: str) -> List[DatasetReference]:
        return [ds for ds in self._datasets.values() if ds.tenant_id == tenant_id]

    def update_status(self, dataset_id: str, tenant_id: str, status: DatasetStatus) -> DatasetReference:
        ds = self.get_dataset(dataset_id, tenant_id)
        ds.status = status
        ds.updated_at = datetime.now(timezone.utc)
        return ds
