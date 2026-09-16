from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.exceptions import ResourceNotFoundException
from app.auth.models import User


class UserAdminService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_users(self, limit: int = 100, offset: int = 0) -> List[User]:
        result = await self.db.execute(select(User).limit(limit).offset(offset))
        return result.scalars().all()

    async def get_user(self, user_id: str) -> User:
        user = await self.db.get(User, user_id)
        if not user:
            raise ResourceNotFoundException(f"User {user_id} not found")
        return user

    async def disable_user(self, user_id: str) -> User:
        user = await self.get_user(user_id)
        user.is_active = False
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def enable_user(self, user_id: str) -> User:
        user = await self.get_user(user_id)
        user.is_active = True
        await self.db.commit()
        await self.db.refresh(user)
        return user
