"""Context Engineering & Dynamic Context Window Builder Subsystem."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from app.knowledge.context_builder import ContextBuilder as BaseContextBuilder
from app.knowledge_platform.retrieval import RetrievalResult

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ContextStrategy(str, Enum):
    FULL_CONTEXT = "FULL_CONTEXT"
    RELEVANCE_FIRST = "RELEVANCE_FIRST"
    RECENCY_FIRST = "RECENCY_FIRST"
    CONFIDENCE_FIRST = "CONFIDENCE_FIRST"
    COST_OPTIMIZED = "COST_OPTIMIZED"
    LATENCY_OPTIMIZED = "LATENCY_OPTIMIZED"
    RISK_AWARE = "RISK_AWARE"
    AGENT_SPECIFIC = "AGENT_SPECIFIC"
    TASK_SPECIFIC = "TASK_SPECIFIC"


class ContextRequest(BaseModel):
    query: str
    tenant_id: str = "global"
    identity_id: str = "user"
    strategy: ContextStrategy = ContextStrategy.RELEVANCE_FIRST


class ContextItem(BaseModel):
    item_id: str
    content: str
    score: float = 1.0


class ContextBudget(BaseModel):
    max_tokens: int = 2048
    max_items: int = 10


class ContextWindow(BaseModel):

    window_id: str = Field(default_factory=lambda: f"cwin_{uuid.uuid4().hex[:10]}")
    tenant_id: str = "global"
    strategy: ContextStrategy = ContextStrategy.RELEVANCE_FIRST

    assembled_context: str
    token_count: int = 0
    provenance_references: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=_now)


class ContextBuilder:
    """Assembles governed context windows from retrieval results adhering to token budgets and context strategies."""

    def __init__(self, base_builder: Optional[BaseContextBuilder] = None) -> None:
        self.base_builder = base_builder or BaseContextBuilder()

    def build_context(
        self,
        retrieval_result: RetrievalResult,
        strategy: ContextStrategy = ContextStrategy.RELEVANCE_FIRST,
        max_tokens: int = 2048,
    ) -> ContextWindow:
        snippets = []
        provenance = []

        for item in retrieval_result.items:
            content = item.get("content", "")
            item_id = item.get("item_id", "unknown")
            snippets.append(f"[Source: {item_id}]\n{content}")
            provenance.append(item_id)

        full_text = "\n\n".join(snippets)
        approx_tokens = len(full_text.split()) * 2

        # Truncate if token budget exceeded
        if approx_tokens > max_tokens:
            words = full_text.split()[: max_tokens // 2]
            full_text = " ".join(words) + "\n[TRUNCATED_FOR_BUDGET]"
            approx_tokens = max_tokens

        win = ContextWindow(
            tenant_id=retrieval_result.tenant_id,
            strategy=strategy,
            assembled_context=full_text,
            token_count=approx_tokens,
            provenance_references=provenance,
        )
        logger.info(
            f"[CONTEXT BUILDER] Assembled context window '{win.window_id}' ({approx_tokens} tokens) via strategy {strategy.value}"
        )
        return win
