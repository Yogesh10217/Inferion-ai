"""
Decision Remediation Subsystem.
Constructs remediation plans for non-compliant or high-risk decision options before delegation.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class DecisionRemediationPlan(BaseModel):
    remediation_id: str = Field(default_factory=lambda: f"remed_{uuid.uuid4().hex[:12]}")
    decision_id: str
    tenant_id: str
    target_option_id: str
    remediation_steps: List[str] = Field(default_factory=list)
    status: str = "PROPOSED"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DecisionRemediationEngine:
    """Constructs remediation plans for decision options."""

    def __init__(self) -> None:
        self._plans: Dict[str, DecisionRemediationPlan] = {}

    def create_remediation_plan(
        self, decision_id: str, tenant_id: str, target_option_id: str, steps: Optional[List[str]] = None
    ) -> DecisionRemediationPlan:
        plan = DecisionRemediationPlan(
            decision_id=decision_id,
            tenant_id=tenant_id,
            target_option_id=target_option_id,
            remediation_steps=steps or ["Enforce encryption at rest", "Add secondary approval step"],
        )
        self._plans[decision_id] = plan
        return plan

    def get_remediation_plan(self, decision_id: str) -> Optional[DecisionRemediationPlan]:
        return self._plans.get(decision_id)
