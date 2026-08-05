import pytest
from app.knowledge.versioning import get_next_version
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_get_next_version_mock():
    # Since it requires a db session, we mock the session executing a query
    session = AsyncMock()
    from unittest.mock import MagicMock
    mock_result = MagicMock()
    class MockDoc:
        version = 2
    mock_result.scalar_one_or_none.return_value = MockDoc()
    session.execute.return_value = mock_result
    
    version = await get_next_version(session, "kb1", "doc1")
    assert version == 3
