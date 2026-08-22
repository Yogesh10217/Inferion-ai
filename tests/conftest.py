import os
os.environ["AUTH_ENABLED"] = "true"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"

try:
    from app.core.config import get_settings
    get_settings.cache_clear()
except Exception:
    pass

import pytest
if os.path.exists("./test.db"):
    try:
        os.remove("./test.db")
    except Exception:
        pass

from httpx import AsyncClient, ASGITransport

from typing import AsyncGenerator
from typing import Dict
from unittest.mock import patch, MagicMock

# Assuming FastAPI app can be imported
from app.main import app

import pytest_asyncio
import asyncio

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture
def get_client(event_loop):
    from httpx import AsyncClient, ASGITransport
    from app.main import create_app
    from app.core.database import init_db, async_session_maker
    
    async def setup_db():
        await init_db()
        # Seed test user and org
        from sqlalchemy.exc import IntegrityError
        async with async_session_maker() as session:
            from app.auth.models import User, Role
            from app.tenant.models import Organization, Membership
            
            role = Role(id="admin", name="Admin", description="Admin Role")
            user = User(id="admin_user_id", username="admin", email="admin@test.com", password_hash="hash", is_admin=True)
            # Create a user with explicit ID to avoid conflict with defaults
            org = Organization(id="test_org_id", name="Test Org", slug="test-org")
            membership = Membership(user_id="admin_user_id", organization_id="test_org_id", role_id="admin", status="active")
            
            from app.billing.plan_service import PlanService
            from app.billing.pricing_service import PricingService
            await PlanService(async_session_maker).seed_default_plans()
            await PricingService(async_session_maker).seed_default_rules()
            try:
                session.add_all([role, user, org, membership])
                await session.commit()
            except IntegrityError:
                await session.rollback()
                
    event_loop.run_until_complete(setup_db())
            
    def _get_client():
        app = create_app()
        transport = ASGITransport(app=app)
        return AsyncClient(transport=transport, base_url="http://testserver")
    return _get_client

@pytest.fixture
def admin_token_headers() -> Dict[str, str]:
    from app.auth.jwt_service import JWTService
    token = JWTService.create_access_token({"sub": "admin_user_id"})
    return {"Authorization": f"Bearer {token}", "X-Organization-Id": "test_org_id"}

@pytest.fixture
def user1_token_headers() -> Dict[str, str]:
    from app.auth.jwt_service import JWTService
    token = JWTService.create_access_token({"sub": "user1_id"})
    return {"Authorization": f"Bearer {token}", "X-Organization-Id": "test_org_id"}

@pytest.fixture
def user2_token_headers() -> Dict[str, str]:
    from app.auth.jwt_service import JWTService
    token = JWTService.create_access_token({"sub": "user2_id"})
    return {"Authorization": f"Bearer {token}", "X-Organization-Id": "test_org_id"}

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
