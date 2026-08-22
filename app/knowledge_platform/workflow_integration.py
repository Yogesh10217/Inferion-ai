"""Workflow Knowledge Adapter & Execution Insight Integration."""

import logging
from typing import Dict, Any, Optional, List

from app.knowledge_platform.knowledge import KnowledgeManager, KnowledgeType
from app.knowledge_platform.retrieval import RetrievalPipeline, RetrievalRequest, RetrievalResult

logger = logging.getLogger(__name__)


class WorkflowKnowledgeAdapter:
    """Provides workflow engines with governed knowledge access and execution insight persistence."""

    def __init__(
        self,
        knowledge_manager: Optional[KnowledgeManager] = None,
        retrieval_pipeline: Optional[RetrievalPipeline] = None,
    ) -> None:
        self.knowledge_manager = knowledge_manager or KnowledgeManager()
        self.retrieval_pipeline = retrieval_pipeline or RetrievalPipeline()

    def retrieve_workflow_context(self, workflow_id: str, query: str, tenant_id: str = "global") -> RetrievalResult:
        req = RetrievalRequest(query=query, tenant_id=tenant_id, identity_id=f"wf_{workflow_id}")
        return self.retrieval_pipeline.execute_retrieval(req)

    def record_workflow_insight(self, workflow_id: str, title: str, content: str, tenant_id: str = "global") -> str:
        item = self.knowledge_manager.create_knowledge_item(
            title=title,
            content=content,
            knowledge_type=KnowledgeType.INSIGHT,
            tenant_id=tenant_id,
        )
        logger.info(f"[WORKFLOW KNOWLEDGE ADAPTER] Saved insight item '{item.item_id}' for workflow '{workflow_id}'")
        return item.item_id
