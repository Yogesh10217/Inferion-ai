from datetime import datetime
from typing import Any, List, Optional

from sqlalchemy import and_, select

from app.auth.models import AuditEvent


class AuditAdminService:
    def __init__(self, db: Any):
        self.db = db

    async def record_event(
        self,
        action: str,
        organization_id: str,
        actor_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        severity: str = "info",
        details: Optional[dict] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
    ) -> AuditEvent:
        event = AuditEvent(
            action=action,
            actor_id=actor_id,
            organization_id=organization_id,
            workspace_id=workspace_id,
            resource_type=resource_type,
            resource_id=resource_id,
            severity=severity,
            details=str(details) if details else None,
            category=category,
        )
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)
        return event

    async def search_events(
        self,
        organization_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        actor_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        action: Optional[str] = None,
        severity: Optional[str] = None,
        category: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[AuditEvent]:
        stmt = select(AuditEvent)
        conditions = []

        if organization_id:
            conditions.append(AuditEvent.organization_id == organization_id)
        if workspace_id:
            conditions.append(AuditEvent.workspace_id == workspace_id)
        if actor_id:
            conditions.append(AuditEvent.actor_id == actor_id)
        if resource_type:
            conditions.append(AuditEvent.resource_type == resource_type)
        if resource_id:
            conditions.append(AuditEvent.resource_id == resource_id)
        if action:
            conditions.append(AuditEvent.action == action)
        if severity:
            conditions.append(AuditEvent.severity == severity)
        if category:
            conditions.append(AuditEvent.category == category)
        if start_time:
            conditions.append(AuditEvent.timestamp >= start_time)
        if end_time:
            conditions.append(AuditEvent.timestamp <= end_time)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        stmt = stmt.order_by(AuditEvent.timestamp.desc()).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
