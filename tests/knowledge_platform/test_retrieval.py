"""Unit tests for RetrievalPipeline pre-retrieval authorization."""

import pytest
from app.knowledge_platform.knowledge import KnowledgeManager
from app.knowledge_platform.retrieval import RetrievalPipeline, RetrievalRequest, RetrievalStrategy


def test_retrieval_pre_authorization():
    km = KnowledgeManager()
    km.create_knowledge_item("Public Manual", content="Public content", classification="INTERNAL", tenant_id="t_r1")
    km.create_knowledge_item("Secret Blueprint", content="Top secret", classification="RESTRICTED", tenant_id="t_r1")

    pipeline = RetrievalPipeline(knowledge_manager=km)

    # Viewer role retrieves -> Restricted items filtered out
    req_viewer = RetrievalRequest(query="content", tenant_id="t_r1", user_role="viewer")
    res_viewer = pipeline.execute_retrieval(req_viewer)

    assert len(res_viewer.items) == 1
    assert res_viewer.items[0]["title"] == "Public Manual"
