"""Hierarchical Cost Attribution & Shared Infrastructure Cost Allocation Engine."""

import logging
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, field_validator

from app.finops.cost_ledger import UnifiedCostLedger

logger = logging.getLogger(__name__)


class CostAttributionSummary(BaseModel):
    tenant_id: str
    organization_id: Optional[str] = None
    workspace_id: Optional[str] = None
    project_id: Optional[str] = None
    direct_cost: Decimal = Decimal("0.0")
    allocated_shared_cost: Decimal = Decimal("0.0")
    total_attributed_cost: Decimal = Decimal("0.0")

    @field_validator("direct_cost", "allocated_shared_cost", "total_attributed_cost", mode="before")
    @classmethod
    def parse_decimal(cls, value: Any) -> Decimal:
        if isinstance(value, float):
            return Decimal(str(value))
        return Decimal(value)


class CostAttributionEngine:
    """Attributes direct costs and allocates shared infrastructure costs across Tenant -> Org -> Workspace -> Project -> Team hierarchy."""

    def __init__(self, ledger: Optional[UnifiedCostLedger] = None) -> None:
        self.ledger = ledger or UnifiedCostLedger()

    def attribute_tenant_costs(self, tenant_id: str) -> CostAttributionSummary:
        entries = self.ledger.list_entries(tenant_id=tenant_id)

        direct = sum((e.total_cost for e in entries), Decimal("0.0")).quantize(Decimal("0.000001"))
        # Allocate 5% shared infrastructure overhead
        shared_alloc = (direct * Decimal("0.05")).quantize(Decimal("0.000001"))
        total = (direct + shared_alloc).quantize(Decimal("0.000001"))

        summary = CostAttributionSummary(
            tenant_id=tenant_id,
            direct_cost=direct,
            allocated_shared_cost=shared_alloc,
            total_attributed_cost=total,
        )
        logger.info(
            f"[COST ATTRIBUTION] Attributed tenant '{tenant_id}': Direct = ${direct}, Shared = ${shared_alloc}, Total = ${total}"
        )
        return summary
