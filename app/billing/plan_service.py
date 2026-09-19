from typing import List, Optional

from sqlalchemy import select

from app.billing.exceptions import InvalidPlanException
from app.billing.models import OrganizationSubscription, SubscriptionPlan


class PlanService:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def get_all_plans(self) -> List[SubscriptionPlan]:
        stmt = select(SubscriptionPlan).where(SubscriptionPlan.enabled == True)
        async with self.session_factory() as db:
            result = await db.execute(stmt)
            return list(result.scalars().all())

    async def get_plan(self, plan_id: str) -> Optional[SubscriptionPlan]:
        stmt = select(SubscriptionPlan).where(SubscriptionPlan.id == plan_id)
        async with self.session_factory() as db:
            result = await db.execute(stmt)
            return result.scalars().first()

    async def seed_default_plans(self) -> None:
        plans = await self.get_all_plans()
        if plans:
            return

        examples = [
            SubscriptionPlan(name="Free", monthly_price=0.0, max_users=1, max_workspaces=1),
            SubscriptionPlan(name="Pro", monthly_price=49.0, max_users=5, max_workspaces=3),
            SubscriptionPlan(
                name="Business", monthly_price=199.0, max_users=20, max_workspaces=10, priority_support=True
            ),
            SubscriptionPlan(name="Enterprise", monthly_price=999.0, priority_support=True),
        ]
        async with self.session_factory() as db:
            db.add_all(examples)
            await db.commit()


class SubscriptionService:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def get_active_subscription(self, org_id: str) -> Optional[OrganizationSubscription]:
        stmt = select(OrganizationSubscription).where(
            OrganizationSubscription.organization_id == org_id, OrganizationSubscription.status == "active"
        )
        async with self.session_factory() as db:
            result = await db.execute(stmt)
            return result.scalars().first()

    async def assign_plan(self, org_id: str, plan_id: str) -> OrganizationSubscription:
        # Verify plan exists
        stmt = select(SubscriptionPlan).where(SubscriptionPlan.id == plan_id)
        async with self.session_factory() as db:
            result = await db.execute(stmt)
            plan = result.scalars().first()
            if not plan:
                raise InvalidPlanException()

            # Check existing
            existing_stmt = select(OrganizationSubscription).where(
                OrganizationSubscription.organization_id == org_id, OrganizationSubscription.status == "active"
            )
            existing_res = await db.execute(existing_stmt)
            existing = existing_res.scalars().first()

            if existing:
                existing.status = "canceled"
                db.add(existing)

            new_sub = OrganizationSubscription(organization_id=org_id, plan_id=plan_id, status="active")
            db.add(new_sub)
            await db.commit()
            await db.refresh(new_sub)
            return new_sub
