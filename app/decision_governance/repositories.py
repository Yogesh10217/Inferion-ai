"""Tenant-isolated thread-safe repositories for Decision Governance entities."""

import threading
from typing import Dict, Generic, List, TypeVar

from pydantic import BaseModel

from app.decision_governance.exceptions import CrossTenantDecisionGovernanceException, DecisionNotFoundException
from app.platform_contracts.redaction import SensitiveDataSanitizer

T = TypeVar("T", bound=BaseModel)


class DecisionGovernanceRepository(Generic[T]):
    """Thread-safe tenant-isolated repository enforcing strict tenant boundaries."""

    def __init__(self) -> None:
        self._store: Dict[str, Dict[str, T]] = {}  # tenant_id -> entity_id -> entity
        self._lock = threading.RLock()

    def save(self, tenant_id: str, entity_id: str, entity: T) -> T:
        with self._lock:
            meta = getattr(entity, "metadata", None)
            if isinstance(meta, dict):
                setattr(entity, "metadata", SensitiveDataSanitizer.sanitize_metadata(meta))

            if tenant_id not in self._store:
                self._store[tenant_id] = {}
            self._store[tenant_id][entity_id] = entity
            return entity

    def get(self, tenant_id: str, entity_id: str) -> T:
        with self._lock:
            tenant_store = self._store.get(tenant_id, {})
            entity = tenant_store.get(entity_id)

            if not entity:
                # Check if entity exists in another tenant to enforce tenant isolation exception with ZERO metadata
                for other_tenant, store in self._store.items():
                    if other_tenant != tenant_id and entity_id in store:
                        raise CrossTenantDecisionGovernanceException()
                raise DecisionNotFoundException(f"Resource '{entity_id}' not found")

            return entity

    def list(self, tenant_id: str) -> List[T]:
        with self._lock:
            tenant_store = self._store.get(tenant_id, {})
            return list(tenant_store.values())

    def delete(self, tenant_id: str, entity_id: str) -> bool:
        with self._lock:
            tenant_store = self._store.get(tenant_id, {})
            if entity_id in tenant_store:
                del tenant_store[entity_id]
                return True
            for other_tenant, store in self._store.items():
                if other_tenant != tenant_id and entity_id in store:
                    raise CrossTenantDecisionGovernanceException()
            return False
