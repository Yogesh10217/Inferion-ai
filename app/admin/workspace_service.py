from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.tenant.models import Workspace
from app.admin.exceptions import ResourceNotFoundException

class WorkspaceAdminService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_workspace(self, name: str, organization_id: str, slug: Optional[str] = None, description: Optional[str] = None) -> Workspace:
        ws = Workspace(name=name, organization_id=organization_id, description=description)
        self.db.add(ws)
        await self.db.commit()
        await self.db.refresh(ws)
        return ws

    async def list_workspaces(self, organization_id: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[Workspace]:
        stmt = select(Workspace)
        if organization_id:
            stmt = stmt.where(Workspace.organization_id == organization_id)
        stmt = stmt.limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_workspace(self, workspace_id: str) -> Workspace:
        workspace = await self.db.get(Workspace, workspace_id)
        if not workspace:
            raise ResourceNotFoundException(f"Workspace {workspace_id} not found")
        return workspace

    async def update_workspace(self, workspace_id: str, **kwargs) -> Workspace:
        workspace = await self.get_workspace(workspace_id)
        for key, value in kwargs.items():
            if hasattr(workspace, key):
                setattr(workspace, key, value)
        await self.db.commit()
        await self.db.refresh(workspace)
        return workspace
