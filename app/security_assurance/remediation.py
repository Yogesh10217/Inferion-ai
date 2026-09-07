"""Security Remediation Planner."""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field


class SecurityRemediationPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: f"remed-plan-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    incident_id: str
    actions: List[str] = Field(default_factory=list)
    status: str = "PLANNED"  # PLANNED, IN_PROGRESS, COMPLETED
    idempotency_key: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SecurityRemediationPlanner:
    """Plans remediation steps for security incidents and findings."""

    def __init__(self) -> None:
        self._plans: Dict[str, SecurityRemediationPlan] = {}
        self._idempotency_map: Dict[str, str] = {}

    def create_plan(
        self,
        tenant_id: str,
        incident_id: str,
        actions: List[str],
        idempotency_key: Optional[str] = None,
    ) -> SecurityRemediationPlan:
        if idempotency_key and idempotency_key in self._idempotency_map:
            plan_id = self._idempotency_map[idempotency_key]
            return self._plans[plan_id]

        plan = SecurityRemediationPlan(
            tenant_id=tenant_id,
            incident_id=incident_id,
            actions=actions,
            idempotency_key=idempotency_key,
        )
        self._plans[plan.plan_id] = plan
        if idempotency_key:
            self._idempotency_map[idempotency_key] = plan.plan_id
        return plan

    def get_plan(self, tenant_id: str, plan_id: str) -> SecurityRemediationPlan:
        return self._plans[plan_id]
