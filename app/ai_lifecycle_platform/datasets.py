"""Dataset Lifecycle Governance Subsystem (Phase 5.33)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.ai_lifecycle_platform.exceptions import DatasetNotFoundException, CrossTenantLifecycleAccessException
from app.data_governance.manager import DataGovernanceManager


class DatasetStatus(str, Enum):
    REGISTERED = "REGISTERED"
    VALIDATED = "VALIDATED"
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"


class DatasetClassification(str, Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    RESTRICTED = "RESTRICTED"


class DatasetLineageReference(BaseModel):
    source_reference: str
    transformation: str = "RAW"


class DatasetVersion(BaseModel):
    version_id: str = Field(default_factory=lambda: f"dsver_{uuid.uuid4().hex[:12]}")
    version_tag: str = "1.0.0"
    num_records: int = 1000
    fingerprint: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Dataset(BaseModel):
    dataset_id: str = Field(default_factory=lambda: f"ds_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    name: str
    classification: DatasetClassification = DatasetClassification.INTERNAL
    status: DatasetStatus = DatasetStatus.REGISTERED
    versions: List[DatasetVersion] = Field(default_factory=list)
    lineage_references: List[DatasetLineageReference] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DatasetManager:
    """Manages AI dataset registration and delegates governance classification to DataGovernanceManager."""

    def __init__(self, data_governance_manager: Optional[DataGovernanceManager] = None) -> None:
        self.data_governance_manager = data_governance_manager or DataGovernanceManager()
        self._datasets: Dict[str, Dataset] = {}

    def register_dataset(
        self,
        tenant_id: str,
        name: str,
        classification: DatasetClassification = DatasetClassification.INTERNAL,
        initial_version_tag: str = "1.0.0",
        num_records: int = 1000,
    ) -> Dataset:
        ver = DatasetVersion(version_tag=initial_version_tag, num_records=num_records)
        ds = Dataset(
            tenant_id=tenant_id,
            name=name,
            classification=classification,
            versions=[ver],
        )
        self._datasets[ds.dataset_id] = ds
        return ds

    def get_dataset(self, dataset_id: str, tenant_id: str) -> Dataset:
        ds = self._datasets.get(dataset_id)
        if not ds:
            raise DatasetNotFoundException(dataset_id)
        if tenant_id != "global" and ds.tenant_id != "global" and tenant_id != ds.tenant_id:
            raise CrossTenantLifecycleAccessException(tenant_id, ds.tenant_id)
        return ds
