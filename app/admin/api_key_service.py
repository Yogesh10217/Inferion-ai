from datetime import datetime, timedelta, timezone
from typing import List, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.exceptions import ResourceNotFoundException
from app.auth.models import APIKey


class APIKeyAdminService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_api_keys(
        self, user_id: Optional[str] = None, org_id: Optional[str] = None, limit: int = 100, offset: int = 0
    ) -> List[APIKey]:
        stmt = select(APIKey)
        if user_id:
            stmt = stmt.where(APIKey.user_id == user_id)
        if org_id:
            stmt = stmt.where(APIKey.organization_id == org_id)
        stmt = stmt.limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_api_key(self, api_key_id: str) -> APIKey:
        key = await self.db.get(APIKey, api_key_id)
        if not key:
            raise ResourceNotFoundException(f"API Key {api_key_id} not found")
        return key

    async def revoke_api_key(self, api_key_id: str) -> APIKey:
        key = await self.get_api_key(api_key_id)
        key.revoked_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(key)
        return key

    async def expire_api_key(self, api_key_id: str, in_days: int = 0) -> APIKey:
        key = await self.get_api_key(api_key_id)
        key.expires_at = datetime.now(timezone.utc) + timedelta(days=in_days)
        await self.db.commit()
        await self.db.refresh(key)
        return key

    async def bulk_revoke(self, user_id: Optional[str] = None, org_id: Optional[str] = None) -> int:
        if not user_id and not org_id:
            raise ValueError("Must specify user_id or org_id for bulk revocation")

        stmt = update(APIKey).values(revoked_at=datetime.now(timezone.utc)).where(APIKey.revoked_at.is_(None))
        if user_id:
            stmt = stmt.where(APIKey.user_id == user_id)
        if org_id:
            stmt = stmt.where(APIKey.organization_id == org_id)

        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount
