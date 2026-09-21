"""
Retriever Module.
Orchestrates Dense/Hybrid Retrieval, and Metadata/Namespace Filtering.
"""

import logging
from typing import Any, Dict, List, Optional

from .reranker import BaseReranker, DocumentInfo
from .retrieval_profiles import Profiles, RetrievalProfile, RetrievalStrategy
from .search import SearchEngine

logger = logging.getLogger(__name__)


class Retriever:
    """Orchestrates the retrieval process."""

    def __init__(self, search_engine: SearchEngine, reranker: Optional[BaseReranker] = None):
        self.search_engine = search_engine
        self.reranker = reranker

    async def retrieve(
        self,
        query: str,
        workspace_id: str,
        organization_id: str,
        profile: RetrievalProfile = Profiles.BALANCED,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[DocumentInfo]:
        """
        Retrieves documents based on the specified profile.

        Args:
            query: The search query.
            workspace_id: Workspace ACL.
            organization_id: Organization ACL.
            profile: The retrieval profile to use.
            metadata_filter: Additional metadata filters.

        Returns:
            List[DocumentInfo]: Retrieved and potentially reranked documents.
        """
        logger.info(f"Starting retrieval with profile: {profile.name} for org {organization_id} ws {workspace_id}")

        # Combine namespace from profile with explicit metadata filters and ACLs
        combined_filter = metadata_filter or {}
        if profile.namespace:
            combined_filter["namespace"] = profile.namespace

        # Enforce Organization and Workspace ACL filtering
        combined_filter["workspace_id"] = workspace_id
        combined_filter["organization_id"] = organization_id

        # Top-K optimization: fetch more if reranking is enabled
        fetch_k = profile.top_k * 2 if profile.use_reranker else profile.top_k

        results = []
        if profile.strategy == RetrievalStrategy.DENSE:
            results = await self.search_engine.dense_search(query, fetch_k, combined_filter)
        elif profile.strategy == RetrievalStrategy.SPARSE:
            results = await self.search_engine.sparse_search(query, fetch_k, combined_filter)
        elif profile.strategy == RetrievalStrategy.HYBRID:
            results = await self.search_engine.hybrid_search(query, fetch_k, profile.alpha or 0.5, combined_filter)

        # Rerank if configured
        if profile.use_reranker and self.reranker and profile.reranker_top_n:
            results = await self.reranker.rerank(query, results, profile.reranker_top_n)

        return results[: profile.top_k]


# Alias for backward compatibility and API caller convenience
KnowledgeRetriever = Retriever
