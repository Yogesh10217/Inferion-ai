from typing import Optional, Set

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.exceptions import PermissionDeniedException
from app.auth.models import User
from app.core.config import get_settings
from app.core.database import get_db_session

settings = get_settings()


async def get_current_user_id(request: Request) -> Optional[str]:
    """Retrieve the current user ID from the request state (populated by middleware)."""
    return getattr(request.state, "user_id", None)


async def get_current_user(request: Request, db: AsyncSession = Depends(get_db_session)) -> Optional[User]:
    """Retrieve the current User object from the database."""
    if not settings.auth_enabled:
        return None

    user_id = await get_current_user_id(request)
    if not user_id:
        if not settings.allow_anonymous:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        return None

    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")

    return user


async def require_admin(current_user: Optional[User] = Depends(get_current_user)) -> Optional[User]:
    """Dependency that requires the current user to be an admin."""
    if not settings.auth_enabled:
        return None

    if not current_user or not current_user.is_admin:
        raise PermissionDeniedException(detail="Admin privileges required")
    return current_user


class RequirePermission:
    def __init__(self, required_permission: str):
        self.required_permission = required_permission

    async def __call__(self, request: Request):
        if not settings.auth_enabled:
            return True

        user_id = getattr(request.state, "user_id", None)
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        permissions: Set[str] = getattr(request.state, "permissions", set())
        if self.required_permission not in permissions:
            raise PermissionDeniedException(detail=f"Missing required permission: {self.required_permission}")
        return True


def require_permission(permission: str):
    return Depends(RequirePermission(permission))
