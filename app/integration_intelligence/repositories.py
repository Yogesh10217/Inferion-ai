"""Tenant-Scoped Repositories for Integration Intelligence (Phase 5.40)."""

from typing import Any, Dict, Generic, List, TypeVar

from app.integration_intelligence.exceptions import CrossTenantIntegrationAccessException

T = TypeVar("T")


class TenantScopedIntegrationRepository(Generic[T]):
    """Generic repository enforcing strict tenant boundary checks with zero metadata leakage."""

    def __init__(self) -> None:
        self._store: Dict[str, T] = {}

    def save(self, tenant_id: str, item_id: str, item: T) -> T:
        key = f"{tenant_id}:{item_id}"
        self._store[key] = item
        return item

    def get(self, tenant_id: str, item_id: str) -> T:
        key = f"{tenant_id}:{item_id}"
        item = self._store.get(key)
        if not item:
            raise CrossTenantIntegrationAccessException()
        return item

    def list(self, tenant_id: str) -> List[T]:
        prefix = f"{tenant_id}:"
        return [v for k, v in self._store.items() if k.startswith(prefix)]


class IntegrationRepository(TenantScopedIntegrationRepository[Any]):
    pass


class ConnectorRepository(TenantScopedIntegrationRepository[Any]):
    pass


class WorkflowRepository(TenantScopedIntegrationRepository[Any]):
    pass


class ExecutionRepository(TenantScopedIntegrationRepository[Any]):
    pass


class FailureRepository(TenantScopedIntegrationRepository[Any]):
    pass


class InvestigationRepository(TenantScopedIntegrationRepository[Any]):
    pass
