"""Tenant-Scoped Repository Abstractions (Phase 5.36)."""

from typing import Dict, Any, Optional, List, Generic, TypeVar
from app.platform_contracts.tenant import TenantAccessGuard
from app.agent_orchestration.exceptions import CrossTenantAgentAccessException

T = TypeVar("T")


class BaseAgentRepository(Generic[T]):
    """Generic in-memory tenant-scoped repository abstraction."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._store: Dict[str, T] = {}

    def save(self, key: str, entity: T, tenant_id: str) -> T:
        self._store[key] = entity
        return entity

    def find_by_id(self, key: str, tenant_id: str) -> Optional[T]:
        entity = self._store.get(key)
        if entity and hasattr(entity, "tenant_id"):
            try:
                self.tenant_guard.enforce_isolation(tenant_id, getattr(entity, "tenant_id"))
            except Exception:
                raise CrossTenantAgentAccessException(tenant_id, getattr(entity, "tenant_id"))
        return entity

    def list_all(self, tenant_id: str) -> List[T]:
        results = []
        for e in self._store.values():
            e_tenant = getattr(e, "tenant_id", None)
            if e_tenant == tenant_id or tenant_id == "global":
                results.append(e)
        return results


class AgentRepository(BaseAgentRepository[Any]):
    pass


class AgentTaskRepository(BaseAgentRepository[Any]):
    pass


class AgentPlanRepository(BaseAgentRepository[Any]):
    pass


class AgentExecutionRepository(BaseAgentRepository[Any]):
    pass


class AgentTraceRepository(BaseAgentRepository[Any]):
    pass


class AgentCollaborationRepository(BaseAgentRepository[Any]):
    pass
