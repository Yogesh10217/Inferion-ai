import pytest
from app.knowledge.context_builder import ContextBuilder
from app.knowledge.reranker import DocumentInfo

def test_context_builder():
    builder = ContextBuilder()
    docs = [DocumentInfo(id="1", text="doc1", score=1.0, metadata={}), DocumentInfo(id="2", text="doc2", score=0.9, metadata={})]
    context, citations = builder.build_context(docs)
    assert "doc1" in context
    assert "doc2" in context
