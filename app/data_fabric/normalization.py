"""Data Normalization & Transformation Pipeline."""

from datetime import datetime, timezone
import uuid
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class NormalizedRecord(BaseModel):
    """Standardized normalized record preserving lineage metadata."""

    record_id: str = Field(default_factory=lambda: f"rec_{uuid.uuid4().hex[:10]}")
    source_id: str
    source_record_id: str
    tenant_id: str = "global"
    workspace_id: Optional[str] = None
    schema_version: int = 1

    payload: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


class DataTransformation(BaseModel):
    """Transformation rule applied during normalization."""

    name: str
    field_mapping: Dict[str, str] = Field(default_factory=dict)  # target_field -> source_field
    drop_nulls: bool = False


class DataNormalizer:
    """Normalizes JSON, CSV, DB rows, documents, and API responses into standardized structures."""

    def normalize_record(
        self,
        raw_data: Dict[str, Any],
        source_id: str,
        source_record_id: str,
        tenant_id: str = "global",
        workspace_id: Optional[str] = None,
        transformation: Optional[DataTransformation] = None,
    ) -> NormalizedRecord:
        """Map raw dictionary to NormalizedRecord."""
        payload = dict(raw_data)
        if transformation and transformation.field_mapping:
            payload = {target: raw_data.get(src) for target, src in transformation.field_mapping.items() if src in raw_data}

        return NormalizedRecord(
            source_id=source_id,
            source_record_id=source_record_id,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            payload=payload,
        )

    def normalize_batch(
        self,
        raw_records: List[Dict[str, Any]],
        source_id: str,
        tenant_id: str = "global",
        workspace_id: Optional[str] = None,
    ) -> List[NormalizedRecord]:
        normalized = []
        for idx, item in enumerate(raw_records):
            src_rec_id = str(item.get("id") or item.get("key") or item.get("file_id") or f"idx_{idx}")
            rec = self.normalize_record(
                raw_data=item,
                source_id=source_id,
                source_record_id=src_rec_id,
                tenant_id=tenant_id,
                workspace_id=workspace_id,
            )
            normalized.append(rec)
        return normalized
