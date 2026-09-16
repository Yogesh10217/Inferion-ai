"""Organizational Memory Governance & Scope Isolation Subsystem."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.knowledge_platform.exceptions import KnowledgeAccessDeniedException, MemoryNotFoundException
from app.memory.memory_manager import MemoryManager as BaseMemoryManager

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class MemoryType(str, Enum):
    EPISODIC = "EPISODIC"
    SEMANTIC = "SEMANTIC"
    PROCEDURAL = "PROCEDURAL"
    WORKING = "WORKING"
    AGENT = "AGENT"
    TEAM = "TEAM"
    WORKFLOW = "WORKFLOW"
    ORGANIZATIONAL = "ORGANIZATIONAL"
    USER_PREFERENCE = "USER_PREFERENCE"
    TASK = "TASK"


class MemoryScope(str, Enum):
    SESSION = "SESSION"
    USER = "USER"
    AGENT = "AGENT"
    TEAM = "TEAM"
    WORKFLOW = "WORKFLOW"
    PROJECT = "PROJECT"
    WORKSPACE = "WORKSPACE"
    ORGANIZATION = "ORGANIZATION"
    TENANT = "TENANT"


class Memory(BaseModel):
    memory_id: str = Field(default_factory=lambda: f"mem_{uuid.uuid4().hex[:10]}")
    key: str
    value: Any
    memory_type: MemoryType = MemoryType.ORGANIZATIONAL
    scope: MemoryScope = MemoryScope.TENANT

    tenant_id: str = "global"
    owner_agent_id: Optional[str] = None
    confidence_score: float = 1.0

    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


class MemoryManager:
    """Manages organizational memory governance, scope boundaries, and cross-agent memory isolation."""

    def __init__(self, base_memory_manager: Optional[BaseMemoryManager] = None) -> None:
        self.base_memory_manager = base_memory_manager or BaseMemoryManager()
        self._memories: Dict[str, Memory] = {}

    def store_memory(
        self,
        key: str,
        value: Any,
        memory_type: MemoryType = MemoryType.ORGANIZATIONAL,
        scope: MemoryScope = MemoryScope.TENANT,
        tenant_id: str = "global",
        owner_agent_id: Optional[str] = None,
    ) -> Memory:
        mem = Memory(
            key=key,
            value=value,
            memory_type=memory_type,
            scope=scope,
            tenant_id=tenant_id,
            owner_agent_id=owner_agent_id,
        )
        self._memories[mem.memory_id] = mem
        logger.info(f"[MEMORY MANAGER] Stored memory '{mem.memory_id}' (Key: '{key}', Scope: {scope.value}, Agent: '{owner_agent_id}')")
        return mem

    def get_memory(self, memory_id: str, requesting_agent_id: Optional[str] = None) -> Memory:
        mem = self._memories.get(memory_id)
        if not mem:
            raise MemoryNotFoundException(memory_id)

        # Enforce agent private memory isolation
        if mem.scope == MemoryScope.AGENT and mem.owner_agent_id and requesting_agent_id:
            if mem.owner_agent_id != requesting_agent_id:
                logger.warning(f"[MEMORY MANAGER] Access denied: Agent '{requesting_agent_id}' attempted to access private memory of Agent '{mem.owner_agent_id}'")
                raise KnowledgeAccessDeniedException(memory_id, f"Agent '{requesting_agent_id}' is not authorized to access private memory of Agent '{mem.owner_agent_id}'")

        return mem

    def list_memories(self, tenant_id: Optional[str] = None, scope: Optional[MemoryScope] = None) -> List[Memory]:
        res = list(self._memories.values())
        if tenant_id:
            res = [r for r in res if r.tenant_id == tenant_id]
        if scope:
            res = [r for r in res if r.scope == scope]
        return res
