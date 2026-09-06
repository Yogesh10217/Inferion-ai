"""Semantic context management across agents, decisions, operations, and workflows."""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional
import uuid
from pydantic import BaseModel, Field

from app.knowledge_assurance.exceptions import (
    KnowledgeContextNotFoundException,
    CrossTenantKnowledgeAssuranceException,
)


class ContextType(str, Enum):
    AGENT = "AGENT"
    DECISION = "DECISION"
    OPERATIONS = "OPERATIONS"
    INCIDENT = "INCIDENT"
    MODEL = "MODEL"
    DATASET = "DATASET"
    WORKFLOW = "WORKFLOW"


class ContextScope(str, Enum):
    GLOBAL = "GLOBAL"
    TENANT = "TENANT"
    WORKSPACE = "WORKSPACE"
    SESSION = "SESSION"


class ContextPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ContextStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    SUPERSEDED = "SUPERSEDED"


class KnowledgeContext(BaseModel):
    context_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    name: str
    context_type: ContextType = ContextType.DECISION
    scope: ContextScope = ContextScope.TENANT
    priority: ContextPriority = ContextPriority.MEDIUM
    status: ContextStatus = ContextStatus.ACTIVE
    reference_ids: List[str] = Field(default_factory=list)
    confidence_score: float = 0.85
    freshness_score: float = 0.90
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class KnowledgeContextManager:
    """Manages semantic contexts for enterprise AI subsystems."""

    def __init__(self) -> None:
        self._contexts: Dict[str, KnowledgeContext] = {}

    def create_context(
        self,
        tenant_id: str,
        name: Optional[str] = None,
        title: Optional[str] = None,
        context_type: Any = ContextType.DECISION,
        scope: Any = ContextScope.TENANT,
        priority: Any = ContextPriority.MEDIUM,
        reference_ids: Optional[List[str]] = None,
        payload: Optional[Dict[str, Any]] = None,
        confidence_score: float = 0.85,
        freshness_score: float = 0.90,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> KnowledgeContext:
        ctx_name = title or name or "Knowledge Context"

        if isinstance(context_type, str):
            try:
                ctype = ContextType(context_type)
            except ValueError:
                ctype = ContextType.DECISION
        else:
            ctype = context_type

        if isinstance(scope, str):
            try:
                cscope = ContextScope(scope)
            except ValueError:
                cscope = ContextScope.TENANT
        else:
            cscope = scope

        if isinstance(priority, str):
            try:
                cprio = ContextPriority(priority)
            except ValueError:
                cprio = ContextPriority.MEDIUM
        else:
            cprio = priority

        meta = metadata or {}
        if payload:
            meta["payload"] = payload

        ctx = KnowledgeContext(
            tenant_id=tenant_id,
            name=ctx_name,
            context_type=ctype,
            scope=cscope,
            priority=cprio,
            reference_ids=reference_ids or [],
            confidence_score=confidence_score,
            freshness_score=freshness_score,
            metadata=meta,
        )
        self._contexts[ctx.context_id] = ctx
        return ctx

    def get_context(self, context_id: str, tenant_id: str) -> KnowledgeContext:
        ctx = self._contexts.get(context_id)
        if not ctx:
            raise KnowledgeContextNotFoundException(f"Context '{context_id}' not found")
        if ctx.tenant_id != tenant_id:
            raise CrossTenantKnowledgeAssuranceException()
        return ctx

    def list_contexts(self, tenant_id: str) -> List[KnowledgeContext]:
        return [c for c in self._contexts.values() if c.tenant_id == tenant_id]
