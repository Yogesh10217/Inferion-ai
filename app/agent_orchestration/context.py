"""Governed Agent Context Assembly Subsystem (Phase 5.36)."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.agent_orchestration.exceptions import CrossTenantAgentAccessException
from app.knowledge_intelligence.manager import KnowledgeIntelligenceManager
from app.platform_contracts.redaction import SensitiveDataSanitizer
from app.platform_contracts.tenant import TenantAccessGuard


class AgentContextItem(BaseModel):
    item_id: str = Field(default_factory=lambda: f"ctxitem_{uuid.uuid4().hex[:10]}")
    source: str = "INTERNAL"
    content_type: str = "TEXT"
    content_sanitized: Dict[str, Any] = Field(default_factory=dict)
    classification: str = "INTERNAL"
    relevance_score: float = 1.0


class AgentContextReference(BaseModel):
    reference_id: str = Field(default_factory=lambda: f"ctxref_{uuid.uuid4().hex[:10]}")
    source_subsystem: str = "KNOWLEDGE_INTELLIGENCE"
    external_entity_id: str
    description: str = ""


class ContextBudget(BaseModel):
    max_tokens: int = 8000
    used_tokens: int = 0
    max_items: int = 20


class ContextConstraint(BaseModel):
    max_classification: str = "CONFIDENTIAL"
    redact_secrets: bool = True


class AgentContext(BaseModel):
    context_id: str = Field(default_factory=lambda: f"ctx_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    agent_id: str
    task_id: str
    items: List[AgentContextItem] = Field(default_factory=list)
    references: List[AgentContextReference] = Field(default_factory=list)
    budget: ContextBudget = Field(default_factory=ContextBudget)
    constraint: ContextConstraint = Field(default_factory=ContextConstraint)
    assembled_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentContextBuilder:
    """Assembles context items while redacting sensitive fields using SensitiveDataSanitizer."""

    def __init__(self, sanitizer: Optional[SensitiveDataSanitizer] = None) -> None:
        self.sanitizer = sanitizer or SensitiveDataSanitizer()

    def build_item(
        self,
        raw_content: Dict[str, Any],
        source: str = "KNOWLEDGE_BASE",
        classification: str = "INTERNAL",
    ) -> AgentContextItem:
        sanitized = self.sanitizer.sanitize_copy(raw_content)
        return AgentContextItem(
            source=source,
            content_type="JSON",
            content_sanitized=sanitized if isinstance(sanitized, dict) else {"data": str(sanitized)},
            classification=classification,
        )


class AgentContextManager:
    """Manages context assembly, delegating retrieval to KnowledgeIntelligenceManager."""

    def __init__(
        self,
        knowledge_manager: Optional[KnowledgeIntelligenceManager] = None,
        tenant_guard: Optional[TenantAccessGuard] = None,
    ) -> None:
        self.knowledge_manager = knowledge_manager or KnowledgeIntelligenceManager()
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self.builder = AgentContextBuilder()
        self._contexts: Dict[str, AgentContext] = {}

    def assemble_context(
        self,
        tenant_id: str,
        agent_id: str,
        task_id: str,
        query: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None,
        max_items: int = 10,
    ) -> AgentContext:
        items: List[AgentContextItem] = []
        references: List[AgentContextReference] = []

        # 1. Retrieve knowledge from KnowledgeIntelligenceManager if query provided
        if query:
            try:
                k_res = self.knowledge_manager.retrieve_knowledge(
                    tenant_id=tenant_id,
                    query=query,
                    max_results=max_items,
                )
                raw_items = getattr(k_res, "items", [])
                for idx, k_item in enumerate(raw_items[:max_items]):
                    item_dict = k_item.model_dump() if hasattr(k_item, "model_dump") else {"data": str(k_item)}
                    ctx_item = self.builder.build_item(item_dict, source="KNOWLEDGE_INTELLIGENCE")
                    items.append(ctx_item)

                    ref_id = item_dict.get("item_id", f"kitem_{idx}")
                    references.append(
                        AgentContextReference(
                            source_subsystem="KNOWLEDGE_INTELLIGENCE",
                            external_entity_id=ref_id,
                            description=f"Knowledge retrieval for '{query}'",
                        )
                    )
            except Exception:  # nosec B110
                pass

        # 2. Add sanitized additional data
        if additional_data:
            ctx_item = self.builder.build_item(additional_data, source="TASK_INPUT")
            items.append(ctx_item)

        ctx = AgentContext(
            tenant_id=tenant_id,
            agent_id=agent_id,
            task_id=task_id,
            items=items,
            references=references,
            budget=ContextBudget(used_tokens=len(items) * 150, max_items=max_items),
        )
        self._contexts[ctx.context_id] = ctx
        return ctx

    def get_context(self, context_id: str, tenant_id: str) -> AgentContext:
        ctx = self._contexts.get(context_id)
        if not ctx:
            # Generate empty context fallback
            return AgentContext(context_id=context_id, tenant_id=tenant_id, agent_id="unknown", task_id="unknown")

        try:
            self.tenant_guard.enforce_isolation(tenant_id, ctx.tenant_id)
        except Exception:
            raise CrossTenantAgentAccessException(tenant_id, ctx.tenant_id)

        return ctx
