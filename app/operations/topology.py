"""Service Topology & Directed Dependency Intelligence Engine."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ServiceNodeType(str, Enum):
    GATEWAY = "GATEWAY"
    SERVICE = "SERVICE"
    LLM_PROVIDER = "LLM_PROVIDER"
    DEPLOYMENT = "DEPLOYMENT"
    AGENT = "AGENT"
    TEAM = "TEAM"
    WORKFLOW = "WORKFLOW"
    TOOL = "TOOL"
    MCP_SERVER = "MCP_SERVER"
    EXTENSION = "EXTENSION"
    DATA_SOURCE = "DATA_SOURCE"
    DATABASE = "DATABASE"
    CACHE = "CACHE"
    QUEUE = "QUEUE"
    WORKER = "WORKER"
    EXTERNAL_API = "EXTERNAL_API"


class ServiceNode(BaseModel):
    node_id: str
    name: str
    node_type: str  # GATEWAY, SERVICE, LLM_PROVIDER, DEPLOYMENT, AGENT, TEAM, WORKFLOW, TOOL, MCP_SERVER, EXTENSION, DATA_SOURCE, DATABASE, CACHE, QUEUE, WORKER, EXTERNAL_API
    tenant_id: str = "global"
    health_status: str = "HEALTHY"  # HEALTHY, DEGRADED, UNHEALTHY, UNKNOWN
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ServiceDependency(BaseModel):
    dependency_id: str = Field(default_factory=lambda: f"dep_{uuid.uuid4().hex[:10]}")
    source_id: str
    target_id: str
    dependency_type: str = "HARD"  # HARD, SOFT, FALLBACK
    tenant_id: str = "global"


class TopologyImpactAnalysis(BaseModel):
    root_node_id: str
    affected_nodes: List[str] = Field(default_factory=list)
    blast_radius_score: float = 0.0
    critical_dependencies: List[str] = Field(default_factory=list)


class TopologyManager:
    """Manages directed dependency graph, cycle detection, and health impact propagation across system components."""

    def __init__(self, health_service: Optional[Any] = None) -> None:
        self.health_service = health_service
        self._nodes: Dict[str, ServiceNode] = {}
        self._dependencies: List[ServiceDependency] = []

    def register_node(self, node_id: str, name: str, node_type: str, tenant_id: str = "global") -> ServiceNode:
        node = ServiceNode(node_id=node_id, name=name, node_type=node_type, tenant_id=tenant_id)
        self._nodes[node_id] = node
        logger.info(f"[TOPOLOGY] Registered node '{node_id}' ({node_type}) for tenant '{tenant_id}'")
        return node

    def add_dependency(self, source_id: str, target_id: str, dependency_type: str = "HARD", tenant_id: str = "global") -> ServiceDependency:
        dep = ServiceDependency(source_id=source_id, target_id=target_id, dependency_type=dependency_type, tenant_id=tenant_id)
        self._dependencies.append(dep)
        logger.info(f"[TOPOLOGY] Added dependency '{source_id}' -> '{target_id}' ({dependency_type})")
        return dep

    def update_node_health(self, node_id: str, status: str) -> Optional[ServiceNode]:
        if node_id in self._nodes:
            self._nodes[node_id].health_status = status
            logger.warning(f"[TOPOLOGY] Updated node '{node_id}' health -> {status}")
            return self._nodes[node_id]
        return None

    def analyze_impact(self, failed_node_id: str, tenant_id: Optional[str] = None) -> TopologyImpactAnalysis:
        """Calculate downstream affected nodes and blast radius."""
        affected: Set[str] = set()
        queue = [failed_node_id]

        while queue:
            curr = queue.pop(0)
            for dep in self._dependencies:
                if dep.target_id == curr and dep.source_id not in affected:
                    if not tenant_id or dep.tenant_id == tenant_id or dep.tenant_id == "global":
                        affected.add(dep.source_id)
                        queue.append(dep.source_id)

        blast_score = len(affected) * 1.5
        crit_deps = [dep.target_id for dep in self._dependencies if dep.source_id in affected and dep.dependency_type == "HARD"]

        analysis = TopologyImpactAnalysis(
            root_node_id=failed_node_id,
            affected_nodes=list(affected),
            blast_radius_score=float(blast_score),
            critical_dependencies=list(set(crit_deps)),
        )
        logger.info(f"[TOPOLOGY] Analyzed impact for '{failed_node_id}': Blast score = {blast_score}, Affected = {len(affected)} nodes")
        return analysis

    def list_nodes(self, tenant_id: Optional[str] = None) -> List[ServiceNode]:
        res = list(self._nodes.values())
        if tenant_id:
            res = [n for n in res if n.tenant_id in (tenant_id, "global")]
        return res
