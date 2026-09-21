"""Unit tests for ContextBuilder window assembly."""

from app.knowledge_platform.context import ContextBuilder, ContextStrategy
from app.knowledge_platform.retrieval import RetrievalResult, RetrievalStrategy


def test_context_builder_window_assembly():
    builder = ContextBuilder()
    ret_res = RetrievalResult(
        query="test query",
        strategy=RetrievalStrategy.HYBRID,
        tenant_id="t_c1",
        items=[{"item_id": "k1", "content": "Sample knowledge snippet 1"}],
    )

    cwin = builder.build_context(ret_res, strategy=ContextStrategy.RELEVANCE_FIRST, max_tokens=100)
    assert cwin.tenant_id == "t_c1"
    assert "Sample knowledge snippet 1" in cwin.assembled_context
