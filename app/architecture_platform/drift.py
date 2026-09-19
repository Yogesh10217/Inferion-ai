"""Auditable Architecture Drift Detector Subsystem."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field

from app.architecture_platform.nodes import ArchitectureNodeManager
from app.architecture_platform.topology import TopologyManager


class DriftType(str, Enum):
    MISSING_NODE = "MISSING_NODE"
    UNEXPECTED_NODE = "UNEXPECTED_NODE"
    MISSING_DEPENDENCY = "MISSING_DEPENDENCY"
    UNEXPECTED_DEPENDENCY = "UNEXPECTED_DEPENDENCY"
    VERSION_DRIFT = "VERSION_DRIFT"
    CONFIGURATION_DRIFT = "CONFIGURATION_DRIFT"
    TOPOLOGY_DRIFT = "TOPOLOGY_DRIFT"
    GOVERNANCE_DRIFT = "GOVERNANCE_DRIFT"
    DATA_FLOW_DRIFT = "DATA_FLOW_DRIFT"


class DriftSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DriftStatus(str, Enum):
    OPEN = "OPEN"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    REMEDIATING = "REMEDIATING"
    RESOLVED = "RESOLVED"


class ArchitectureDrift(BaseModel):
    drift_id: str = Field(default_factory=lambda: f"drift_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    drift_type: DriftType
    severity: DriftSeverity = DriftSeverity.MEDIUM
    status: DriftStatus = DriftStatus.OPEN
    expected_snapshot_reference: str
    observed_state_reference: str
    affected_nodes: List[str] = Field(default_factory=list)
    affected_dependencies: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    audit_reference: str = Field(default_factory=lambda: f"audit_{uuid.uuid4().hex[:12]}")
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ArchitectureDriftDetector:
    """Detects architectural drift by comparing immutable snapshots against observed live state."""

    def __init__(self, topology_manager: TopologyManager, node_manager: ArchitectureNodeManager) -> None:
        self.topology_manager = topology_manager
        self.node_manager = node_manager
        self._drift_records: Dict[str, List[ArchitectureDrift]] = {}

    def detect_drift(
        self, tenant_id: str, snapshot_id: str, environment: str = "production"
    ) -> List[ArchitectureDrift]:
        snapshot = self.topology_manager.get_snapshot(snapshot_id, tenant_id)
        current_topology = self.topology_manager.build_topology(tenant_id, environment)

        expected_nodes = set(snapshot.node_ids)
        observed_nodes = set(current_topology.nodes.keys())

        drifts: List[ArchitectureDrift] = []

        # 1. Missing Nodes
        missing = expected_nodes - observed_nodes
        if missing:
            drifts.append(
                ArchitectureDrift(
                    tenant_id=tenant_id,
                    drift_type=DriftType.MISSING_NODE,
                    severity=DriftSeverity.HIGH,
                    expected_snapshot_reference=snapshot.snapshot_id,
                    observed_state_reference=current_topology.topology_id,
                    affected_nodes=list(missing),
                    evidence=[f"Expected node '{nid}' missing in observed topology." for nid in missing],
                )
            )

        # 2. Unexpected / Unauthorized Nodes
        unexpected = observed_nodes - expected_nodes
        if unexpected:
            drifts.append(
                ArchitectureDrift(
                    tenant_id=tenant_id,
                    drift_type=DriftType.UNEXPECTED_NODE,
                    severity=DriftSeverity.HIGH,
                    expected_snapshot_reference=snapshot.snapshot_id,
                    observed_state_reference=current_topology.topology_id,
                    affected_nodes=list(unexpected),
                    evidence=[
                        f"Observed unauthorized/unexpected node '{nid}' not present in baseline snapshot."
                        for nid in unexpected
                    ],
                )
            )

        if tenant_id not in self._drift_records:
            self._drift_records[tenant_id] = []
        self._drift_records[tenant_id].extend(drifts)
        return drifts

    def list_drifts(self, tenant_id: str) -> List[ArchitectureDrift]:
        return self._drift_records.get(tenant_id, [])
