"""Enterprise Architecture Topology & Immutable Snapshot Subsystem."""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.architecture_platform.exceptions import (
    CrossTenantArchitectureAccessException,
    ImmutableTopologySnapshotException,
)
from app.architecture_platform.nodes import ArchitectureNode, ArchitectureNodeManager


class TopologyVersion(BaseModel):
    version_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    version_string: str = "1.0.0"
    description: str = "Initial Topology Version"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ArchitectureTopology(BaseModel):
    tenant_id: str
    topology_id: str = Field(default_factory=lambda: f"top_{uuid.uuid4().hex[:12]}")
    environment: str = "production"
    nodes: Dict[str, ArchitectureNode] = Field(default_factory=dict)
    boundary_map: Dict[str, List[str]] = Field(default_factory=dict)  # domain -> list[node_id]
    version: str = "1.0.0"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TopologySnapshot(BaseModel):
    """Immutable finalized architecture snapshot with reproducible SHA-256 fingerprinting."""

    snapshot_id: str = Field(default_factory=lambda: f"snap_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    environment: str = "production"
    topology_version: str = "1.0.0"
    node_ids: List[str] = Field(default_factory=list)
    boundary_map: Dict[str, List[str]] = Field(default_factory=dict)
    architecture_fingerprint: str
    observed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_finalized: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def verify_fingerprint(self, canonical_state_json: str) -> bool:
        calculated = hashlib.sha256(canonical_state_json.encode("utf-8")).hexdigest()
        return calculated == self.architecture_fingerprint


class TopologyManager:
    """Manages tenant-scoped topology graph building and immutable snapshot creation."""

    def __init__(self, node_manager: ArchitectureNodeManager) -> None:
        self.node_manager = node_manager
        self._topologies: Dict[str, Dict[str, ArchitectureTopology]] = {}  # tenant_id -> {env -> ArchitectureTopology}
        self._snapshots: Dict[str, TopologySnapshot] = {}  # snapshot_id -> TopologySnapshot

    def build_topology(self, tenant_id: str, environment: str = "production") -> ArchitectureTopology:
        nodes = self.node_manager.list_nodes(tenant_id=tenant_id, environment=environment)
        node_dict = {n.node_id: n for n in nodes}

        boundaries: Dict[str, List[str]] = {}
        for n in nodes:
            team = n.metadata.team
            if team not in boundaries:
                boundaries[team] = []
            boundaries[team].append(n.node_id)

        top = ArchitectureTopology(
            tenant_id=tenant_id,
            environment=environment,
            nodes=node_dict,
            boundary_map=boundaries,
        )

        if tenant_id not in self._topologies:
            self._topologies[tenant_id] = {}
        self._topologies[tenant_id][environment] = top
        return top

    def create_snapshot(self, tenant_id: str, environment: str = "production", description: str = "Snapshot") -> TopologySnapshot:
        top = self.build_topology(tenant_id, environment)

        # Generate deterministic SHA-256 fingerprint from canonical architecture state
        sorted_nodes = sorted([{"id": n.node_id, "type": n.node_type.value, "status": n.status.value} for n in top.nodes.values()], key=lambda x: x["id"])
        canonical_json = json.dumps({"tenant_id": tenant_id, "environment": environment, "nodes": sorted_nodes}, sort_keys=True)
        fingerprint = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

        snapshot = TopologySnapshot(
            tenant_id=tenant_id,
            environment=environment,
            topology_version=top.version,
            node_ids=list(top.nodes.keys()),
            boundary_map=top.boundary_map,
            architecture_fingerprint=fingerprint,
            metadata={"description": description, "node_count": len(top.nodes)},
        )
        self._snapshots[snapshot.snapshot_id] = snapshot
        return snapshot

    def get_snapshot(self, snapshot_id: str, tenant_id: str) -> TopologySnapshot:
        snap = self._snapshots.get(snapshot_id)
        if not snap:
            raise ImmutableTopologySnapshotException(snapshot_id=snapshot_id, tenant_id=tenant_id)
        if snap.tenant_id != tenant_id and tenant_id != "system":
            raise CrossTenantArchitectureAccessException(request_tenant=tenant_id, target_tenant=snap.tenant_id, resource_id=snapshot_id)
        return snap

    def list_snapshots(self, tenant_id: str, environment: Optional[str] = None) -> List[TopologySnapshot]:
        snaps = [s for s in self._snapshots.values() if s.tenant_id == tenant_id]
        if environment:
            snaps = [s for s in snaps if s.environment == environment]
        return snaps

    def compare_snapshots(self, snapshot_id_1: str, snapshot_id_2: str, tenant_id: str) -> Dict[str, Any]:
        s1 = self.get_snapshot(snapshot_id_1, tenant_id)
        s2 = self.get_snapshot(snapshot_id_2, tenant_id)

        set1 = set(s1.node_ids)
        set2 = set(s2.node_ids)

        return {
            "snapshot_1": s1.snapshot_id,
            "snapshot_2": s2.snapshot_id,
            "added_nodes": list(set2 - set1),
            "removed_nodes": list(set1 - set2),
            "retained_nodes": list(set1 & set2),
            "fingerprint_match": s1.architecture_fingerprint == s2.architecture_fingerprint,
        }
