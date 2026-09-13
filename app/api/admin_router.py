from fastapi import APIRouter, Depends, HTTPException, Query, Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session
from app.admin import SystemAdminService, HealthAdminService, UserAdminService, OrganizationAdminService, WorkspaceAdminService, APIKeyAdminService, SubscriptionAdminService, AuditAdminService, ReportAdminService
from app.auth.dependencies import require_admin
from app.auth.models import User
from app.admin.exceptions import ResourceNotFoundException, InvalidOperationException

# Use a single router for all admin routes, prefixed with /admin and enforcing the "admin" role globally.
# This ensures that ONLY platform administrators can access these endpoints.
admin_router = APIRouter(
    prefix="/admin",
    tags=["Administration"],
    dependencies=[Depends(require_admin)]
)

# ----------------- SYSTEM & HEALTH -----------------

@admin_router.get("/system")
async def get_system_stats(
    db: AsyncSession = Depends(get_db_session)
):
    """Retrieve overarching platform statistics."""
    return await SystemAdminService(db).get_system_stats()

@admin_router.get("/health")
async def get_admin_health(
    db: AsyncSession = Depends(get_db_session)
):
    """Retrieve comprehensive system health (DB, Redis, Providers)."""
    return await HealthAdminService(db).get_system_health()

# ----------------- USERS -----------------

@admin_router.get("/users")
async def list_users(
    limit: int = Query(100),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db_session)
):
    users = await UserAdminService(db).list_users(limit=limit, offset=offset)
    return [{"id": u.id, "username": u.username, "email": u.email, "is_active": u.is_active} for u in users]

class UserUpdate(BaseModel):
    is_active: bool

@admin_router.patch("/users/{user_id}")
async def update_user(
    update_data: UserUpdate,
    user_id: str = Path(...),
    db: AsyncSession = Depends(get_db_session)
):
    try:
        if update_data.is_active:
            user = await UserAdminService(db).enable_user(user_id)
        else:
            user = await UserAdminService(db).disable_user(user_id)
        return {"id": user.id, "is_active": user.is_active}
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))

# ----------------- ORGANIZATIONS -----------------

@admin_router.get("/organizations")
async def list_organizations(
    limit: int = Query(100),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db_session)
):
    orgs = await OrganizationAdminService(db).list_organizations(limit=limit, offset=offset)
    return [{"id": o.id, "name": o.name, "slug": o.slug, "status": o.status} for o in orgs]

class OrganizationUpdate(BaseModel):
    status: str # active, suspended, archived
    actor_id: Optional[str] = None

@admin_router.patch("/organizations/{org_id}")
async def update_organization(
    update_data: OrganizationUpdate,
    org_id: str = Path(...),
    db: AsyncSession = Depends(get_db_session)
):
    try:
        if update_data.status == "suspended":
            actor = update_data.actor_id or "system_admin"
            org = await OrganizationAdminService(db).suspend_organization(org_id, actor_id=actor)
        elif update_data.status == "active":
            org = await OrganizationAdminService(db).reactivate_organization(org_id)
        elif update_data.status == "archived":
            org = await OrganizationAdminService(db).archive_organization(org_id)
        else:
            raise HTTPException(status_code=400, detail="Invalid status")
        return {"id": org.id, "status": org.status}
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidOperationException as e:
        raise HTTPException(status_code=400, detail=str(e))

# ----------------- WORKSPACES -----------------

@admin_router.get("/workspaces")
async def list_workspaces(
    organization_id: Optional[str] = Query(None),
    limit: int = Query(100),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db_session)
):
    ws = await WorkspaceAdminService(db).list_workspaces(organization_id=organization_id, limit=limit, offset=offset)
    return [{"id": w.id, "name": w.name, "organization_id": w.organization_id} for w in ws]

@admin_router.patch("/workspaces/{workspace_id}")
async def update_workspace(
    update_data: dict,
    workspace_id: str = Path(...),
    db: AsyncSession = Depends(get_db_session)
):
    try:
        w = await WorkspaceAdminService(db).update_workspace(workspace_id, **update_data)
        return {"id": w.id, "name": w.name}
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))

# ----------------- API KEYS -----------------

@admin_router.get("/api-keys")
async def list_api_keys(
    user_id: Optional[str] = Query(None),
    organization_id: Optional[str] = Query(None),
    limit: int = Query(100),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db_session)
):
    keys = await APIKeyAdminService(db).list_api_keys(user_id=user_id, org_id=organization_id, limit=limit, offset=offset)
    return [{"id": k.id, "prefix": k.prefix, "revoked_at": k.revoked_at, "expires_at": k.expires_at} for k in keys]

class APIKeyUpdate(BaseModel):
    action: str # revoke, expire
    grace_period_days: int = 0

@admin_router.patch("/api-keys/{api_key_id}")
async def update_api_key(
    update_data: APIKeyUpdate,
    api_key_id: str = Path(...),
    db: AsyncSession = Depends(get_db_session)
):
    try:
        if update_data.action == "revoke":
            k = await APIKeyAdminService(db).revoke_api_key(api_key_id)
        elif update_data.action == "expire":
            k = await APIKeyAdminService(db).expire_api_key(api_key_id, in_days=update_data.grace_period_days)
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
        return {"id": k.id, "revoked_at": k.revoked_at, "expires_at": k.expires_at}
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))

# ----------------- SUBSCRIPTIONS -----------------

@admin_router.get("/subscriptions")
async def list_subscriptions(
    organization_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db_session)
):
    subs = await SubscriptionAdminService(db).list_subscriptions(organization_id=organization_id, status=status, limit=limit, offset=offset)
    return [{"id": s.id, "organization_id": s.organization_id, "status": s.status} for s in subs]

# ----------------- AUDIT & REPORTS -----------------

@admin_router.get("/audit")
async def search_audit_events(
    organization_id: Optional[str] = Query(None),
    actor_id: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    limit: int = Query(100),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db_session)
):
    events = await AuditAdminService(db).search_events(
        organization_id=organization_id,
        actor_id=actor_id,
        action=action,
        severity=severity,
        limit=limit,
        offset=offset
    )
    return [
        {
            "id": e.id, 
            "action": e.action, 
            "actor_id": e.actor_id, 
            "organization_id": e.organization_id,
            "severity": e.severity,
            "timestamp": e.timestamp
        } for e in events
    ]

@admin_router.post("/reports")
async def create_report(
    type: str = Query(...),
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(require_admin)
):
    """Asynchronously generate a report."""
    job = await ReportAdminService(db).create_report_job(type=type, created_by=user.id)
    return {"job_id": job.id, "status": job.status}

@admin_router.get("/reports")
async def list_reports(
    limit: int = Query(100),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db_session)
):
    jobs = await ReportAdminService(db).list_report_jobs(limit=limit, offset=offset)
    return [{"id": j.id, "type": j.type, "status": j.status, "created_at": j.created_at} for j in jobs]

# ----------------- DEAD-LETTER QUEUE -----------------

@admin_router.get("/dlq")
async def get_dead_letter_queue():
    """Retrieve permanently failed requests from Dead Letter Queue."""
    from app.main import app
    container = getattr(app.state, "container", None)
    if container and hasattr(container, "dead_letter_queue") and container.dead_letter_queue:
        entries = await container.dead_letter_queue.get_entries()
        return {"count": len(entries), "entries": [e.model_dump() for e in entries]}
    return {"count": 0, "entries": []}
