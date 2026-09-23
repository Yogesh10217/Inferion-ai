"""Knowledge reference intelligence referencing enterprise knowledge assets without duplicating storage."""

import hashlib
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.knowledge_assurance.exceptions import (
    CrossTenantKnowledgeAssuranceException,
    KnowledgeReferenceNotFoundException,
)


class KnowledgeReferenceType(str, Enum):
    DOCUMENT = "DOCUMENT"
    DATASET = "DATASET"
    POLICY = "POLICY"
    PROCEDURE = "PROCEDURE"
    INCIDENT = "INCIDENT"
    DECISION = "DECISION"
    MODEL = "MODEL"
    CONTROL = "CONTROL"
    SERVICE = "SERVICE"
    INTEGRATION = "INTEGRATION"


class KnowledgeReferenceStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DEPRECATED = "DEPRECATED"
    ARCHIVED = "ARCHIVED"


class KnowledgeReferenceClassification(str, Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    RESTRICTED = "RESTRICTED"
    TOP_SECRET = "TOP_SECRET"  # nosec B105


class KnowledgeReferenceMetadata(BaseModel):
    author: str = "system"
    version: str = "1.0.0"
    tags: List[str] = Field(default_factory=list)
    custom_attributes: Dict[str, Any] = Field(default_factory=dict)


class KnowledgeReference(BaseModel):
    reference_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    target_resource_id: str
    target_resource_type: KnowledgeReferenceType
    title: str
    summary: str = ""
    status: KnowledgeReferenceStatus = KnowledgeReferenceStatus.ACTIVE
    classification: KnowledgeReferenceClassification = KnowledgeReferenceClassification.INTERNAL
    metadata: KnowledgeReferenceMetadata = Field(default_factory=KnowledgeReferenceMetadata)
    fingerprint: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def external_key(self) -> str:
        return self.target_resource_id

    def calculate_fingerprint(self) -> str:
        data = f"{self.reference_id}:{self.tenant_id}:{self.target_resource_id}:{self.status.value}:{self.created_at.isoformat()}"
        return hashlib.sha256(data.encode("utf-8")).hexdigest()


class KnowledgeReferenceManager:
    """Manages references to external and internal knowledge assets."""

    def __init__(self) -> None:
        self._references: Dict[str, KnowledgeReference] = {}

    def create_reference(
        self,
        tenant_id: str,
        target_resource_id: Optional[str] = None,
        target_resource_type: Any = KnowledgeReferenceType.DOCUMENT,
        title: str = "Knowledge Reference",
        summary: str = "",
        classification: Any = KnowledgeReferenceClassification.INTERNAL,
        metadata: Optional[Any] = None,
        external_key: Optional[str] = None,
        resource_type: Optional[Any] = None,
    ) -> KnowledgeReference:
        res_id = external_key or target_resource_id or f"res-{uuid.uuid4().hex[:8]}"
        res_type_raw = resource_type or target_resource_type

        if isinstance(res_type_raw, str):
            try:
                res_type = KnowledgeReferenceType(res_type_raw)
            except ValueError:
                res_type = KnowledgeReferenceType.DOCUMENT
        else:
            res_type = res_type_raw

        if isinstance(classification, str):
            try:
                classif = KnowledgeReferenceClassification(classification)
            except ValueError:
                classif = KnowledgeReferenceClassification.INTERNAL
        else:
            classif = classification

        meta_obj = KnowledgeReferenceMetadata()
        if isinstance(metadata, dict):
            meta_obj.custom_attributes = metadata
        elif isinstance(metadata, KnowledgeReferenceMetadata):
            meta_obj = metadata

        ref = KnowledgeReference(
            tenant_id=tenant_id,
            target_resource_id=res_id,
            target_resource_type=res_type,
            title=title,
            summary=summary,
            classification=classif,
            metadata=meta_obj,
        )
        ref.fingerprint = ref.calculate_fingerprint()
        self._references[ref.reference_id] = ref
        return ref

    def register_reference(
        self,
        tenant_id: str,
        external_key: str,
        resource_type: Any = "DOCUMENT",
        classification: Any = "INTERNAL",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> KnowledgeReference:
        return self.create_reference(
            tenant_id=tenant_id,
            external_key=external_key,
            resource_type=resource_type,
            classification=classification,
            metadata=metadata,
        )

    def get_reference(
        self,
        tenant_id: Optional[str] = None,
        reference_id: Optional[str] = None,
    ) -> KnowledgeReference:
        ref_id = reference_id
        t_id = tenant_id
        # Handle positional args if passed as (tenant_id, reference_id) or (reference_id)
        if not ref_id and t_id and t_id in self._references:
            ref_id = t_id
            t_id = None

        if not ref_id or ref_id not in self._references:
            raise KnowledgeReferenceNotFoundException(f"Reference '{ref_id or 'unknown'}' not found")

        ref = self._references[ref_id]
        if t_id and ref.tenant_id != t_id:
            raise CrossTenantKnowledgeAssuranceException("Access denied: Tenant boundary violation.")

        return ref

    def list_references(self, tenant_id: str) -> List[KnowledgeReference]:
        return [r for r in self._references.values() if r.tenant_id == tenant_id]
