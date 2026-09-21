"""
Tests for Memory REST API Layer (/v1/memory)
"""

import pytest


@pytest.mark.asyncio
async def test_create_and_get_memory_api(get_client, admin_token_headers):
    async with get_client() as client:
        resp = await client.post(
            "/v1/memory", json={"content": "Test memory content from API"}, headers=admin_token_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        mem_id = data["memory"]["id"]

        get_resp = await client.get(f"/v1/memory/{mem_id}", headers=admin_token_headers)
        assert get_resp.status_code == 200
        assert get_resp.json()["memory"]["content"] == "Test memory content from API"


@pytest.mark.asyncio
async def test_list_and_search_memory_api(get_client, admin_token_headers):
    async with get_client() as client:
        await client.post("/v1/memory", json={"content": "Searchable memory item"}, headers=admin_token_headers)

        list_resp = await client.get("/v1/memory", headers=admin_token_headers)
        assert list_resp.status_code == 200
        assert len(list_resp.json()) >= 1

        search_resp = await client.post(
            "/v1/memory/search", json={"query": "Searchable", "top_k": 5}, headers=admin_token_headers
        )
        assert search_resp.status_code == 200
        assert len(search_resp.json()) >= 1


@pytest.mark.asyncio
async def test_profile_memory_api(get_client, admin_token_headers):
    async with get_client() as client:
        get_resp = await client.get("/v1/memory/profile?user_id=test_user", headers=admin_token_headers)
        assert get_resp.status_code == 200

        patch_resp = await client.patch(
            "/v1/memory/profile?user_id=test_user",
            json={"profile_data": {"preferred_language": "go"}},
            headers=admin_token_headers,
        )
        assert patch_resp.status_code == 200
        assert patch_resp.json()["profile"]["preferred_language"] == "go"
