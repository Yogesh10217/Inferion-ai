from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import UserOut
from app.auth.dependencies import require_admin
from app.auth.models import Permission, Role, User
from app.core.database import get_db_session

router = APIRouter(prefix="/admin", tags=["admin"])


class RoleOut(BaseModel):
    id: str
    name: str
    description: str | None

    model_config = {"from_attributes": True}


class PermissionOut(BaseModel):
    id: str
    name: str
    description: str | None

    model_config = {"from_attributes": True}


@router.get("/users", response_model=List[UserOut])
async def list_users(db: AsyncSession = Depends(get_db_session), _=Depends(require_admin)):
    stmt = select(User)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/roles", response_model=List[RoleOut])
async def list_roles(db: AsyncSession = Depends(get_db_session), _=Depends(require_admin)):
    stmt = select(Role)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/permissions", response_model=List[PermissionOut])
async def list_permissions(db: AsyncSession = Depends(get_db_session), _=Depends(require_admin)):
    stmt = select(Permission)
    result = await db.execute(stmt)
    return result.scalars().all()
