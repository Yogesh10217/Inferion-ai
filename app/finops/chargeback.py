"""Internal Chargeback, Showback & Cost Allocation Reporting Subsystem."""

import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator

from app.finops.cost_ledger import UnifiedCostLedger

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ShowbackReport(BaseModel):
    tenant_id: str
    organization_id: Optional[str] = None
    workspace_id: Optional[str] = None
    direct_cost: Decimal
    allocated_shared_cost: Decimal
    total_cost: Decimal
    period: str = "MONTHLY"
    generated_at: datetime = Field(default_factory=_now)

    @field_validator("direct_cost", "allocated_shared_cost", "total_cost", mode="before")
    @classmethod
    def parse_decimal(cls, value: Any) -> Decimal:
        if isinstance(value, float):
            return Decimal(str(value))
        return Decimal(value)


class ChargebackManager:
    """Generates internal showback and chargeback cost allocation reports."""

    def __init__(self, ledger: Optional[UnifiedCostLedger] = None) -> None:
        self.ledger = ledger or UnifiedCostLedger()

    def generate_showback_report(self, tenant_id: str = "global") -> ShowbackReport:
        total = self.ledger.get_total_cost(tenant_id=tenant_id)
        shared = (total * Decimal("0.05")).quantize(Decimal("0.000001"))
        total_bill = (total + shared).quantize(Decimal("0.000001"))

        rep = ShowbackReport(
            tenant_id=tenant_id,
            direct_cost=total,
            allocated_shared_cost=shared,
            total_cost=total_bill,
        )
        logger.info(f"[CHARGEBACK MANAGER] Generated showback report for tenant '{tenant_id}': Total = ${total_bill}")
        return rep
