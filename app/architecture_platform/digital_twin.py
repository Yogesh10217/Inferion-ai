"""Reference-Based Enterprise AI System Digital Twin Subsystem."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.architecture_platform.exceptions import DigitalTwinSynchronizationException, CrossTenantArchitectureAccessException


class TwinSynchronizationStatus(str, Enum):
    OBSERVED = "OBSERVED"
    STALE = "STALE"
    UNKNOWN = "UNKNOWN"
    SYNCHRONIZATION_FAILED = "SYNCHRONIZATION_FAILED"


class DigitalTwinState(BaseModel):
    operational_state_ref: str = "HEALTHY"
    cost_summary_usd: float = 0.0
    risk_level_ref: str = "LOW"
    data_trust_score_ref: float = 90.0
    architecture_trust_score: float = 90.0
    last_synced_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    sync_status: TwinSynchronizationStatus = TwinSynchronizationStatus.OBSERVED


class DigitalTwinSnapshot(BaseModel):
    snapshot_id: str = Field(default_factory=lambda: f"twinsnap_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    topology_snapshot_id: str
    state: DigitalTwinState
    node_count: int = 0
    dependency_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ArchitectureDigitalTwin(BaseModel):
    twin_id: str = Field(default_factory=lambda: f"twin_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    environment: str = "production"
    topology_reference_id: str
    state: DigitalTwinState = Field(default_factory=DigitalTwinState)
    synced_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DigitalTwinManager:
    """Manages reference-based digital twins by synchronizing pointers to existing managers."""

    def __init__(self) -> None:
        self._twins: Dict[str, Dict[str, ArchitectureDigitalTwin]] = {}  # tenant_id -> {env -> ArchitectureDigitalTwin}

        self._twin_snapshots: Dict[str, DigitalTwinSnapshot] = {}

    def get_or_create_twin(self, tenant_id: str, environment: str = "production", topology_ref_id: str = "latest") -> ArchitectureDigitalTwin:
        if tenant_id not in self._twins:
            self._twins[tenant_id] = {}

        if environment not in self._twins[tenant_id]:
            twin = ArchitectureDigitalTwin(
                tenant_id=tenant_id,
                environment=environment,
                topology_reference_id=topology_ref_id,
            )
            self._twins[tenant_id][environment] = twin
        return self._twins[tenant_id][environment]

    def synchronize_twin(
        self,
        tenant_id: str,
        environment: str = "production",
        operational_state_ref: str = "HEALTHY",
        cost_usd: float = 0.0,
        risk_level: str = "LOW",
        data_trust_score: float = 90.0,
        architecture_trust_score: float = 90.0,
        fail_sync: bool = False,
    ) -> ArchitectureDigitalTwin:
        twin = self.get_or_create_twin(tenant_id, environment)

        if fail_sync:
            twin.state.sync_status = TwinSynchronizationStatus.SYNCHRONIZATION_FAILED
            raise DigitalTwinSynchronizationException(
                f"Digital Twin synchronization failed for tenant '{tenant_id}' in environment '{environment}'.",
                tenant_id=tenant_id,
            )

        twin.state.operational_state_ref = operational_state_ref
        twin.state.cost_summary_usd = cost_usd
        twin.state.risk_level_ref = risk_level
        twin.state.data_trust_score_ref = data_trust_score
        twin.state.architecture_trust_score = architecture_trust_score
        twin.state.last_synced_at = datetime.now(timezone.utc)
        twin.state.sync_status = TwinSynchronizationStatus.OBSERVED
        twin.synced_at = datetime.now(timezone.utc)
        return twin

    def detect_twin_drift(self, tenant_id: str, environment: str = "production") -> Dict[str, Any]:
        twin = self.get_or_create_twin(tenant_id, environment)
        age_seconds = (datetime.now(timezone.utc) - twin.state.last_synced_at).total_seconds()

        is_stale = age_seconds > 3600  # Stale if not synced in 1 hour
        if is_stale and twin.state.sync_status == TwinSynchronizationStatus.OBSERVED:
            twin.state.sync_status = TwinSynchronizationStatus.STALE

        has_drift = (
            twin.state.sync_status in (TwinSynchronizationStatus.STALE, TwinSynchronizationStatus.SYNCHRONIZATION_FAILED)
            or twin.state.operational_state_ref in ("DEGRADED", "UNHEALTHY", "FAILED")
            or twin.state.risk_level_ref in ("HIGH", "CRITICAL")
        )

        return {
            "tenant_id": tenant_id,
            "environment": environment,
            "has_twin_drift": has_drift,
            "sync_status": twin.state.sync_status.value,
            "age_seconds": age_seconds,
            "operational_state": twin.state.operational_state_ref,
            "risk_level": twin.state.risk_level_ref,
        }
