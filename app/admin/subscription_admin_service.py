from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.exceptions import ResourceNotFoundException
from app.billing.models import OrganizationSubscription, SubscriptionPlan


class SubscriptionAdminService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_subscriptions(self, organization_id: Optional[str] = None, status: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[OrganizationSubscription]:
        stmt = select(OrganizationSubscription)
        if organization_id:
            stmt = stmt.where(OrganizationSubscription.organization_id == organization_id)
        if status:
            stmt = stmt.where(OrganizationSubscription.status == status)
        stmt = stmt.limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_subscription(self, subscription_id: str) -> OrganizationSubscription:
        sub = await self.db.get(OrganizationSubscription, subscription_id)
        if not sub:
            raise ResourceNotFoundException(f"Subscription {subscription_id} not found")
        return sub

    async def list_plans(self, limit: int = 100, offset: int = 0) -> List[SubscriptionPlan]:
        result = await self.db.execute(select(SubscriptionPlan).limit(limit).offset(offset))
        return result.scalars().all()
