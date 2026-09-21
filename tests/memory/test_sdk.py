"""
Tests for Python SDK MemoryClient Interface
"""

from sdk.python.llm_engine.memory import MemoryClient


class MockHTTPResponse:
    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code

    def raise_for_status(self):
        pass

    def json(self):
        return self._json


class DummyHTTPClient:
    def post(self, url, json=None, params=None):
        if "search" in url:
            return MockHTTPResponse([{"id": "mem_1", "content": "FastAPI fact"}])
        return MockHTTPResponse(
            {"status": "success", "memory": {"id": "mem_1", "content": json.get("content") if json else ""}}
        )

    def get(self, url, params=None):
        if "profile" in url:
            return MockHTTPResponse({"user_id": "u1", "preferred_language": "python"})
        if "analytics" in url:
            return MockHTTPResponse({"total_reads": 5})
        return MockHTTPResponse([{"id": "mem_1", "content": "test"}])

    def delete(self, url):
        return MockHTTPResponse({"status": "success"})

    def patch(self, url, params=None, json=None):
        return MockHTTPResponse({"status": "success", "profile": json.get("profile_data") if json else {}})


def test_sdk_memory_client_interface():
    dummy = DummyHTTPClient()
    client = MemoryClient(dummy, "http://localhost:8000")

    res = client.create("Test memory via SDK")
    assert res["status"] == "success"

    search_res = client.search("FastAPI")
    assert len(search_res) == 1
    assert search_res[0]["id"] == "mem_1"

    prof = client.get_profile("u1")
    assert prof["user_id"] == "u1"

    analytics = client.analytics()
    assert analytics["total_reads"] == 5
