"""Agent Knowledge Adapter & Delegated Scope Boundary Integration."""

import logging
from typing import Dict, Any, Optional, List

from app.identity.agent_identity import AgentIdentityManager
from app.knowledge_platform.retrieval import RetrievalPipeline, RetrievalRequest, RetrievalResult

logger = logging.getLogger(__name__)


class AgentKnowledgeAdapter:
    """Adapts AI Agent knowledge requests while enforcing agent delegated scope boundaries."""

    def __init__(
        self,
        retrieval_pipeline: Optional[RetrievalPipeline] = None,
        agent_identity_manager: Optional[AgentIdentityManager] = None,
    ) -> None:
        self.retrieval_pipeline = retrieval_pipeline or RetrievalPipeline()
        self.agent_identity_manager = agent_identity_manager or AgentIdentityManager()

    def query_knowledge_for_agent(
        self,
        agent_id: str,
        query: str,
        delegation_id: Optional[str] = None,
        tenant_id: str = "global",
    ) -> RetrievalResult:
        # Validate delegation if provided
        if delegation_id:
            del_auth = self.agent_identity_manager.get_delegated_authorization(delegation_id)
            self.agent_identity_manager.validate_agent_boundary(del_auth, requested_action=query, requested_scope="read")

        req = RetrievalRequest(query=query, tenant_id=tenant_id, identity_id=f"agent_{agent_id}")
        return self.retrieval_pipeline.execute_retrieval(req)
