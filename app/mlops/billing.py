"""MLOps Cost Tracking & Billing Hierarchy Subsystem."""

from datetime import datetime, timezone
import uuid
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class MLOpsBillingRecord(BaseModel):
    record_id: str = Field(default_factory=lambda: f"ml_bill_{uuid.uuid4().hex[:10]}")
    tenant_id: str = "global"
    organization_id: Optional[str] = None
    workspace_id: Optional[str] = None
    project_id: Optional[str] = None

    asset_id: Optional[str] = None
    version_number: Optional[str] = None
    deployment_id: Optional[str] = None

    operation: str  # EVALUATION, EXPERIMENT, INFERENCE, SHADOW_TRAFFIC, STORAGE, ROLLBACK
    cost_dollars: float = 0.0
    recorded_at: datetime = Field(default_factory=_now)


class MLOpsBillingTracker:
    """Tracks costs across MLOps operations in accordance with Tenant -> Org -> Workspace -> Project -> Asset -> Version -> Deployment hierarchy."""

    def __init__(self) -> None:
        self._records: List[MLOpsBillingRecord] = []

    def track_cost(
        self,
        tenant_id: str,
        operation: str,
        cost_dollars: float,
        organization_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        project_id: Optional[str] = None,
        asset_id: Optional[str] = None,
        version_number: Optional[str] = None,
        deployment_id: Optional[str] = None,
    ) -> MLOpsBillingRecord:
        rec = MLOpsBillingRecord(
            tenant_id=tenant_id,
            organization_id=organization_id,
            workspace_id=workspace_id,
            project_id=project_id,
            asset_id=asset_id,
            version_number=version_number,
            deployment_id=deployment_id,
            operation=operation,
            cost_dollars=cost_dollars,
        )
        self._records.append(rec)
        logger.info(f"[MLOPS BILLING] Recorded cost ${cost_dollars:.6f} for operation '{operation}' (Tenant: {tenant_id})")
        return rec

    def get_total_cost(self, tenant_id: Optional[str] = None, asset_id: Optional[str] = None) -> float:
        recs = self._records
        if tenant_id:
            recs = [r for r in recs if r.tenant_id == tenant_id]
        if asset_id:
            recs = [r for r in recs if r.asset_id == asset_id]
        return sum(r.cost_dollars for r in recs)
