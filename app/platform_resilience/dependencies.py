"""Service Dependency Intelligence Subsystem (Phase 5.37)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantAccessGuard
from app.architecture_platform.manager import ArchitecturePlatformManager
from app.platform_resilience.exceptions import CrossTenantResilienceAccessException


class DependencyType(str, Enum):
    UPSTREAM = "UPSTREAM"
    DOWNSTREAM = "DOWNSTREAM"
    HARD = "HARD"
    SOFT = "SOFT"
    OPTIONAL = "OPTIONAL"
    EXTERNAL = "EXTERNAL"


class DependencyCriticality(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class DependencyHealth(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
    UNKNOWN = "UNKNOWN"


class DependencyNode(BaseModel):
    node_id: str
    tenant_id: str
    service_name: str
    health: DependencyHealth = DependencyHealth.HEALTHY


class DependencyEdge(BaseModel):
    edge_id: str = Field(default_factory=lambda: f"depedge_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    source_service: str
    target_service: str
    dependency_type: DependencyType = DependencyType.HARD
    criticality: DependencyCriticality = DependencyCriticality.HIGH


class DependencyGraph(BaseModel):
    graph_id: str = Field(default_factory=lambda: f"depgraph_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    nodes: List[DependencyNode] = Field(default_factory=list)
    edges: List[DependencyEdge] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DependencyFailureImpact(BaseModel):
    impact_id: str = Field(default_factory=lambda: f"depimp_{uuid.uuid4().hex[:12]}")
    failed_service: str
    affected_services: List[str] = Field(default_factory=list)
    cascade_risk_score: float = 0.0
    recommended_isolation_strategy: str = "CIRCUIT_BREAKER"


class DependencyManager:
    """Service dependency intelligence manager leveraging ArchitecturePlatformManager."""

    def __init__(
        self,
        architecture_manager: Optional[ArchitecturePlatformManager] = None,
        tenant_guard: Optional[TenantAccessGuard] = None,
    ) -> None:
        self.architecture_manager = architecture_manager or ArchitecturePlatformManager()
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._graphs: Dict[str, DependencyGraph] = {}

    def register_dependency(
        self,
        tenant_id: str,
        source_service: str,
        target_service: str,
        dependency_type: DependencyType = DependencyType.HARD,
        criticality: DependencyCriticality = DependencyCriticality.HIGH,
    ) -> DependencyEdge:
        graph = self.get_or_create_graph(tenant_id)
        edge = DependencyEdge(
            tenant_id=tenant_id,
            source_service=source_service,
            target_service=target_service,
            dependency_type=dependency_type,
            criticality=criticality,
        )
        graph.edges.append(edge)
        
        # Add nodes if not existing
        node_names = {n.service_name for n in graph.nodes}
        if source_service not in node_names:
            graph.nodes.append(DependencyNode(node_id=f"node_{source_service}", tenant_id=tenant_id, service_name=source_service))
        if target_service not in node_names:
            graph.nodes.append(DependencyNode(node_id=f"node_{target_service}", tenant_id=tenant_id, service_name=target_service))

        # Register in architecture platform as well
        try:
            self.architecture_manager.dependency_manager.register_dependency(
                tenant_id=tenant_id,
                source_node_id=source_service,
                target_node_id=target_service,
            )
        except Exception:
            pass

        return edge

    def get_or_create_graph(self, tenant_id: str) -> DependencyGraph:
        if tenant_id not in self._graphs:
            self._graphs[tenant_id] = DependencyGraph(tenant_id=tenant_id)
        return self._graphs[tenant_id]

    def evaluate_failure_impact(self, tenant_id: str, failed_service: str) -> DependencyFailureImpact:
        graph = self.get_or_create_graph(tenant_id)
        affected = [e.source_service for e in graph.edges if e.target_service == failed_service]
        
        cascade_score = min(1.0, len(affected) * 0.25)
        return DependencyFailureImpact(
            failed_service=failed_service,
            affected_services=affected,
            cascade_risk_score=cascade_score,
            recommended_isolation_strategy="CIRCUIT_BREAKER" if cascade_score > 0.5 else "LOAD_SHED",
        )
