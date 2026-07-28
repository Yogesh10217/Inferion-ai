import pytest
from httpx import AsyncClient, ASGITransport
from typing import AsyncGenerator
from typing import Dict
from unittest.mock import patch, MagicMock

# Assuming FastAPI app can be imported
from app.main import app

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    # Use ASGITransport to mock requests to the FastAPI app
    # We will mock the DB dependencies inside the tests or endpoints if they aren't configured
    # For now, let's just provide the client
    # Note: If the real DB isn't running, this might still fail on real requests
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

@pytest.fixture
def admin_token_headers() -> Dict[str, str]:
    # Mock JWT token for admin
    return {"Authorization": "Bearer mock_admin_token"}

@pytest.fixture
def user1_token_headers() -> Dict[str, str]:
    return {"Authorization": "Bearer mock_user1_token"}

@pytest.fixture
def user2_token_headers() -> Dict[str, str]:
    return {"Authorization": "Bearer mock_user2_token"}

@pytest.fixture
def test_organization() -> dict:
    return {"id": "org_123", "name": "Test Org", "slug": "test-org"}

@pytest.fixture
def org1() -> dict:
    return {"id": "org_1", "name": "Org 1", "slug": "org-1"}

@pytest.fixture
def org2() -> dict:
    return {"id": "org_2", "name": "Org 2", "slug": "org-2"}

@pytest.fixture
def user1_api_key() -> str:
    return "sk_test_mockkey"
