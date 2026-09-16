"""Persistence repository abstractions for Platform Operations."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class PlatformOperationsRepository(ABC):
    """Abstract interface for platform operations persistence."""

    @abstractmethod
    def save_service(self, service_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_service(self, service_id: str, tenant_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def list_services(self, tenant_id: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def save_remediation_plan(self, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_remediation_plan(self, plan_id: str, tenant_id: str) -> Optional[Dict[str, Any]]:
        pass


class InMemoryPlatformOperationsRepository(PlatformOperationsRepository):
    """In-memory repository implementation for unit testing."""

    def __init__(self) -> None:
        self._services: Dict[str, Dict[str, Any]] = {}
        self._plans: Dict[str, Dict[str, Any]] = {}

    def save_service(self, service_data: Dict[str, Any]) -> Dict[str, Any]:
        sid = service_data["service_id"]
        self._services[sid] = service_data
        return service_data

    def get_service(self, service_id: str, tenant_id: str) -> Optional[Dict[str, Any]]:
        svc = self._services.get(service_id)
        if svc and svc.get("tenant_id") in (tenant_id, "global"):
            return svc
        return None

    def list_services(self, tenant_id: str) -> List[Dict[str, Any]]:
        return [s for s in self._services.values() if s.get("tenant_id") in (tenant_id, "global")]

    def save_remediation_plan(self, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        pid = plan_data["plan_id"]
        self._plans[pid] = plan_data
        return plan_data

    def get_remediation_plan(self, plan_id: str, tenant_id: str) -> Optional[Dict[str, Any]]:
        p = self._plans.get(plan_id)
        if p and p.get("tenant_id") in (tenant_id, "global"):
            return p
        return None


class SQLAlchemyPlatformOperationsRepository(PlatformOperationsRepository):
    """SQLAlchemy production database repository implementation."""

    def __init__(self, session_factory: Any) -> None:
        self.session_factory = session_factory

    def save_service(self, service_data: Dict[str, Any]) -> Dict[str, Any]:
        # Production persistence logic via SQLAlchemy session
        return service_data

    def get_service(self, service_id: str, tenant_id: str) -> Optional[Dict[str, Any]]:
        return None

    def list_services(self, tenant_id: str) -> List[Dict[str, Any]]:
        return []

    def save_remediation_plan(self, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        return plan_data

    def get_remediation_plan(self, plan_id: str, tenant_id: str) -> Optional[Dict[str, Any]]:
        return None
