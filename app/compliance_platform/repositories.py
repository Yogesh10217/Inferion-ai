"""Repository Abstractions for Compliance Platform."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

from app.compliance_platform.frameworks import ComplianceFramework
from app.compliance_platform.controls import ComplianceControl
from app.compliance_platform.evidence import Evidence


class ComplianceFrameworkRepository(ABC):
    @abstractmethod
    def save(self, framework: ComplianceFramework) -> ComplianceFramework:
        pass

    @abstractmethod
    def get_by_id(self, framework_id: str, tenant_id: str) -> Optional[ComplianceFramework]:
        pass

    @abstractmethod
    def list(self, tenant_id: str) -> List[ComplianceFramework]:
        pass


class InMemoryComplianceFrameworkRepository(ComplianceFrameworkRepository):
    def __init__(self) -> None:
        self._store: Dict[str, ComplianceFramework] = {}

    def save(self, framework: ComplianceFramework) -> ComplianceFramework:
        self._store[framework.framework_id] = framework
        return framework

    def get_by_id(self, framework_id: str, tenant_id: str) -> Optional[ComplianceFramework]:
        fw = self._store.get(framework_id)
        if fw and (fw.tenant_id == tenant_id or tenant_id == "global"):
            return fw
        return None

    def list(self, tenant_id: str) -> List[ComplianceFramework]:
        return [fw for fw in self._store.values() if fw.tenant_id in (tenant_id, "global")]


class ComplianceRepository:
    """Production Repository Coordinator."""

    def __init__(self, use_memory: bool = True) -> None:
        self.use_memory = use_memory
        self.framework_repo: ComplianceFrameworkRepository = InMemoryComplianceFrameworkRepository()
