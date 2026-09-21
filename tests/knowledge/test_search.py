import pytest

from app.knowledge.search import SearchEngine


class MockSearchEngine(SearchEngine):
    async def search(self, query):
        return {"hits": [{"id": "1", "text": "result"}]}


@pytest.mark.asyncio
async def test_search():
    engine = MockSearchEngine()
    results = await engine.search("test")
    assert "hits" in results
    assert results["hits"][0]["id"] == "1"
