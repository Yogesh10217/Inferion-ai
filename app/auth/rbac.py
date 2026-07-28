from typing import List, Set, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.auth.models import User, Role, Permission
from app.tenant.models import Membership, WorkspaceMembership


class RBACService:
    @staticmethod
    async def get_user_permissions(db: AsyncSession, user_id: str, organization_id: Optional[str] = None, workspace_id: Optional[str] = None) -> Set[str]:
        """Fetch all resolved permissions for a given user scoped to their current tenant context."""
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
        
        # 1. Global / System roles
        for role in user.roles:
            for perm in role.permissions:
                permissions.add(perm.name)
                
        # 2. Organization roles
        if organization_id:
            stmt_mem = (
                select(Membership)
                .where(Membership.user_id == user_id, Membership.organization_id == organization_id)
            )
            res_mem = await db.execute(stmt_mem)
            mem = res_mem.scalar_one_or_none()
            if mem and mem.status == "active":
                stmt_role = select(Role).options(selectinload(Role.permissions)).where(Role.id == mem.role_id)
                res_role = await db.execute(stmt_role)
                role = res_role.scalar_one_or_none()
                if role:
                    for perm in role.permissions:
                        permissions.add(perm.name)
                        
        # 3. Workspace roles
        if workspace_id:
            stmt_ws = (
                select(WorkspaceMembership)
                .where(WorkspaceMembership.user_id == user_id, WorkspaceMembership.workspace_id == workspace_id)
            )
            res_ws = await db.execute(stmt_ws)
            ws_mem = res_ws.scalar_one_or_none()
            if ws_mem:
                stmt_role = select(Role).options(selectinload(Role.permissions)).where(Role.id == ws_mem.role_id)
                res_role = await db.execute(stmt_role)
                role = res_role.scalar_one_or_none()
                if role:
                    for perm in role.permissions:
                        permissions.add(perm.name)
        
        return permissions

    @staticmethod
    def has_permission(user_permissions: Set[str], required_permission: str) -> bool:
        """Check if user has a specific permission."""
        return required_permission in user_permissions
