"""Unified Enterprise Cost Intelligence (Phase 5.42)."""

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.finops.cost_ledger import CostCategory as PlatformCostCategory
from app.finops.cost_ledger import UnifiedCostLedger
from app.finops_intelligence.exceptions import CrossTenantFinOpsIntelligenceException


class CostCategory(str, Enum):
    MODEL_INFERENCE = "MODEL_INFERENCE"
    MODEL_TRAINING = "MODEL_TRAINING"
    AGENT_EXECUTION = "AGENT_EXECUTION"
    INTEGRATION = "INTEGRATION"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    STORAGE = "STORAGE"
    OPERATIONS = "OPERATIONS"
    RESILIENCE = "RESILIENCE"


class CostDimension(BaseModel):
    key: str
    value: str


class CostAggregation(BaseModel):
    tenant_id: str
    category: Optional[CostCategory] = None
    total_cost_usd: float = 0.0
    record_count: int = 0


class CostIntelligenceRecord(BaseModel):
    record_id: str = Field(default_factory=lambda: f"cost_rec_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    category: CostCategory = CostCategory.MODEL_INFERENCE
    amount_usd: float = 0.0
    dimensions: List[CostDimension] = Field(default_factory=list)
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CostIntelligenceManager:
    """Manages unified cost recording and aggregation, delegating to UnifiedCostLedger."""

    def __init__(self) -> None:
        self._records: Dict[str, CostIntelligenceRecord] = {}
        self.cost_ledger = UnifiedCostLedger()

    def record_cost(
        self,
        tenant_id: str,
        category: CostCategory,
        amount_usd: float,
        dimensions: Optional[List[CostDimension]] = None,
    ) -> CostIntelligenceRecord:
        rec = CostIntelligenceRecord(
            tenant_id=tenant_id,
            category=category,
            amount_usd=amount_usd,
            dimensions=dimensions or [],
        )
        self._records[rec.record_id] = rec

        # Delegate cost to platform UnifiedCostLedger
        plat_cat = PlatformCostCategory.MODEL_INFERENCE
        if category == CostCategory.AGENT_EXECUTION:
            plat_cat = PlatformCostCategory.WORKFLOW_EXECUTION
        elif category in [CostCategory.INFRASTRUCTURE, CostCategory.STORAGE]:
            plat_cat = PlatformCostCategory.COMPUTE

        self.cost_ledger.record_cost(
            component="FINOPS_INTELLIGENCE",
            cost_category=plat_cat,
            quantity=Decimal("1.0"),
            unit_price=Decimal(str(amount_usd)),
            tenant_id=tenant_id,
            metadata={"record_id": rec.record_id, "finops_category": category.value},
        )
        return rec

    def aggregate_costs(self, tenant_id: str, category: Optional[CostCategory] = None) -> CostAggregation:
        matching = [r for r in self._records.values() if r.tenant_id == tenant_id]
        if category:
            matching = [r for r in matching if r.category == category]

        total = sum(r.amount_usd for r in matching)
        return CostAggregation(
            tenant_id=tenant_id,
            category=category,
            total_cost_usd=round(total, 4),
            record_count=len(matching),
        )

    def get_record(self, tenant_id: str, record_id: str) -> CostIntelligenceRecord:
        rec = self._records.get(record_id)
        if not rec or rec.tenant_id != tenant_id:
            raise CrossTenantFinOpsIntelligenceException()
        return rec

    def list_records(self, tenant_id: str) -> List[CostIntelligenceRecord]:
        return [r for r in self._records.values() if r.tenant_id == tenant_id]
