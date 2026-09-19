"""Unified Enterprise Data Catalog & Asset Registry."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class DataAsset(BaseModel):
    """Specific entity inside dataset (table, file, API endpoint, collection)."""

    asset_id: str = Field(default_factory=lambda: f"asset_{uuid.uuid4().hex[:10]}")
    name: str
    asset_type: str  # TABLE, FILE, COLLECTION, ENDPOINT
    field_count: int = 0
    record_count: int = 0
    quality_score: float = 100.0


class DatasetVersion(BaseModel):
    """Version descriptor for a dataset."""

    version_id: str = Field(default_factory=lambda: f"ver_{uuid.uuid4().hex[:10]}")
    version_number: int = 1
    description: str = ""
    created_at: datetime = Field(default_factory=_now)


class Dataset(BaseModel):
    """Logical dataset grouping assets."""

    dataset_id: str = Field(default_factory=lambda: f"ds_set_{uuid.uuid4().hex[:10]}")
    source_id: str
    tenant_id: str = "global"
    organization_id: Optional[str] = None
    workspace_id: Optional[str] = None

    name: str
    description: str = ""
    owner: str = "system"

    classification: str = "INTERNAL"
    quality_score: float = 100.0
    assets: List[DataAsset] = Field(default_factory=list)
    versions: List[DatasetVersion] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)
    last_sync_at: Optional[datetime] = None


class CatalogEntry(BaseModel):
    """Entry stored in central catalog index."""

    entry_id: str
    title: str
    dataset_id: str
    tenant_id: str
    tags: List[str] = Field(default_factory=list)
    search_vector: str = ""


class DataCatalog:
    """Enterprise Data Catalog providing search, schema inspection, asset tracking, quality scoring, and classification."""

    def __init__(self) -> None:
        self._datasets: Dict[str, Dataset] = {}

    def register_dataset(self, dataset: Dataset) -> Dataset:
        self._datasets[dataset.dataset_id] = dataset
        logger.info(
            f"[DATA CATALOG] Registered dataset '{dataset.name}' (ID: {dataset.dataset_id}, Tenant: {dataset.tenant_id})"
        )
        return dataset

    def get_dataset(self, dataset_id: str) -> Dataset:
        ds = self._datasets.get(dataset_id)
        if not ds:
            raise KeyError(f"Dataset '{dataset_id}' not found in catalog")
        return ds

    def list_datasets(
        self,
        tenant_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        classification: Optional[str] = None,
    ) -> List[Dataset]:
        res = list(self._datasets.values())
        if tenant_id:
            res = [d for d in res if d.tenant_id == tenant_id]
        if organization_id:
            res = [d for d in res if d.organization_id == organization_id]
        if workspace_id:
            res = [d for d in res if d.workspace_id == workspace_id]
        if classification:
            res = [d for d in res if d.classification == classification]
        return res

    def search(self, query: str, tenant_id: Optional[str] = None) -> List[Dataset]:
        q_norm = query.lower()
        datasets = self.list_datasets(tenant_id=tenant_id)
        return [d for d in datasets if q_norm in d.name.lower() or q_norm in d.description.lower()]
