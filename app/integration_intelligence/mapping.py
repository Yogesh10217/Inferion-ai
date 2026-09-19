"""Cross-System Data Mapping Intelligence (Phase 5.40)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.integration_intelligence.exceptions import (
    CrossTenantIntegrationAccessException,
    IntegrationValidationException,
)


class MappingTransformation(str, Enum):
    DIRECT_COPY = "DIRECT_COPY"
    TYPE_CAST = "TYPE_CAST"
    STRUCTURAL_REMAP = "STRUCTURAL_REMAP"
    ANONYMIZE = "ANONYMIZE"
    CALCULATED = "CALCULATED"


class MappingRule(BaseModel):
    """Rule specifying field-level transformation mapping."""

    rule_id: str = Field(default_factory=lambda: f"map_rule_{uuid.uuid4().hex[:8]}")
    source_field: str
    target_field: str
    transformation: MappingTransformation = MappingTransformation.DIRECT_COPY
    transformation_expression: Optional[str] = None
    is_required: bool = True


class MappingValidation(BaseModel):
    """Declarative validation result for data mapping."""

    validation_id: str = Field(default_factory=lambda: f"map_val_{uuid.uuid4().hex[:8]}")
    is_valid: bool = True
    missing_required_fields: List[str] = Field(default_factory=list)
    type_mismatches: List[str] = Field(default_factory=list)


class IntegrationMapping(BaseModel):
    """Declarative Cross-System Data Mapping Representation."""

    mapping_id: str = Field(default_factory=lambda: f"map_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    name: str
    source_schema_id: str
    target_schema_id: str
    rules: List[MappingRule] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IntegrationMappingManager:
    """Manages declarative cross-system data mappings and transformation planning."""

    def __init__(self) -> None:
        self._mappings: Dict[str, IntegrationMapping] = {}

    def create_mapping(
        self,
        tenant_id: str,
        name: str,
        source_schema_id: str,
        target_schema_id: str,
        rules: Optional[List[MappingRule]] = None,
    ) -> IntegrationMapping:
        mapping = IntegrationMapping(
            tenant_id=tenant_id,
            name=name,
            source_schema_id=source_schema_id,
            target_schema_id=target_schema_id,
            rules=rules or [],
        )
        self._mappings[mapping.mapping_id] = mapping
        return mapping

    def validate_mapping(self, tenant_id: str, mapping_id: str, target_schema_fields: List[str]) -> MappingValidation:
        mapping = self.get_mapping(tenant_id, mapping_id)
        target_fields_mapped = {r.target_field for r in mapping.rules}

        missing = [f for f in target_schema_fields if f not in target_fields_mapped]
        is_valid = len(missing) == 0

        val = MappingValidation(
            is_valid=is_valid,
            missing_required_fields=missing,
        )
        if not is_valid:
            raise IntegrationValidationException(
                f"Mapping '{mapping_id}' missing required target fields: {', '.join(missing)}"
            )
        return val

    def get_mapping(self, tenant_id: str, mapping_id: str) -> IntegrationMapping:
        mapping = self._mappings.get(mapping_id)
        if not mapping or mapping.tenant_id != tenant_id:
            raise CrossTenantIntegrationAccessException()
        return mapping
