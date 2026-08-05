import pytest
from app.knowledge.reranker import DocumentInfo

def test_document_info():
    doc = DocumentInfo(id="1", text="test", score=0.0, metadata={})
    assert doc.id == "1"
    assert doc.text == "test"
