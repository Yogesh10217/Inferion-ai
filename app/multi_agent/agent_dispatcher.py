"""
Agent Task Event Dispatcher
"""

import logging
from typing import Dict, Any, Optional

from app.multi_agent.agent_messaging import MessageBus, AgentMessage, MessageType

logger = logging.getLogger(__name__)


class AgentDispatcher:
    """Dispatches task requests and execution signals to team members."""

    def __init__(self, message_bus: MessageBus):
        self.bus = message_bus

    async def dispatch_task(
        self,
        sender_id: str,
        recipient_id: str,
        task_prompt: str,
        team_id: str,
        tenant_id: str = "default_tenant",
        payload: Optional[Dict[str, Any]] = None,
    ) -> AgentMessage:
        msg = AgentMessage(
            sender_id=sender_id,
            recipient_id=recipient_id,
            message_type=MessageType.TASK,
            content=task_prompt,
            payload=payload or {},
            team_id=team_id,
            tenant_id=tenant_id,
        )
        await self.bus.publish(msg)
        return msg
