"""Schema intelligence (Phase 5.43)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class SchemaCompatibility(str, Enum):
    NONE = "NONE"
    BACKWARD = "BACKWARD"
    FORWARD = "FORWARD"
    FULL = "FULL"
    INCOMPATIBLE = "INCOMPATIBLE"


class SchemaField(BaseModel):
    name: str
    data_type: str
    is_nullable: bool = True
    is_primary_key: bool = False
    is_deprecated: bool = False
    description: str = ""


class SchemaVersion(BaseModel):
    version_id: str
    dataset_id: str
    tenant_id: str
    version_number: str = "1.0.0"
    fields: List[SchemaField] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DatasetSchema(BaseModel):
    schema_id: str
    dataset_id: str
    tenant_id: str
    current_version: SchemaVersion
    version_history: List[SchemaVersion] = Field(default_factory=list)


class SchemaAssessment(BaseModel):
    assessment_id: str
    dataset_id: str
    tenant_id: str
    compatibility: SchemaCompatibility
    is_breaking_change: bool
    added_fields: List[str] = Field(default_factory=list)
    removed_fields: List[str] = Field(default_factory=list)
    modified_fields: List[str] = Field(default_factory=list)
    summary: str
    assessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SchemaManager:
    """Manages dataset schema versions and compatibility analysis (read-only, never mutates schemas)."""

    def __init__(self) -> None:
        self._schemas: Dict[str, DatasetSchema] = {}

    def register_schema(
        self,
        dataset_id: str,
        tenant_id: str,
        fields: List[SchemaField],
        version_number: str = "1.0.0",
        schema_id: Optional[str] = None,
    ) -> DatasetSchema:
        sid = schema_id or f"sch-{uuid.uuid4().hex[:8]}"
        vid = f"ver-{uuid.uuid4().hex[:8]}"

        sv = SchemaVersion(
            version_id=vid,
            dataset_id=dataset_id,
            tenant_id=tenant_id,
            version_number=version_number,
            fields=fields,
        )

        existing = self._schemas.get(dataset_id)
        if existing:
            existing.version_history.append(existing.current_version)
            existing.current_version = sv
            return existing

        ds = DatasetSchema(
            schema_id=sid,
            dataset_id=dataset_id,
            tenant_id=tenant_id,
            current_version=sv,
            version_history=[sv],
        )
        self._schemas[dataset_id] = ds
        return ds

    def compare_schemas(
        self,
        dataset_id: str,
        tenant_id: str,
        target_fields: List[SchemaField],
    ) -> SchemaAssessment:
        ds = self._schemas.get(dataset_id)
        current_fields = ds.current_version.fields if ds else []

        curr_names = {f.name: f for f in current_fields}
        targ_names = {f.name: f for f in target_fields}

        added = [n for n in targ_names if n not in curr_names]
        removed = [n for n in curr_names if n not in targ_names]
        modified = []

        for n in curr_names:
            if n in targ_names:
                if curr_names[n].data_type != targ_names[n].data_type:
                    modified.append(n)

        is_breaking = len(removed) > 0 or len(modified) > 0
        compat = SchemaCompatibility.INCOMPATIBLE if is_breaking else SchemaCompatibility.BACKWARD

        aid = f"sa-{uuid.uuid4().hex[:8]}"
        return SchemaAssessment(
            assessment_id=aid,
            dataset_id=dataset_id,
            tenant_id=tenant_id,
            compatibility=compat,
            is_breaking_change=is_breaking,
            added_fields=added,
            removed_fields=removed,
            modified_fields=modified,
            summary=f"Schema comparison for {dataset_id}: compatibility={compat.value}, breaking={is_breaking}",
        )
