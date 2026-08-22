"""Extension Usage & Cost Attribution Tracker."""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.control_plane.usage_manager import ControlPlaneUsageManager

logger = logging.getLogger(__name__)


class ExtensionBillingRecord(BaseModel):
    """Cost attribution record for extension executions."""

    extension_id: str
    tenant_id: str = "global"
    organization_id: Optional[str] = None
    workspace_id: Optional[str] = None
    developer_project_id: Optional[str] = None
    total_executions: int = 0
    total_compute_seconds: float = 0.0
    total_memory_mb_seconds: float = 0.0
    total_tokens: int = 0
    total_cost_dollars: float = 0.0
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ExtensionBillingTracker:
    """Tracks extension cost metrics across the hierarchy (Platform -> Tenant -> Org -> Workspace -> Project -> Extension)."""

    def __init__(self, usage_manager: Optional[ControlPlaneUsageManager] = None) -> None:
        self.usage_manager = usage_manager or ControlPlaneUsageManager()
        self._records: Dict[str, ExtensionBillingRecord] = {}

    def record_extension_execution(
        self,
        extension_id: str,
        tenant_id: str = "global",
        organization_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        developer_project_id: Optional[str] = None,
        compute_seconds: float = 0.0,
        memory_mb_seconds: float = 0.0,
        tokens: int = 0,
        cost_dollars: float = 0.0,
    ) -> ExtensionBillingRecord:
        """Record extension execution into billing ledger and report to control plane telemetry."""
        key = f"{tenant_id}:{extension_id}"
        if key not in self._records:
            self._records[key] = ExtensionBillingRecord(
                extension_id=extension_id,
                tenant_id=tenant_id,
                organization_id=organization_id,
                workspace_id=workspace_id,
                developer_project_id=developer_project_id,
            )

        rec = self._records[key]
        rec.total_executions += 1
        rec.total_compute_seconds += compute_seconds
        rec.total_memory_mb_seconds += memory_mb_seconds
        rec.total_tokens += tokens
        rec.total_cost_dollars += cost_dollars
        rec.updated_at = datetime.now(timezone.utc)

        # Propagate to control plane usage aggregator
        self.usage_manager.record_event(
            tenant_id=tenant_id,
            organization_id=organization_id,
            workspace_id=workspace_id,
            requests=1,
            tokens=tokens,
            cost_dollars=cost_dollars,
        )

        return rec

    def get_billing_record(self, extension_id: str, tenant_id: str = "global") -> Optional[ExtensionBillingRecord]:
        return self._records.get(f"{tenant_id}:{extension_id}")
