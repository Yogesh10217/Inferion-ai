"""Tenant-Scoped Repositories Subsystem (Phase 5.37)."""

from typing import Any, Dict, List, Optional

from app.platform_contracts.tenant import TenantAccessGuard
from app.platform_resilience.exceptions import CrossTenantResilienceAccessException


class PlatformResilienceRepository:
    """Tenant-scoped repository interface for all resilience entities."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._storage: Dict[str, Dict[str, Any]] = {}

    def save(self, entity_id: str, tenant_id: str, data: Dict[str, Any]) -> None:
        data["tenant_id"] = tenant_id
        self._storage[entity_id] = data

    def get(self, entity_id: str, tenant_id: str) -> Optional[Dict[str, Any]]:
        item = self._storage.get(entity_id)
        if not item:
            return None

        try:
            self.tenant_guard.enforce_isolation(tenant_id, item["tenant_id"])
        except Exception:
            raise CrossTenantResilienceAccessException(tenant_id, item["tenant_id"])

        return item

    def list_by_tenant(self, tenant_id: str) -> List[Dict[str, Any]]:
        return [item for item in self._storage.values() if item.get("tenant_id") == tenant_id or tenant_id == "global"]
