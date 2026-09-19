"""Security Persistence Repositories Subsystem (Phase 5.32)."""

from typing import Any, Dict, List, Optional

from app.platform_contracts.repositories import TenantScopedRepository


class SecurityRepository(TenantScopedRepository[Any]):
    """Repository abstraction supporting memory and database persistence with tenant scoping."""

    def __init__(self) -> None:
        self._store: Dict[str, Any] = {}

    def save(self, entity: Any) -> Any:
        eid = getattr(
            entity,
            "asset_id",
            getattr(
                entity,
                "threat_id",
                getattr(
                    entity, "incident_id", getattr(entity, "vulnerability_id", getattr(entity, "posture_id", None))
                ),
            ),
        )
        if eid:
            self._store[eid] = entity
        return entity

    def get_by_id(self, entity_id: str) -> Optional[Any]:
        return self._store.get(entity_id)

    def get_by_id_and_tenant(self, entity_id: str, tenant_id: str) -> Optional[Any]:
        entity = self._store.get(entity_id)
        if entity and getattr(entity, "tenant_id", None) == tenant_id:
            return entity
        return None

    def list_by_tenant(self, tenant_id: str) -> List[Any]:
        return [e for e in self._store.values() if getattr(e, "tenant_id", None) == tenant_id]


class SecurityAssetRepository(SecurityRepository):
    pass


class SecurityThreatRepository(SecurityRepository):
    pass


class SecurityIncidentRepository(SecurityRepository):
    pass


class SecurityVulnerabilityRepository(SecurityRepository):
    pass


class SecurityPostureRepository(SecurityRepository):
    pass
