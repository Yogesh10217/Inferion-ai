"""Shared Repository Contract Interfaces (Phase 5.30)."""

from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar

T = TypeVar("T")


class Repository(ABC, Generic[T]):
    @abstractmethod
    def save(self, entity: T) -> T:
        pass

    @abstractmethod
    def get_by_id(self, entity_id: str) -> Optional[T]:
        pass


class TenantScopedRepository(Repository[T], ABC):
    @abstractmethod
    def get_by_id_and_tenant(self, entity_id: str, tenant_id: str) -> Optional[T]:
        pass

    @abstractmethod
    def list_by_tenant(self, tenant_id: str) -> List[T]:
        pass


class ImmutableRepository(TenantScopedRepository[T], ABC):
    @abstractmethod
    def finalize(self, entity_id: str, tenant_id: str, fingerprint: str) -> T:
        pass


class VersionedRepository(TenantScopedRepository[T], ABC):
    @abstractmethod
    def get_by_version(self, entity_id: str, tenant_id: str, version: str) -> Optional[T]:
        pass
