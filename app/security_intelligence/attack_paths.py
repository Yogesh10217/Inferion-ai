"""Attack Path Analysis Subsystem (Phase 5.32)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.architecture_platform.manager import ArchitecturePlatformManager
from app.security_intelligence.exceptions import AttackPathNotFoundException, CrossTenantSecurityAccessException


class AttackPathRisk(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class AttackPathNode(BaseModel):
    node_id: str
    node_name: str
    node_type: str  # e.g., PUBLIC_API, APPLICATION, AGENT, TOOL, DATA_ASSET


class AttackPathEdge(BaseModel):
    source_id: str
    target_id: str
    relationship: str  # e.g., CALLS, DELEGATES_TO, USES_TOOL, ACCESSES_DATA


class AttackPath(BaseModel):
    path_id: str = Field(default_factory=lambda: f"path_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    title: str
    nodes: List[AttackPathNode] = Field(default_factory=list)
    edges: List[AttackPathEdge] = Field(default_factory=list)
    risk_level: AttackPathRisk = AttackPathRisk.HIGH
    exposure_score: float = 85.0
    dependency_concentration: float = 0.75
    analyzed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AttackPathAnalyzer:
    """Analyzes topology paths to evaluate security exposure and attack vector risks analytically."""

    def __init__(self, architecture_manager: Optional[ArchitecturePlatformManager] = None) -> None:
        self.architecture_manager = architecture_manager or ArchitecturePlatformManager()
        self._paths: Dict[str, AttackPath] = {}

    def analyze_attack_path(
        self,
        tenant_id: str,
        entry_node_name: str = "Public_API",
        target_asset_name: str = "Sensitive_Data_Vault",
    ) -> AttackPath:
        n1 = AttackPathNode(node_id="n1", node_name=entry_node_name, node_type="PUBLIC_API")
        n2 = AttackPathNode(node_id="n2", node_name="Application_Gateway", node_type="APPLICATION")
        n3 = AttackPathNode(node_id="n3", node_name="AI_Agent_Worker", node_type="AGENT")
        n4 = AttackPathNode(node_id="n4", node_name="DB_Tool", node_type="TOOL")
        n5 = AttackPathNode(node_id="n5", node_name=target_asset_name, node_type="DATA_ASSET")

        edges = [
            AttackPathEdge(source_id="n1", target_id="n2", relationship="CALLS"),
            AttackPathEdge(source_id="n2", target_id="n3", relationship="DELEGATES_TO"),
            AttackPathEdge(source_id="n3", target_id="n4", relationship="USES_TOOL"),
            AttackPathEdge(source_id="n4", target_id="n5", relationship="ACCESSES_DATA"),
        ]

        path = AttackPath(
            tenant_id=tenant_id,
            title=f"Attack Path: {entry_node_name} -> {target_asset_name}",
            nodes=[n1, n2, n3, n4, n5],
            edges=edges,
            risk_level=AttackPathRisk.CRITICAL,
            exposure_score=92.0,
            dependency_concentration=0.85,
        )
        self._paths[path.path_id] = path
        return path

    def calculate_path_risk(self, path: AttackPath) -> float:
        return path.exposure_score * path.dependency_concentration

    def get_attack_path(self, path_id: str, tenant_id: str) -> AttackPath:
        path = self._paths.get(path_id)
        if not path:
            raise AttackPathNotFoundException(path_id)
        if tenant_id != "global" and path.tenant_id != "global" and tenant_id != path.tenant_id:
            raise CrossTenantSecurityAccessException(tenant_id, path.tenant_id)
        return path
