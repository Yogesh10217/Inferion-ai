import pytest


@pytest.mark.asyncio
async def test_pgvector_vector_store_operations(real_vector_store):
    store = real_vector_store
    await store.add([{"id": "1", "vector": [0.1, 0.2], "metadata": {}}], "col1")
    res = await store.get(["1"], "col1")
    assert len(res) == 1
    assert res[0]["id"] == "1"

    await store.delete(["1"], "col1")
    res = await store.get(["1"], "col1")
    assert len(res) == 0
