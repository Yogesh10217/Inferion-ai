"""Human Experience & Escalation Engine (Phase 5.22 - Component 8).

Orchestrates human-in-the-loop experience & escalation by reusing:
- HumanTaskManager (app.orchestration.human_tasks)
- ApprovalEngine (app.approvals.approval_engine)

Triggers:
- LOW_CONFIDENCE, POLICY_REQUIREMENT, HIGH_RISK, EXPLICIT_USER_REQUEST, REPEATED_FAILURE, SAFETY_CONCERN, BUDGET_RESTRICTION
"""

import logging
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.orchestration.human_tasks import HumanTaskManager, HumanTask, TaskPriority, TaskStatus
from app.approvals.approval_engine import ApprovalEngine

logger = logging.getLogger(__name__)


class EscalationReason(str, Enum):
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    POLICY_REQUIREMENT = "POLICY_REQUIREMENT"
    HIGH_RISK = "HIGH_RISK"
    EXPLICIT_USER_REQUEST = "EXPLICIT_USER_REQUEST"
    REPEATED_FAILURE = "REPEATED_FAILURE"
    SAFETY_CONCERN = "SAFETY_CONCERN"
    BUDGET_RESTRICTION = "BUDGET_RESTRICTION"


class ExperienceAction(BaseModel):
    """Action requested during human intervention."""

    action_id: str = Field(default_factory=lambda: f"act_{uuid.uuid4().hex[:12]}")
    action_type: str = "REVIEW"
    actor_id: Optional[str] = None
    outcome: str = "PENDING"
    notes: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EscalationPolicy(BaseModel):
    """Escalation trigger policy."""

    policy_id: str = Field(default_factory=lambda: f"escpol_{uuid.uuid4().hex[:12]}")
    application_id: str
    tenant_id: str
    confidence_threshold: float = 0.70
    max_automated_retries: int = 3
    risk_level_trigger: str = "HIGH"
    auto_escalate_on_safety_warning: bool = True


class HumanEscalation(BaseModel):
    """Human escalation record."""

    escalation_id: str = Field(default_factory=lambda: f"esc_{uuid.uuid4().hex[:12]}")
    application_id: str
    execution_id: str
    tenant_id: str
    reason: EscalationReason
    human_task_id: Optional[str] = None
    approval_request_id: Optional[str] = None
    status: str = "OPEN"  # OPEN, RESOLVED, REJECTED, TIMED_OUT
    resolution_notes: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None


class HumanExperienceManager:
    """Manages human-in-the-loop experience escalations."""

    def __init__(
        self,
        human_task_manager: Optional[HumanTaskManager] = None,
        approval_engine: Optional[ApprovalEngine] = None,
    ) -> None:
        self.human_task_manager = human_task_manager or HumanTaskManager()
        self.approval_engine = approval_engine or ApprovalEngine()
        self._escalations: Dict[str, HumanEscalation] = {}

    def trigger_escalation(
        self,
        tenant_id: str,
        application_id: str,
        execution_id: str,
        reason: EscalationReason,
        details: str = "",
        assigned_group: str = "OPERATORS",
    ) -> HumanEscalation:
        """Trigger escalation by creating a HumanTask in HumanTaskManager."""
        task = self.human_task_manager.create_task(
            tenant_id=tenant_id,
            title=f"Application Escalation [{reason.value}] - App {application_id}",
            execution_id=execution_id,
            priority=TaskPriority.HIGH if reason in {EscalationReason.HIGH_RISK, EscalationReason.SAFETY_CONCERN} else TaskPriority.MEDIUM,
        )


        esc = HumanEscalation(
            application_id=application_id,
            execution_id=execution_id,
            tenant_id=tenant_id,
            reason=reason,
            human_task_id=task.task_id,
            status="OPEN",
        )
        self._escalations[esc.escalation_id] = esc
        logger.info(f"[HUMAN EXPERIENCE] Escalation {esc.escalation_id} created for execution {execution_id}: {reason.value}")
        return esc

    def resolve_escalation(
        self,
        escalation_id: str,
        resolution_notes: str = "",
        approved: bool = True,
        resolver_id: str = "operator",
    ) -> HumanEscalation:
        if escalation_id not in self._escalations:
            raise KeyError(f"Escalation '{escalation_id}' not found.")

        esc = self._escalations[escalation_id]
        if esc.human_task_id:
            try:
                self.human_task_manager.complete_task(
                    task_id=esc.human_task_id,
                    completed_by=resolver_id,
                    result={"approved": approved, "notes": resolution_notes},
                )
            except Exception as e:
                logger.warning(f"[HUMAN EXPERIENCE] Error completing human task {esc.human_task_id}: {e}")

        esc.status = "RESOLVED" if approved else "REJECTED"
        esc.resolution_notes = resolution_notes
        esc.resolved_at = datetime.now(timezone.utc)
        return esc

    def get_escalation(self, escalation_id: str) -> Optional[HumanEscalation]:
        return self._escalations.get(escalation_id)
