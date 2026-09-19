"""Lifecycle Persistence Repositories Subsystem (Phase 5.33)."""

from typing import Any, Dict, List, Optional

from app.platform_contracts.repositories import TenantScopedRepository


class LifecycleRepository(TenantScopedRepository[Any]):
    """Repository abstraction supporting in-memory and database persistence with tenant scoping."""

    def __init__(self) -> None:
        self._store: Dict[str, Any] = {}

    def save(self, entity: Any) -> Any:
        eid = getattr(
            entity,
            "asset_id",
            getattr(
                entity,
                "dataset_id",
                getattr(
                    entity,
                    "model_id",
                    getattr(entity, "agent_id", getattr(entity, "release_id", getattr(entity, "snapshot_id", None))),
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


class AIAssetRepository(LifecycleRepository):
    pass


class DatasetRepository(LifecycleRepository):
    pass


class ModelRepository(LifecycleRepository):
    pass


class AgentRepository(LifecycleRepository):
    pass


class ReleaseRepository(LifecycleRepository):
    pass
