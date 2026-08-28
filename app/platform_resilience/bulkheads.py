"""Workload Isolation Intelligence Subsystem (Phase 5.37)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantAccessGuard
from app.platform_resilience.exceptions import CrossTenantResilienceAccessException, BulkheadCapacityExceededException


class BulkheadStatus(str, Enum):
    HEALTHY = "HEALTHY"
    SATURATED = "SATURATED"
    EXHAUSTED = "EXHAUSTED"


class BulkheadCapacity(BaseModel):
    max_concurrent_calls: int = 50
    current_calls: int = 0
    max_queue_capacity: int = 100
    current_queue_depth: int = 0


class BulkheadPartition(BaseModel):
    partition_id: str = Field(default_factory=lambda: f"bhkpart_{uuid.uuid4().hex[:12]}")
    partition_name: str
    tenant_id: str
    capacity: BulkheadCapacity = Field(default_factory=BulkheadCapacity)
    status: BulkheadStatus = BulkheadStatus.HEALTHY


class BulkheadPolicy(BaseModel):
    policy_id: str = Field(default_factory=lambda: f"bhkpoly_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    partitions: Dict[str, BulkheadPartition] = Field(default_factory=dict)


class BulkheadAssessment(BaseModel):
    partition_id: str
    tenant_id: str
    status: BulkheadStatus = BulkheadStatus.HEALTHY
    is_capacity_available: bool = True


class BulkheadManager:
    """Workload Isolation Intelligence Manager protecting shared capacity from workload exhaustion."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._partitions: Dict[str, BulkheadPartition] = {}

    def configure_partition(
        self,
        tenant_id: str,
        partition_name: str,
        max_concurrent_calls: int = 50,
        max_queue_capacity: int = 100,
    ) -> BulkheadPartition:
        part = BulkheadPartition(
            partition_name=partition_name,
            tenant_id=tenant_id,
            capacity=BulkheadCapacity(
                max_concurrent_calls=max_concurrent_calls,
                max_queue_capacity=max_queue_capacity,
            ),
        )
        self._partitions[f"{tenant_id}:{partition_name}"] = part
        return part

    def acquire_capacity(self, tenant_id: str, partition_name: str) -> bool:
        part = self._partitions.get(f"{tenant_id}:{partition_name}")
        if not part:
            part = self.configure_partition(tenant_id, partition_name)

        if part.capacity.current_calls >= part.capacity.max_concurrent_calls:
            if part.capacity.current_queue_depth >= part.capacity.max_queue_capacity:
                part.status = BulkheadStatus.EXHAUSTED
                raise BulkheadCapacityExceededException(partition_name)
            part.capacity.current_queue_depth += 1
            part.status = BulkheadStatus.SATURATED
            return True

        part.capacity.current_calls += 1
        return True

    def release_capacity(self, tenant_id: str, partition_name: str) -> None:
        part = self._partitions.get(f"{tenant_id}:{partition_name}")
        if part:
            if part.capacity.current_calls > 0:
                part.capacity.current_calls -= 1
            elif part.capacity.current_queue_depth > 0:
                part.capacity.current_queue_depth -= 1
            if part.capacity.current_calls < part.capacity.max_concurrent_calls:
                part.status = BulkheadStatus.HEALTHY
