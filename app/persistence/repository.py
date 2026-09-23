"""Reusable Repository Pattern for Async Database Operations."""

import logging
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Generic repository providing consistent CRUD access across database entities."""

    def __init__(self, model_cls: Type[T], session: AsyncSession) -> None:
        self.model_cls = model_cls
        self.session = session

    async def get_by_id(self, entity_id: Any) -> Optional[T]:
        """Fetch single model entity by primary key."""
        return await self.session.get(self.model_cls, entity_id)

    async def list_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        """List model entities with pagination."""
        stmt = select(self.model_cls).limit(limit).offset(offset)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def create(self, entity: T) -> T:
        """Add and commit new entity."""
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def update(self, entity_id: Any, values: Dict[str, Any]) -> Optional[T]:
        """Update entity by ID with dictionary values."""
        id_attr = getattr(self.model_cls, "id")
        stmt = update(self.model_cls).where(id_attr == entity_id).values(**values)
        await self.session.execute(stmt)
        await self.session.commit()
        return await self.get_by_id(entity_id)

    async def delete(self, entity_id: Any) -> bool:
        """Delete entity by ID."""
        id_attr = getattr(self.model_cls, "id")
        stmt = delete(self.model_cls).where(id_attr == entity_id)
        res = await self.session.execute(stmt)
        await self.session.commit()
        rowcount = getattr(res, "rowcount", 0)
        return int(rowcount or 0) > 0
