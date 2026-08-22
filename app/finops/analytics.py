"""Cost Analytics, Unit Economics & Cost Growth Intelligence Engine."""

from datetime import datetime, timezone
from decimal import Decimal
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, field_validator

from app.finops.cost_ledger import UnifiedCostLedger, CostCategory

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class CostCategoryBreakdown(BaseModel):
    category: str
    total_cost: Decimal

    @field_validator("total_cost", mode="before")
    @classmethod
    def parse_decimal(cls, value: Any) -> Decimal:
        if isinstance(value, float):
            return Decimal(str(value))
        return Decimal(value)


class CostAnalyticsReport(BaseModel):
    tenant_id: str
    total_cost: Decimal
    cost_by_category: List[CostCategoryBreakdown] = Field(default_factory=list)
    cost_per_execution: Decimal = Decimal("0.0")
    top_component: str = "GATEWAY"
    generated_at: datetime = Field(default_factory=_now)

    @field_validator("total_cost", "cost_per_execution", mode="before")
    @classmethod
    def parse_decimal(cls, value: Any) -> Decimal:
        if isinstance(value, float):
            return Decimal(str(value))
        return Decimal(value)


class CostAnalyticsEngine:
    """Provides financial reports, unit economics (cost per request/execution), and category breakdowns."""

    def __init__(self, ledger: Optional[UnifiedCostLedger] = None) -> None:
        self.ledger = ledger or UnifiedCostLedger()

    def generate_report(self, tenant_id: str = "global") -> CostAnalyticsReport:
        entries = self.ledger.list_entries(tenant_id=tenant_id)

        cat_totals: Dict[str, Decimal] = {}
        component_totals: Dict[str, Decimal] = {}

        total = Decimal("0.0")
        for e in entries:
            total += e.total_cost
            cat_str = e.cost_category.value if hasattr(e.cost_category, "value") else str(e.cost_category)
            cat_totals[cat_str] = cat_totals.get(cat_str, Decimal("0.0")) + e.total_cost
            component_totals[e.component] = component_totals.get(e.component, Decimal("0.0")) + e.total_cost

        breakdowns = [CostCategoryBreakdown(category=k, total_cost=v) for k, v in cat_totals.items()]
        top_comp = max(component_totals.items(), key=lambda x: x[1])[0] if component_totals else "GATEWAY"

        num_entries = len(entries)
        cost_per_exec = (total / Decimal(str(num_entries))) if num_entries > 0 else Decimal("0.0")

        rep = CostAnalyticsReport(
            tenant_id=tenant_id,
            total_cost=total.quantize(Decimal("0.000001")),
            cost_by_category=breakdowns,
            cost_per_execution=cost_per_exec.quantize(Decimal("0.000001")),
            top_component=top_comp,
        )
        logger.info(f"[COST ANALYTICS] Generated report for tenant '{tenant_id}': Total = ${total}")
        return rep
