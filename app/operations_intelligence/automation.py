"""Governed Operational Automation Intelligence (Phase 5.41)."""

import uuid
from typing import Dict

from pydantic import BaseModel, Field


class AutomationPolicy(BaseModel):
    policy_id: str = Field(default_factory=lambda: f"auto_pol_{uuid.uuid4().hex[:8]}")
    name: str
    max_auto_remediations_per_hour: int = 5
    requires_human_approval_for_high_risk: bool = True


class AutomationDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: f"auto_dec_{uuid.uuid4().hex[:8]}")
    tenant_id: str
    action_name: str
    is_automated_execution_permitted: bool = True
    requires_approval: bool = False
    reason: str = ""


class OperationalAutomation(BaseModel):
    automation_id: str = Field(default_factory=lambda: f"auto_op_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    name: str
    action_type: str
    is_enabled: bool = True


class OperationalAutomationManager:
    """Manages operational automation policy evaluation and execution boundaries."""

    def __init__(self) -> None:
        self._automations: Dict[str, OperationalAutomation] = {}

    def evaluate_automation(
        self,
        tenant_id: str,
        action_name: str,
        is_high_risk: bool = False,
    ) -> AutomationDecision:
        if is_high_risk:
            return AutomationDecision(
                tenant_id=tenant_id,
                action_name=action_name,
                is_automated_execution_permitted=False,
                requires_approval=True,
                reason=f"High-risk operational action '{action_name}' requires explicit human approval.",
            )

        return AutomationDecision(
            tenant_id=tenant_id,
            action_name=action_name,
            is_automated_execution_permitted=True,
            requires_approval=False,
            reason=f"Standard operational action '{action_name}' permitted under automation policy.",
        )
