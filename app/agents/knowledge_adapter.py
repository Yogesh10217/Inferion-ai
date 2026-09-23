"""
Knowledge Integration Adapter (Phase 5.0 Bridge)
"""

import logging
from typing import Any, Dict, Optional

from app.agents.agent_context import AgentContext
from app.knowledge.citation_engine import CitationEngine
from app.knowledge.context_builder import ContextBuilder
from app.knowledge.search import SearchEngine

logger = logging.getLogger(__name__)


class KnowledgeAdapter:
    def __init__(self, search_engine: Optional[SearchEngine] = None):
        self.search_engine = search_engine or SearchEngine()
        self.context_builder = ContextBuilder()
        self.citation_engine = CitationEngine()

    async def search_and_build_context(self, query: str, context: AgentContext, top_k: int = 3) -> Dict[str, Any]:
        """
        Executes hybrid knowledge retrieval and formats citations.
        """
        try:
            filter_expr = {"organization_id": context.organization_id, "workspace_id": context.workspace_id}
            results = await self.search_engine.hybrid_search(query=query, top_k=top_k, filter=filter_expr)

            docs_data = [
                {"id": doc.id, "text": doc.text, "metadata": doc.metadata, "score": doc.score} for doc in results
            ]

            formatted_context, _ = self.context_builder.build_context(results)
            citations = self.citation_engine.generate_citations(results)
            cited_text = self.citation_engine.format_inline_citations(formatted_context, citations)

            return {
                "query": query,
                "documents": docs_data,
                "formatted_context": formatted_context,
                "cited_text": cited_text,
            }

        except Exception as e:
            logger.warning(f"Knowledge search failed: {e}")
            return {"query": query, "documents": [], "formatted_context": "", "cited_text": f"Search unavailable: {e}"}
