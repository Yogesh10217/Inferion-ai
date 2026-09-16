"""Tenant-Scoped Repositories for Access Intelligence (Phase 5.39)."""

from typing import Dict, Generic, List, TypeVar

from app.access_intelligence.exceptions import CrossTenantAccessIntelligenceException

T = TypeVar("T")


class TenantScopedRepository(Generic[T]):
    """Generic repository enforcing strict tenant isolation."""

    def __init__(self) -> None:
        self._storage: Dict[str, Dict[str, T]] = {}  # tenant_id -> (entity_id -> Entity)

    def save(self, tenant_id: str, entity_id: str, entity: T) -> T:
        if tenant_id not in self._storage:
            self._storage[tenant_id] = {}
        self._storage[tenant_id][entity_id] = entity
        return entity

    def get(self, tenant_id: str, entity_id: str) -> T:
        tenant_data = self._storage.get(tenant_id)
        if not tenant_data or entity_id not in tenant_data:
            raise CrossTenantAccessIntelligenceException()
        return tenant_data[entity_id]

    def list(self, tenant_id: str) -> List[T]:
        tenant_data = self._storage.get(tenant_id, {})
        return list(tenant_data.values())

    def delete(self, tenant_id: str, entity_id: str) -> bool:
        tenant_data = self._storage.get(tenant_id)
        if not tenant_data or entity_id not in tenant_data:
            raise CrossTenantAccessIntelligenceException()
        del tenant_data[entity_id]
        return True
