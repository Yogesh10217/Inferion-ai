"""Unified Immutable Cost Ledger with Fixed-Precision Monetary Calculations."""

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
import uuid
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, field_validator

from app.finops.exceptions import CostLedgerException

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class CostCategory(str, Enum):
    MODEL_INFERENCE = "MODEL_INFERENCE"
    TOKEN_USAGE = "TOKEN_USAGE"
    EMBEDDING = "EMBEDDING"
    RERANKING = "RERANKING"
    AGENT_EXECUTION = "AGENT_EXECUTION"
    WORKFLOW_EXECUTION = "WORKFLOW_EXECUTION"
    TOOL_EXECUTION = "TOOL_EXECUTION"
    MCP_EXECUTION = "MCP_EXECUTION"
    PLANNING = "PLANNING"
    REASONING = "REASONING"
    SIMULATION = "SIMULATION"
    AUTONOMOUS_WORKER = "AUTONOMOUS_WORKER"
    DIGITAL_WORKER = "DIGITAL_WORKER"
    DATA_INGESTION = "DATA_INGESTION"
    DATA_STORAGE = "DATA_STORAGE"
    DATA_SYNCHRONIZATION = "DATA_SYNCHRONIZATION"
    EXTENSION_EXECUTION = "EXTENSION_EXECUTION"
    EVALUATION = "EVALUATION"
    EXPERIMENT = "EXPERIMENT"
    DEPLOYMENT = "DEPLOYMENT"
    COMPUTE = "COMPUTE"
    MEMORY = "MEMORY"
    STORAGE = "STORAGE"
    NETWORK = "NETWORK"
    CACHE = "CACHE"
    BACKGROUND_JOB = "BACKGROUND_JOB"
    OTHER = "OTHER"


class CostLedgerEntry(BaseModel):
    """Immutable financial event entry recorded with Decimal precision."""

    cost_id: str = Field(default_factory=lambda: f"cost_{uuid.uuid4().hex[:12]}")
    timestamp: datetime = Field(default_factory=_now)

    tenant_id: str = "global"
    organization_id: Optional[str] = None
    workspace_id: Optional[str] = None
    project_id: Optional[str] = None
    resource_id: Optional[str] = None
    execution_id: Optional[str] = None

    component: str  # GATEWAY, TOOL, PLANNING, EXTENSION, DATA_FABRIC, MLOPS, WORKER, INFRASTRUCTURE
    provider: str = "internal"
    model_id: Optional[str] = None
    cost_category: CostCategory = CostCategory.MODEL_INFERENCE

    quantity: Decimal = Field(default=Decimal("1.0"))
    unit: str = "request"
    unit_price: Decimal = Field(default=Decimal("0.0"))
    total_cost: Decimal = Field(default=Decimal("0.0"))
    currency: str = "USD"
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("quantity", "unit_price", "total_cost", mode="before")
    @classmethod
    def parse_decimal(cls, value: Any) -> Decimal:
        if isinstance(value, float):
            return Decimal(str(value))
        return Decimal(value)


class CostAdjustment(BaseModel):
    """Adjustment entry for financial corrections without modifying historical cost entries."""

    adjustment_id: str = Field(default_factory=lambda: f"adj_{uuid.uuid4().hex[:12]}")
    original_cost_id: str
    tenant_id: str = "global"
    adjustment_amount: Decimal
    reason: str
    created_at: datetime = Field(default_factory=_now)

    @field_validator("adjustment_amount", mode="before")
    @classmethod
    def parse_decimal(cls, value: Any) -> Decimal:
        if isinstance(value, float):
            return Decimal(str(value))
        return Decimal(value)


class UnifiedCostLedger:
    """Central append-only financial ledger enforcing Decimal arithmetic and immutable history."""

    def __init__(self) -> None:
        self._entries: List[CostLedgerEntry] = []
        self._adjustments: List[CostAdjustment] = []

    def record_cost(
        self,
        component: str,
        cost_category: CostCategory,
        quantity: Decimal,
        unit_price: Decimal,
        tenant_id: str = "global",
        organization_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        project_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        provider: str = "internal",
        model_id: Optional[str] = None,
        unit: str = "units",
        currency: str = "USD",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> CostLedgerEntry:
        qty = Decimal(str(quantity)) if isinstance(quantity, (float, int, str)) else quantity
        price = Decimal(str(unit_price)) if isinstance(unit_price, (float, int, str)) else unit_price
        total = (qty * price).quantize(Decimal("0.000001"))

        entry = CostLedgerEntry(
            component=component,
            cost_category=cost_category,
            quantity=qty,
            unit_price=price,
            total_cost=total,
            tenant_id=tenant_id,
            organization_id=organization_id,
            workspace_id=workspace_id,
            project_id=project_id,
            resource_id=resource_id,
            execution_id=execution_id,
            provider=provider,
            model_id=model_id,
            unit=unit,
            currency=currency,
            metadata=metadata or {},
        )
        self._entries.append(entry)
        logger.info(f"[COST LEDGER] Recorded immutable cost entry '{entry.cost_id}': ${total} ({component}/{cost_category.value})")
        return entry

    def record_adjustment(self, original_cost_id: str, adjustment_amount: Decimal, reason: str, tenant_id: str = "global") -> CostAdjustment:
        adj_amt = Decimal(str(adjustment_amount)) if isinstance(adjustment_amount, (float, int, str)) else adjustment_amount
        adj = CostAdjustment(original_cost_id=original_cost_id, tenant_id=tenant_id, adjustment_amount=adj_amt, reason=reason)
        self._adjustments.append(adj)
        logger.info(f"[COST LEDGER] Recorded adjustment '{adj.adjustment_id}' for cost '{original_cost_id}': ${adj_amt}")
        return adj

    def list_entries(self, tenant_id: Optional[str] = None, component: Optional[str] = None) -> List[CostLedgerEntry]:
        res = self._entries
        if tenant_id:
            res = [e for e in res if e.tenant_id == tenant_id]
        if component:
            res = [e for e in res if e.component == component]
        return res

    def get_total_cost(self, tenant_id: Optional[str] = None) -> Decimal:
        entries = self.list_entries(tenant_id=tenant_id)
        base_cost = sum((e.total_cost for e in entries), Decimal("0.0"))

        adjustments = self._adjustments
        if tenant_id:
            adjustments = [a for a in adjustments if a.tenant_id == tenant_id]
        adj_cost = sum((a.adjustment_amount for a in adjustments), Decimal("0.0"))

        return (base_cost + adj_cost).quantize(Decimal("0.000001"))
