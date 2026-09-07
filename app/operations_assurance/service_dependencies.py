"""Enterprise dependency intelligence mapping service targets across APIs, Databases, Models, Agents, Datasets, Infrastructure, and External Providers."""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional
import uuid
from pydantic import BaseModel, Field

from app.operations_assurance.exceptions import CrossTenantOperationsAssuranceException, DependencyNotFoundException


class DependencyType(str, Enum):
    API = "API"
    DATABASE = "DATABASE"
    MODEL = "MODEL"
    AGENT = "AGENT"
    DATASET = "DATASET"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    EXTERNAL_PROVIDER = "EXTERNAL_PROVIDER"


class DependencyCriticality(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ServiceDependency(BaseModel):
    dependency_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    source_service_id: str
    target_id: str
    dependency_type: DependencyType
    criticality: DependencyCriticality = DependencyCriticality.HIGH
    is_hard_dependency: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ServiceDependencyManager:
    """Manages mapping and retrieval of enterprise service dependencies."""

    def __init__(self) -> None:
        self._dependencies: Dict[str, Dict[str, ServiceDependency]] = {}  # tenant_id -> {dependency_id: dep}

    def add_dependency(
        self,
        tenant_id: str,
        source_service_id: str,
        target_id: str,
        dependency_type: DependencyType,
        criticality: DependencyCriticality = DependencyCriticality.HIGH,
        is_hard_dependency: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ServiceDependency:
        dep = ServiceDependency(
            tenant_id=tenant_id,
            source_service_id=source_service_id,
            target_id=target_id,
            dependency_type=dependency_type,
            criticality=criticality,
            is_hard_dependency=is_hard_dependency,
            metadata=metadata or {},
        )
        if tenant_id not in self._dependencies:
            self._dependencies[tenant_id] = {}
        self._dependencies[tenant_id][dep.dependency_id] = dep
        return dep

    def list_dependencies_for_service(self, tenant_id: str, source_service_id: str) -> List[ServiceDependency]:
        tenant_deps = self._dependencies.get(tenant_id, {})
        return [dep for dep in tenant_deps.values() if dep.source_service_id == source_service_id]

    def get_dependency(self, tenant_id: str, dependency_id: str) -> ServiceDependency:
        if tenant_id not in self._dependencies or dependency_id not in self._dependencies[tenant_id]:
            for tid, deps in self._dependencies.items():
                if tid != tenant_id and dependency_id in deps:
                    raise CrossTenantOperationsAssuranceException("Access denied.")
            raise DependencyNotFoundException("Dependency not found.")
        return self._dependencies[tenant_id][dependency_id]
