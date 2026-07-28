import asyncio
import os
os.environ["AUTH_ENABLED"] = "true"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
if os.path.exists("./test.db"):
    os.remove("./test.db")

from app.core.database import init_db, async_session_maker
from sqlalchemy.exc import IntegrityError

async def main():
    await init_db()
    async with async_session_maker() as session:
        from app.auth.models import User, Role
        from app.tenant.models import Organization, Membership
        
        role = Role(id="admin", name="Admin", description="Admin Role")
        user = User(id="admin_user_id", email="admin@test.com", password_hash="hash")
        org = Organization(id="test_org_id", name="Test Org", slug="test-org")
        membership = Membership(user_id="admin_user_id", organization_id="test_org_id", role_id="admin", status="active")
        
        try:
            session.add_all([role, user, org, membership])
            await session.commit()
            print("SUCCESS")
        except Exception as e:
            print("ERROR:", e)
            import traceback
            traceback.print_exc()

asyncio.run(main())
