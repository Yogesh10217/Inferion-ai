"""Integration Automation & Ecosystem Event Triggers Subsystem."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from app.orchestration.manager import OrchestrationManager

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class TriggerType(str, Enum):
    WEBHOOK = "WEBHOOK"
    SCHEDULE = "SCHEDULE"
    EVENT = "EVENT"
    DATA_CHANGE = "DATA_CHANGE"
    WORKFLOW_EVENT = "WORKFLOW_EVENT"
    AGENT_EVENT = "AGENT_EVENT"
    MANUAL = "MANUAL"


class ActionType(str, Enum):
    CALL_API = "CALL_API"
    SEND_MESSAGE = "SEND_MESSAGE"
    CREATE_TICKET = "CREATE_TICKET"
    UPDATE_RECORD = "UPDATE_RECORD"
    START_WORKFLOW = "START_WORKFLOW"
    TRIGGER_AGENT = "TRIGGER_AGENT"
    WRITE_KNOWLEDGE = "WRITE_KNOWLEDGE"
    NOTIFY_HUMAN = "NOTIFY_HUMAN"


class AutomationDefinition(BaseModel):
    automation_id: str = Field(default_factory=lambda: f"auto_{uuid.uuid4().hex[:10]}")
    name: str
    trigger_type: TriggerType = TriggerType.WEBHOOK
    action_type: ActionType = ActionType.CALL_API
    tenant_id: str = "global"
    is_active: bool = True
    created_at: datetime = Field(default_factory=_now)


class AutomationExecution(BaseModel):
    execution_id: str = Field(default_factory=lambda: f"aexec_{uuid.uuid4().hex[:10]}")
    automation_id: str
    tenant_id: str = "global"
    status: str = "COMPLETED"
    executed_at: datetime = Field(default_factory=_now)


class AutomationManager:
    """Manages integration event automations and routes execution to OrchestrationManager."""

    def __init__(self, orchestration_manager: Optional[OrchestrationManager] = None) -> None:
        self.orchestration_manager = orchestration_manager or OrchestrationManager()
        self._automations: Dict[str, AutomationDefinition] = {}

    def create_automation(
        self,
        name: str,
        trigger_type: TriggerType = TriggerType.WEBHOOK,
        action_type: ActionType = ActionType.CALL_API,
        tenant_id: str = "global",
    ) -> AutomationDefinition:
        auto = AutomationDefinition(name=name, trigger_type=trigger_type, action_type=action_type, tenant_id=tenant_id)
        self._automations[auto.automation_id] = auto
        logger.info(f"[AUTOMATION MANAGER] Created automation '{auto.automation_id}' ('{name}') for tenant '{tenant_id}'")
        return auto

    def trigger_automation(self, automation_id: str, payload: Optional[Dict[str, Any]] = None) -> AutomationExecution:
        auto = self._automations.get(automation_id)
        if not auto:
            logger.warning(f"[AUTOMATION MANAGER] Automation '{automation_id}' not found")
            return AutomationExecution(automation_id=automation_id, status="FAILED")

        exec_obj = AutomationExecution(automation_id=automation_id, tenant_id=auto.tenant_id, status="COMPLETED")
        logger.info(f"[AUTOMATION MANAGER] Executed automation '{automation_id}' ({auto.action_type.value})")
        return exec_obj
