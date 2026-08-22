"""Data Fabric Cost Attribution & Billing Tracker."""

from datetime import datetime, timezone
import uuid
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class DataFabricBillingRecord(BaseModel):
    record_id: str = Field(default_factory=lambda: f"bill_df_{uuid.uuid4().hex[:10]}")
    source_id: str
    tenant_id: str = "global"
    organization_id: Optional[str] = None
    workspace_id: Optional[str] = None

    connector_api_requests: int = 0
    records_ingested: int = 0
    compute_seconds: float = 0.0
    cost_dollars: float = 0.0

    recorded_at: datetime = Field(default_factory=_now)


class DataFabricBillingTracker:
    """Tracks storage, compute, API requests, and synchronization costs across the hierarchy."""

    def __init__(self) -> None:
        self._records: List[DataFabricBillingRecord] = []

    def record_usage(
        self,
        source_id: str,
        tenant_id: str = "global",
        organization_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        connector_api_requests: int = 1,
        records_ingested: int = 0,
        compute_seconds: float = 0.0,
        cost_dollars: float = 0.0,
    ) -> DataFabricBillingRecord:
        rec = DataFabricBillingRecord(
            source_id=source_id,
            tenant_id=tenant_id,
            organization_id=organization_id,
            workspace_id=workspace_id,
            connector_api_requests=connector_api_requests,
            records_ingested=records_ingested,
            compute_seconds=compute_seconds,
            cost_dollars=cost_dollars,
        )
        self._records.append(rec)
        logger.info(f"[DATA FABRIC BILLING] Recorded {records_ingested} records ingested for source '{source_id}' (${cost_dollars:.4f})")
        return rec

    def get_tenant_total_cost(self, tenant_id: str) -> float:
        return sum(r.cost_dollars for r in self._records if r.tenant_id == tenant_id)
