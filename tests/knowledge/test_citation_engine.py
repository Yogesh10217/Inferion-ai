from app.knowledge.citation_engine import CitationEngine
from app.knowledge.reranker import DocumentInfo


def test_citation_engine():
    engine = CitationEngine()
    docs = [
        DocumentInfo(id="1", text="test 1", score=0.9, metadata={"page": 1}),
        DocumentInfo(id="2", text="test 2", score=0.8, metadata={"page": 2}),
    ]
    citations = engine.generate_citations(docs)
    assert len(citations) == 2
