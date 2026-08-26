"""Knowledge Context Assembly Subsystem (Phase 5.35)."""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.knowledge_intelligence.exceptions import CrossTenantKnowledgeAccessException
from app.knowledge_intelligence.knowledge import KnowledgeItem
from app.platform_contracts.redaction import SensitiveDataSanitizer


class KnowledgeContextReference(BaseModel):
    item_id: str
    source_system: str = "INTERNAL"
    classification: str = "INTERNAL"


class KnowledgeContextItem(BaseModel):
    item_id: str
    title: str
    summary: str = ""
    relevance_score: float = 0.95
    provenance_reference: str = ""
    sanitized_metadata: Dict[str, Any] = Field(default_factory=dict)


class ContextAssemblyPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: f"cplan_{uuid.uuid4().hex[:8]}")
    tenant_id: str
    max_items: int = 10
    include_provenance: bool = True
    include_evidence: bool = True


class KnowledgeContext(BaseModel):
    context_id: str = Field(default_factory=lambda: f"kctx_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    assembly_plan_id: str
    items: List[KnowledgeContextItem] = Field(default_factory=list)
    references: List[KnowledgeContextReference] = Field(default_factory=list)
    assembled_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeContextBuilder:
    """Assembles governed, sanitized knowledge context bundles for down-stream consumers."""

    def build_context(
        self,
        tenant_id: str,
        knowledge_items: List[KnowledgeItem],
        assembly_plan: Optional[ContextAssemblyPlan] = None,
    ) -> KnowledgeContext:
        plan = assembly_plan or ContextAssemblyPlan(tenant_id=tenant_id)
        ctx_items = []
        ctx_refs = []

        for item in knowledge_items[: plan.max_items]:
            if item.tenant_id != tenant_id:
                raise CrossTenantKnowledgeAccessException(tenant_id)

            sanitized_meta = SensitiveDataSanitizer.sanitize(item.metadata.attributes)
            ctx_items.append(
                KnowledgeContextItem(
                    item_id=item.item_id,
                    title=item.metadata.title,
                    summary=item.metadata.summary,
                    provenance_reference=f"prov_{item.item_id}",
                    sanitized_metadata=sanitized_meta if isinstance(sanitized_meta, dict) else {},
                )
            )
            ctx_refs.append(
                KnowledgeContextReference(
                    item_id=item.item_id,
                    source_system=item.reference.source_system if item.reference else "INTERNAL",
                    classification=item.classification.value,
                )
            )

        return KnowledgeContext(
            tenant_id=tenant_id,
            assembly_plan_id=plan.plan_id,
            items=ctx_items,
            references=ctx_refs,
        )


class KnowledgeContextManager:
    """Manages knowledge context assembly requests and history."""

    def __init__(self) -> None:
        self.builder = KnowledgeContextBuilder()
        self._contexts: Dict[str, KnowledgeContext] = {}

    def create_context(
        self,
        tenant_id: str,
        items: List[KnowledgeItem],
        max_items: int = 10,
    ) -> KnowledgeContext:
        plan = ContextAssemblyPlan(tenant_id=tenant_id, max_items=max_items)
        ctx = self.builder.build_context(tenant_id, items, plan)
        self._contexts[ctx.context_id] = ctx
        return ctx
