"""Operational Runbook Intelligence (Phase 5.41)."""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.operations_intelligence.exceptions import CrossTenantOperationsAccessException


class RunbookRecommendation(BaseModel):
    recommendation_id: str = Field(default_factory=lambda: f"rb_rec_{uuid.uuid4().hex[:8]}")
    runbook_id: str
    target_service_id: str
    action_type: str
    confidence_score: float = 85.0
    reason: str


class RunbookExecutionPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: f"rb_plan_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    runbook_id: str
    action_type: str
    requires_approval: bool = True
    is_delegated: bool = False


class OperationalRunbook(BaseModel):
    runbook_id: str = Field(default_factory=lambda: f"rb_op_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    title: str
    description: str
    target_service_id: str
    action_type: str
    is_automated: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OperationalRunbookManager:
    """Manages operational runbook catalog and automated remediation recommendations."""

    def __init__(self) -> None:
        self._runbooks: Dict[str, OperationalRunbook] = {}

    def register_runbook(
        self,
        tenant_id: str,
        title: str,
        description: str,
        target_service_id: str,
        action_type: str,
    ) -> OperationalRunbook:
        rb = OperationalRunbook(
            tenant_id=tenant_id,
            title=title,
            description=description,
            target_service_id=target_service_id,
            action_type=action_type,
        )
        self._runbooks[rb.runbook_id] = rb
        return rb

    def recommend_runbook(
        self,
        tenant_id: str,
        service_id: str,
        incident_title: str,
    ) -> Optional[RunbookRecommendation]:
        service_rbs = [r for r in self._runbooks.values() if r.tenant_id == tenant_id and r.target_service_id == service_id]
        if not service_rbs:
            return None

        best_rb = service_rbs[0]
        return RunbookRecommendation(
            runbook_id=best_rb.runbook_id,
            target_service_id=service_id,
            action_type=best_rb.action_type,
            confidence_score=90.0,
            reason=f"Recommended runbook '{best_rb.title}' for incident '{incident_title}'",
        )

    def get_runbook(self, tenant_id: str, runbook_id: str) -> OperationalRunbook:
        rb = self._runbooks.get(runbook_id)
        if not rb or rb.tenant_id != tenant_id:
            raise CrossTenantOperationsAccessException()
        return rb
