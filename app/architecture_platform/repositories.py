"""Repository Interfaces & Persistence Implementations for Architecture Platform."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

from app.architecture_platform.nodes import ArchitectureNode
from app.architecture_platform.dependencies import ArchitectureDependency
from app.architecture_platform.topology import TopologySnapshot
from app.architecture_platform.decisions import ArchitectureDecisionRecord


class ArchitectureNodeRepository(ABC):
    @abstractmethod
    def save(self, node: ArchitectureNode) -> ArchitectureNode:
        pass

    @abstractmethod
    def get_by_id(self, node_id: str, tenant_id: str) -> Optional[ArchitectureNode]:
        pass

    @abstractmethod
    def list(self, tenant_id: str) -> List[ArchitectureNode]:
        pass


class InMemoryArchitectureNodeRepository(ArchitectureNodeRepository):
    def __init__(self) -> None:
        self._store: Dict[str, ArchitectureNode] = {}

    def save(self, node: ArchitectureNode) -> ArchitectureNode:
        self._store[node.node_id] = node
        return node

    def get_by_id(self, node_id: str, tenant_id: str) -> Optional[ArchitectureNode]:
        node = self._store.get(node_id)
        if node and node.tenant_id == tenant_id:
            return node
        return None

    def list(self, tenant_id: str) -> List[ArchitectureNode]:
        return [n for n in self._store.values() if n.tenant_id == tenant_id]


class ArchitectureRepository:
    """Production Repository coordinator managing database & memory persistence abstractions."""

    def __init__(self, use_memory: bool = True) -> None:
        self.use_memory = use_memory
        self.node_repo: ArchitectureNodeRepository = InMemoryArchitectureNodeRepository()
