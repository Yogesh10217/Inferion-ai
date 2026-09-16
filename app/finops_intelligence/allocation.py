"""Cost Allocation Intelligence (Phase 5.42)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field

from app.finops_intelligence.exceptions import CrossTenantFinOpsIntelligenceException


class AllocationDimension(str, Enum):
    TENANT = "TENANT"
    ORGANIZATION = "ORGANIZATION"
    TEAM = "TEAM"
    PROJECT = "PROJECT"
    APPLICATION = "APPLICATION"
    MODEL = "MODEL"
    AGENT = "AGENT"
    WORKFLOW = "WORKFLOW"
    ENVIRONMENT = "ENVIRONMENT"


class AllocationRule(BaseModel):
    rule_id: str = Field(default_factory=lambda: f"alloc_rule_{uuid.uuid4().hex[:8]}")
    dimension: AllocationDimension
    target_entity: str
    percentage: float = 100.0


class AllocationResult(BaseModel):
    result_id: str = Field(default_factory=lambda: f"alloc_res_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    cost_record_id: str
    dimension: AllocationDimension
    target_entity: str
    allocated_amount_usd: float


class CostAllocation(BaseModel):
    allocation_id: str = Field(default_factory=lambda: f"alloc_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    cost_record_id: str
    rules: List[AllocationRule] = Field(default_factory=list)
    allocated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CostAllocationManager:
    """Manages cost allocation across organizational and application dimensions."""

    def __init__(self) -> None:
        self._allocations: Dict[str, CostAllocation] = {}

    def allocate_cost(
        self,
        tenant_id: str,
        cost_record_id: str,
        total_amount_usd: float,
        rules: List[AllocationRule],
    ) -> List[AllocationResult]:
        alloc = CostAllocation(
            tenant_id=tenant_id,
            cost_record_id=cost_record_id,
            rules=rules,
        )
        self._allocations[alloc.allocation_id] = alloc

        results: List[AllocationResult] = []
        for r in rules:
            amt = round(total_amount_usd * (r.percentage / 100.0), 4)
            results.append(
                AllocationResult(
                    tenant_id=tenant_id,
                    cost_record_id=cost_record_id,
                    dimension=r.dimension,
                    target_entity=r.target_entity,
                    allocated_amount_usd=amt,
                )
            )
        return results

    def get_allocation(self, tenant_id: str, allocation_id: str) -> CostAllocation:
        alloc = self._allocations.get(allocation_id)
        if not alloc or alloc.tenant_id != tenant_id:
            raise CrossTenantFinOpsIntelligenceException()
        return alloc
