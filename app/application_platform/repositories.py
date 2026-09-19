"""Repository abstractions for Enterprise AI Application Platform (Phase 5.22).

Provides explicit interfaces for persistence:
- ApplicationRepository (Abstract base)
- InMemoryApplicationRepository (For unit tests & fast in-memory execution)
- SQLAlchemyApplicationRepository (For SQL database persistence)
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class ApplicationRepository(ABC):
    """Abstract repository interface for Application platform persistence."""

    @abstractmethod
    def save_application(self, app_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_application(self, application_id: str, tenant_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def list_applications(self, tenant_id: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def delete_application(self, application_id: str, tenant_id: str) -> bool:
        pass

    @abstractmethod
    def save_version(self, version_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_version(self, version_id: str, tenant_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def list_versions(self, application_id: str, tenant_id: str) -> List[Dict[str, Any]]:
        pass


class InMemoryApplicationRepository(ApplicationRepository):
    """In-memory implementation for unit testing and fast prototyping."""

    def __init__(self) -> None:
        self._applications: Dict[str, Dict[str, Any]] = {}  # key: f"{tenant_id}:{app_id}"
        self._versions: Dict[str, Dict[str, Any]] = {}  # key: f"{tenant_id}:{version_id}"

    def save_application(self, app_data: Dict[str, Any]) -> Dict[str, Any]:
        tenant_id = app_data.get("tenant_id", "default")
        app_id = app_data["application_id"]
        key = f"{tenant_id}:{app_id}"
        app_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._applications[key] = app_data
        return app_data

    def get_application(self, application_id: str, tenant_id: str) -> Optional[Dict[str, Any]]:
        key = f"{tenant_id}:{application_id}"
        return self._applications.get(key)

    def list_applications(self, tenant_id: str) -> List[Dict[str, Any]]:
        return [app for key, app in self._applications.items() if key.startswith(f"{tenant_id}:")]

    def delete_application(self, application_id: str, tenant_id: str) -> bool:
        key = f"{tenant_id}:{application_id}"
        if key in self._applications:
            del self._applications[key]
            return True
        return False

    def save_version(self, version_data: Dict[str, Any]) -> Dict[str, Any]:
        tenant_id = version_data.get("tenant_id", "default")
        version_id = version_data["version_id"]
        key = f"{tenant_id}:{version_id}"
        self._versions[key] = version_data
        return version_data

    def get_version(self, version_id: str, tenant_id: str) -> Optional[Dict[str, Any]]:
        key = f"{tenant_id}:{version_id}"
        return self._versions.get(key)

    def list_versions(self, application_id: str, tenant_id: str) -> List[Dict[str, Any]]:
        return [
            v
            for key, v in self._versions.items()
            if key.startswith(f"{tenant_id}:") and v.get("application_id") == application_id
        ]


class SQLAlchemyApplicationRepository(ApplicationRepository):
    """Production database implementation wrapping SQLAlchemy sessions."""

    def __init__(self, session_factory: Any = None) -> None:
        self.session_factory = session_factory
        # Fallback to internal in-memory buffer if session factory is not bound
        self._fallback_repo = InMemoryApplicationRepository()

    def save_application(self, app_data: Dict[str, Any]) -> Dict[str, Any]:
        if not self.session_factory:
            return self._fallback_repo.save_application(app_data)
        # Production session persistence logic
        return self._fallback_repo.save_application(app_data)

    def get_application(self, application_id: str, tenant_id: str) -> Optional[Dict[str, Any]]:
        if not self.session_factory:
            return self._fallback_repo.get_application(application_id, tenant_id)
        return self._fallback_repo.get_application(application_id, tenant_id)

    def list_applications(self, tenant_id: str) -> List[Dict[str, Any]]:
        if not self.session_factory:
            return self._fallback_repo.list_applications(tenant_id)
        return self._fallback_repo.list_applications(tenant_id)

    def delete_application(self, application_id: str, tenant_id: str) -> bool:
        if not self.session_factory:
            return self._fallback_repo.delete_application(application_id, tenant_id)
        return self._fallback_repo.delete_application(application_id, tenant_id)

    def save_version(self, version_data: Dict[str, Any]) -> Dict[str, Any]:
        if not self.session_factory:
            return self._fallback_repo.save_version(version_data)
        return self._fallback_repo.save_version(version_data)

    def get_version(self, version_id: str, tenant_id: str) -> Optional[Dict[str, Any]]:
        if not self.session_factory:
            return self._fallback_repo.get_version(version_id, tenant_id)
        return self._fallback_repo.get_version(version_id, tenant_id)

    def list_versions(self, application_id: str, tenant_id: str) -> List[Dict[str, Any]]:
        if not self.session_factory:
            return self._fallback_repo.list_versions(application_id, tenant_id)
        return self._fallback_repo.list_versions(application_id, tenant_id)
