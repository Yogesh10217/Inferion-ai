"""Unit tests for hybrid retrieval strategy execution."""

import pytest
from app.knowledge_platform.knowledge import KnowledgeManager
from app.knowledge_platform.retrieval import RetrievalPipeline, RetrievalRequest, RetrievalStrategy


def test_hybrid_retrieval_strategy():
    km = KnowledgeManager()
    km.create_knowledge_item("Policy Doc", content="Security policy details", tenant_id="t_hr")
    pipeline = RetrievalPipeline(knowledge_manager=km)

    req = RetrievalRequest(query="policy", strategy=RetrievalStrategy.HYBRID, tenant_id="t_hr")
    res = pipeline.execute_retrieval(req)

    assert res.strategy == RetrievalStrategy.HYBRID
    assert len(res.items) == 1
