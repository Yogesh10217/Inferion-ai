"""Tenant-Scoped Repository Interfaces (Phase 5.38)."""

from typing import Dict, Any, Optional, List
from app.platform_contracts.tenant import TenantAccessGuard
from app.control_assurance.exceptions import CrossTenantControlAssuranceAccessException


class ControlAssuranceRepository:
    """Production tenant-isolated in-memory and database repository for control assurance domain objects."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._storage: Dict[str, Dict[str, Any]] = {}

    def save(self, tenant_id: str, resource_type: str, resource_id: str, payload: Dict[str, Any]) -> None:
        key = f"{resource_type}:{resource_id}"
        self._storage[key] = {
            "tenant_id": tenant_id,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "payload": payload,
        }

    def get(self, tenant_id: str, resource_type: str, resource_id: str) -> Optional[Dict[str, Any]]:
        key = f"{resource_type}:{resource_id}"
        item = self._storage.get(key)
        if not item:
            return None
        try:
            self.tenant_guard.enforce_isolation(tenant_id, item["tenant_id"])
        except Exception:
            raise CrossTenantControlAssuranceAccessException()
        return item["payload"]
