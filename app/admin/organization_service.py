from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from app.tenant.models import Organization
from app.admin.exceptions import ResourceNotFoundException, InvalidOperationException

class OrganizationAdminService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_organizations(self, limit: int = 100, offset: int = 0) -> List[Organization]:
        result = await self.db.execute(select(Organization).limit(limit).offset(offset))
        return result.scalars().all()

    async def get_organization(self, org_id: str) -> Organization:
        org = await self.db.get(Organization, org_id)
        if not org:
            raise ResourceNotFoundException(f"Organization {org_id} not found")
        return org

    async def suspend_organization(self, org_id: str, actor_id: str) -> Organization:
        org = await self.get_organization(org_id)
        if org.status == "archived":
            raise InvalidOperationException("Cannot suspend an archived organization.")
        if org.status == "suspended":
            return org
            
        org.status = "suspended"
        org.suspended_at = datetime.now(timezone.utc)
        org.suspended_by = actor_id
        await self.db.commit()
        await self.db.refresh(org)
        return org

    async def reactivate_organization(self, org_id: str) -> Organization:
        org = await self.get_organization(org_id)
        if org.status == "archived":
            raise InvalidOperationException("Cannot reactivate an archived organization.")
        if org.status == "active":
            return org
            
        org.status = "active"
        org.suspended_at = None
        org.suspended_by = None
        await self.db.commit()
        await self.db.refresh(org)
        return org

    async def archive_organization(self, org_id: str) -> Organization:
        org = await self.get_organization(org_id)
        if org.status == "archived":
            return org
            
        org.status = "archived"
        org.archived_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(org)
        return org

    async def update_organization(self, org_id: str, **kwargs) -> Organization:
        org = await self.get_organization(org_id)
        for key, value in kwargs.items():
            if hasattr(org, key):
                setattr(org, key, value)
        await self.db.commit()
        await self.db.refresh(org)
        return org
