from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.auth_service import AuthService
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.core.database import get_db_session
from app.tenant.models import Workspace
from app.tenant.schemas import WorkspaceCreate, WorkspaceResponse, WorkspaceUpdate

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


@router.post("", response_model=WorkspaceResponse, status_code=201)
async def create_workspace(
    ws_in: WorkspaceCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    org_id = getattr(request.state, "organization_id", None)
    if not org_id:
        raise HTTPException(status_code=403, detail="Organization context required")

    ws = Workspace(
        organization_id=org_id,
        name=ws_in.name,
        description=ws_in.description
    )
    db.add(ws)
    await db.flush()

    ip_address = request.client.host if request.client else None
    await AuthService.log_audit_event(
        db, "workspace_created",
        organization_id=org_id,
        workspace_id=ws.id,
        actor_id=current_user.id,
        resource_type="Workspace",
        resource_id=ws.id,
        ip_address=ip_address
    )

    await db.commit()
    await db.refresh(ws)
    return ws


@router.get("", response_model=List[WorkspaceResponse])
async def list_workspaces(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    org_id = getattr(request.state, "organization_id", None)
    if not org_id:
        raise HTTPException(status_code=403, detail="Organization context required")

    stmt = select(Workspace).where(Workspace.organization_id == org_id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.patch("/{ws_id}", response_model=WorkspaceResponse)
async def update_workspace(
    ws_id: str,
    ws_in: WorkspaceUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    org_id = getattr(request.state, "organization_id", None)
    if not org_id:
        raise HTTPException(status_code=403, detail="Organization context required")

    stmt = select(Workspace).where(Workspace.id == ws_id, Workspace.organization_id == org_id)
    result = await db.execute(stmt)
    ws = result.scalar_one_or_none()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")

    if ws_in.name is not None:
        ws.name = ws_in.name
    if ws_in.description is not None:
        ws.description = ws_in.description

    ip_address = request.client.host if request.client else None
    await AuthService.log_audit_event(
        db, "workspace_updated",
        organization_id=org_id,
        workspace_id=ws.id,
        actor_id=current_user.id,
        resource_type="Workspace",
        resource_id=ws.id,
        ip_address=ip_address
    )

    await db.commit()
    await db.refresh(ws)
    return ws


@router.delete("/{ws_id}", status_code=204)
async def delete_workspace(
    ws_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    org_id = getattr(request.state, "organization_id", None)
    if not org_id:
        raise HTTPException(status_code=403, detail="Organization context required")

    stmt = select(Workspace).where(Workspace.id == ws_id, Workspace.organization_id == org_id)
    result = await db.execute(stmt)
    ws = result.scalar_one_or_none()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")

    await db.delete(ws)

    ip_address = request.client.host if request.client else None
    await AuthService.log_audit_event(
        db, "workspace_deleted",
        organization_id=org_id,
        workspace_id=ws_id,
        actor_id=current_user.id,
        resource_type="Workspace",
        resource_id=ws_id,
        ip_address=ip_address
    )

    await db.commit()
