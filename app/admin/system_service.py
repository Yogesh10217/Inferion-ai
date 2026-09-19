from typing import Any, Dict

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import APIKey, User
from app.billing.models import OrganizationSubscription
from app.tenant.models import Organization, Workspace


class SystemAdminService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_system_stats(self) -> Dict[str, Any]:
        # Count organizations
        orgs_active = await self.db.scalar(select(func.count(Organization.id)).where(Organization.status == "active"))
        orgs_suspended = await self.db.scalar(
            select(func.count(Organization.id)).where(Organization.status == "suspended")
        )

        # Count users
        users_active = await self.db.scalar(select(func.count(User.id)).where(User.is_active == True))
        users_disabled = await self.db.scalar(select(func.count(User.id)).where(User.is_active == False))

        # Count workspaces
        workspaces_total = await self.db.scalar(select(func.count(Workspace.id)))

        # Count API Keys
        keys_active = await self.db.scalar(select(func.count(APIKey.id)).where(APIKey.revoked_at.is_(None)))
        keys_revoked = await self.db.scalar(select(func.count(APIKey.id)).where(APIKey.revoked_at.is_not(None)))

        # Count Subscriptions
        subs_active = await self.db.scalar(
            select(func.count(OrganizationSubscription.id)).where(OrganizationSubscription.status == "active")
        )

        return {
            "organizations": {
                "active": orgs_active or 0,
                "suspended": orgs_suspended or 0,
            },
            "users": {
                "active": users_active or 0,
                "disabled": users_disabled or 0,
            },
            "workspaces": {
                "total": workspaces_total or 0,
            },
            "api_keys": {
                "active": keys_active or 0,
                "revoked": keys_revoked or 0,
            },
            "subscriptions": {"active": subs_active or 0},
        }
