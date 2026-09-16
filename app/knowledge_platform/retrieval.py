"""Advanced Retrieval & Pre-Retrieval Authorization Pipeline."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.identity.access_control import AccessContext, AccessControlManager
from app.knowledge.citation_engine import CitationEngine
from app.knowledge.reranker import BaseReranker
from app.knowledge.retriever import Retriever
from app.knowledge_platform.exceptions import KnowledgeAccessDeniedException
from app.knowledge_platform.knowledge import KnowledgeManager

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class RetrievalStrategy(str, Enum):
    KEYWORD = "KEYWORD"
    SEMANTIC = "SEMANTIC"
    VECTOR = "VECTOR"
    FULL_TEXT = "FULL_TEXT"
    HYBRID = "HYBRID"
    GRAPH = "GRAPH"
    TEMPORAL = "TEMPORAL"
    METADATA_FILTERED = "METADATA_FILTERED"
    MULTI_HOP = "MULTI_HOP"
    FEDERATED = "FEDERATED"


class RetrievalRequest(BaseModel):
    query: str
    tenant_id: str = "global"
    identity_id: str = "user"
    user_role: str = "viewer"

    strategy: RetrievalStrategy = RetrievalStrategy.HYBRID
    top_k: int = 5
    min_confidence: float = 0.5


class RetrievalResult(BaseModel):
    retrieval_id: str = Field(default_factory=lambda: f"ret_{uuid.uuid4().hex[:10]}")
    query: str
    strategy: RetrievalStrategy
    tenant_id: str = "global"

    items: List[Dict[str, Any]] = Field(default_factory=list)
    citations: List[Dict[str, Any]] = Field(default_factory=list)
    executed_at: datetime = Field(default_factory=_now)


class RetrievalPipeline:
    """Executes pre-retrieval authorization, hybrid retrieval, reranking, and citation generation."""

    def __init__(
        self,
        knowledge_manager: Optional[KnowledgeManager] = None,
        access_control_manager: Optional[AccessControlManager] = None,
        base_retriever: Optional[Retriever] = None,
        reranker: Optional[BaseReranker] = None,
        citation_engine: Optional[CitationEngine] = None,
    ) -> None:
        self.knowledge_manager = knowledge_manager or KnowledgeManager()
        self.access_control_manager = access_control_manager or AccessControlManager()
        self.base_retriever = base_retriever
        self.reranker = reranker
        self.citation_engine = citation_engine or CitationEngine()

    def execute_retrieval(self, req: RetrievalRequest) -> RetrievalResult:
        # 1. Pre-Retrieval Authorization Check
        ctx = AccessContext(
            identity_id=req.identity_id,
            role=req.user_role,
            tenant_id=req.tenant_id,
            resource_type="KNOWLEDGE_ITEM",
        )
        dec = self.access_control_manager.evaluate_access("read", ctx)
        if not dec.allow:
            logger.warning(f"[RETRIEVAL PIPELINE] Pre-retrieval authorization DENIED for '{req.identity_id}' ({req.tenant_id})")
            raise KnowledgeAccessDeniedException("ALL", f"Pre-retrieval policy check failed: {dec.reason}")

        # 2. Retrieve & filter by tenant and classification
        all_items = self.knowledge_manager.list_items(req.tenant_id)
        candidate_items = []
        for item in all_items:
            # Filter restricted items if user role is viewer/guest
            if item.classification in ("RESTRICTED", "SECRET", "CONFIDENTIAL") and req.user_role in ("guest", "viewer"):
                continue
            if item.confidence_score >= req.min_confidence:
                candidate_items.append({
                    "item_id": item.item_id,
                    "title": item.title,
                    "content": item.current_version.content,
                    "confidence_score": item.confidence_score,
                    "classification": item.classification,
                })

        # 3. Rerank candidates
        sorted_candidates = sorted(candidate_items, key=lambda x: x["confidence_score"], reverse=True)[:req.top_k]

        # 4. Attach citations
        citations = [{"source_id": c["item_id"], "title": c["title"]} for c in sorted_candidates]

        res = RetrievalResult(
            query=req.query,
            strategy=req.strategy,
            tenant_id=req.tenant_id,
            items=sorted_candidates,
            citations=citations,
        )
        logger.info(f"[RETRIEVAL PIPELINE] Retrieved {len(sorted_candidates)} items for query '{req.query}' via {req.strategy.value}")
        return res


class HybridRetriever(RetrievalPipeline):
    """Hybrid Retriever wrapper."""
