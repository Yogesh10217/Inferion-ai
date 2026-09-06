"""Knowledge Assurance Repositories Module.

Provides tenant-isolated, metadata-sanitized, SHA-256 fingerprint verified repository implementations.
Enforces strict cross-tenant isolation and immutability rules.
"""

import hashlib
import json
from typing import Dict, List, Optional, TypeVar, Generic
from pydantic import BaseModel

from app.knowledge_assurance.exceptions import (
    CrossTenantKnowledgeAssuranceException,
    ImmutableKnowledgeRecordException,
    KnowledgeReferenceNotFoundException,
)
from app.platform_contracts.redaction import SensitiveDataSanitizer


T = TypeVar("T", bound=BaseModel)


class TenantIsolatedRepository(Generic[T]):
    """Generic in-memory tenant-isolated repository with immutability and sanitization features."""

    def __init__(self, resource_name: str = "Resource") -> None:
        self.resource_name = resource_name
        self._store: Dict[str, T] = {}
        self._tenant_map: Dict[str, str] = {}
        self._finalized_ids: set = set()
        self._fingerprints: Dict[str, str] = {}

    def _compute_sha256(self, entity: T) -> str:
        dumped = entity.model_dump(mode="json")
        raw = json.dumps(dumped, sort_keys=True).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    def save(
        self,
        tenant_id: str,
        entity_id: str,
        entity: T,
        is_finalized: bool = False,
    ) -> T:
        if entity_id in self._finalized_ids:
            raise ImmutableKnowledgeRecordException(
                f"{self.resource_name} {entity_id} is finalized and immutable."
            )

        # Ensure entity fields match tenant_id if present
        if hasattr(entity, "tenant_id") and getattr(entity, "tenant_id") != tenant_id:
            raise CrossTenantKnowledgeAssuranceException()

        # Sanitize metadata or payload if present
        if hasattr(entity, "metadata") and isinstance(getattr(entity, "metadata"), dict):
            sanitized = SensitiveDataSanitizer.sanitize(getattr(entity, "metadata"))
            if isinstance(sanitized, dict):
                setattr(entity, "metadata", sanitized)

        self._store[entity_id] = entity
        self._tenant_map[entity_id] = tenant_id
        self._fingerprints[entity_id] = self._compute_sha256(entity)

        if is_finalized:
            self._finalized_ids.add(entity_id)

        return entity

    def get(self, tenant_id: str, entity_id: str) -> T:
        if entity_id not in self._store:
            raise KnowledgeReferenceNotFoundException(
                f"{self.resource_name} not found."
            )
        owner_tenant = self._tenant_map.get(entity_id)
        if owner_tenant != tenant_id:
            # ZERO metadata leakage
            raise CrossTenantKnowledgeAssuranceException()
        return self._store[entity_id]

    def list_all(self, tenant_id: str) -> List[T]:
        return [
            entity
            for eid, entity in self._store.items()
            if self._tenant_map.get(eid) == tenant_id
        ]

    def verify_integrity(self, tenant_id: str, entity_id: str) -> bool:
        entity = self.get(tenant_id, entity_id)
        stored_fp = self._fingerprints.get(entity_id, "")
        current_fp = self._compute_sha256(entity)
        return stored_fp == current_fp

    def mark_finalized(self, tenant_id: str, entity_id: str) -> None:
        self.get(tenant_id, entity_id)  # Verifies tenant ownership
        self._finalized_ids.add(entity_id)
