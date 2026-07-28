from typing import List, Set
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.auth.models import User, Role, Permission


class RBACService:
    @staticmethod
    async def get_user_permissions(db: AsyncSession, user_id: str) -> Set[str]:
        """Fetch all resolved permissions for a given user."""
        stmt = (
            select(User)
            .options(
                selectinload(User.roles).selectinload(Role.permissions)
            )
            .where(User.id == user_id)
        )
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            return set()

        permissions = set()
        for role in user.roles:
            for perm in role.permissions:
                permissions.add(perm.name)
        
        return permissions

    @staticmethod
    def has_permission(user_permissions: Set[str], required_permission: str) -> bool:
        """Check if user has a specific permission."""
        return required_permission in user_permissions
