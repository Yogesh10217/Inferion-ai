"""
Message Bus & Agent-to-Agent Communication Subsystem
"""

import asyncio
import logging
import time
import uuid
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    TASK = "TASK"
    RESULT = "RESULT"
    QUESTION = "QUESTION"
    ANSWER = "ANSWER"
    STATUS = "STATUS"
    ERROR = "ERROR"
    ESCALATION = "ESCALATION"
    APPROVAL = "APPROVAL"


class AgentMessage(BaseModel):
    message_id: str = Field(default_factory=lambda: f"msg_{uuid.uuid4().hex[:10]}")
    sender_id: str
    recipient_id: str  # specific agent_id or '*' for broadcast
    message_type: MessageType = MessageType.TASK
    content: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    tenant_id: str = "default_tenant"
    team_id: str = "default_team"
    trace_id: Optional[str] = None
    timestamp: float = Field(default_factory=time.time)


class MessageBus:
    """Async Message Bus enabling peer-to-peer and broadcast messaging between agents."""

    def __init__(self):
        self._subscriptions: Dict[str, List[Callable]] = {}
        self._history: Dict[str, List[AgentMessage]] = {}  # team_id -> list of messages

    def subscribe(self, agent_id: str, callback: Callable[[AgentMessage], None]) -> None:
        if agent_id not in self._subscriptions:
            self._subscriptions[agent_id] = []
        self._subscriptions[agent_id].append(callback)

    async def publish(self, message: AgentMessage) -> None:
        team_id = message.team_id
        if team_id not in self._history:
            self._history[team_id] = []
        self._history[team_id].append(message)

        logger.debug(
            f"[BUS] Msg '{message.message_id}' ({message.message_type.value}) from {message.sender_id} -> {message.recipient_id}"
        )

        # Broadcast
        if message.recipient_id == "*":
            for aid, callbacks in self._subscriptions.items():
                for cb in callbacks:
                    if asyncio.iscoroutinefunction(cb):
                        await cb(message)
                    else:
                        cb(message)
        else:
            # Directed
            callbacks = self._subscriptions.get(message.recipient_id, [])
            for cb in callbacks:
                if asyncio.iscoroutinefunction(cb):
                    await cb(message)
                else:
                    cb(message)

    def get_team_history(self, team_id: str, limit: int = 100) -> List[AgentMessage]:
        return self._history.get(team_id, [])[-limit:]
