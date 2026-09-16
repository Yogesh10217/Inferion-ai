"""FastAPI Router for Developer Platform (/v1/developers & /v1/events)."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.developer_platform.exceptions import DeveloperPlatformException
from app.developer_platform.manager import DeveloperPlatformManager
from app.developer_platform.project import ProjectLifecycle

router = APIRouter(tags=["developers"])

_global_dev_manager = DeveloperPlatformManager()


def get_dev_platform() -> DeveloperPlatformManager:
    return _global_dev_manager


# Schemas
class RegisterDeveloperSchema(BaseModel):
    user_id: str
    full_name: str
    email: str
    tenant_id: str = "global"
    company: Optional[str] = None


class CreateProjectSchema(BaseModel):
    name: str
    organization_id: str
    workspace_id: str
    developer_id: str
    tenant_id: str = "global"
    description: str = ""
    repository_url: Optional[str] = None


class TransitionProjectSchema(BaseModel):
    target_state: ProjectLifecycle


class CreateSubscriptionSchema(BaseModel):
    developer_id: str
    target_url: str
    event_types: List[str]
    tenant_id: str = "global"


# Developer Endpoints
@router.post("/v1/developers", status_code=status.HTTP_201_CREATED)
async def register_developer(data: RegisterDeveloperSchema, mgr: DeveloperPlatformManager = Depends(get_dev_platform)):
    dev = mgr.developer_manager.register_developer(
        user_id=data.user_id,
        full_name=data.full_name,
        email=data.email,
        tenant_id=data.tenant_id,
        company=data.company,
    )
    return {"status": "registered", "developer": dev.model_dump()}


@router.get("/v1/developers/me")
async def get_current_developer(developer_id: str = "dev_default", mgr: DeveloperPlatformManager = Depends(get_dev_platform)):
    try:
        dev = mgr.developer_manager.get_developer(developer_id)
        return {"developer": dev.model_dump()}
    except DeveloperPlatformException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


# Project Endpoints
@router.post("/v1/developers/projects", status_code=status.HTTP_201_CREATED)
async def create_project(data: CreateProjectSchema, mgr: DeveloperPlatformManager = Depends(get_dev_platform)):
    proj = mgr.project_manager.create_project(
        name=data.name,
        organization_id=data.organization_id,
        workspace_id=data.workspace_id,
        developer_id=data.developer_id,
        tenant_id=data.tenant_id,
        description=data.description,
        repository_url=data.repository_url,
    )
    return {"status": "created", "project": proj.model_dump()}


@router.get("/v1/developers/projects")
async def list_projects(tenant_id: Optional[str] = None, developer_id: Optional[str] = None, mgr: DeveloperPlatformManager = Depends(get_dev_platform)):
    projs = mgr.project_manager.list_projects(tenant_id=tenant_id, developer_id=developer_id)
    return {"projects": [p.model_dump() for p in projs]}


@router.get("/v1/developers/projects/{id}")
async def get_project(id: str, mgr: DeveloperPlatformManager = Depends(get_dev_platform)):
    try:
        proj = mgr.project_manager.get_project(id)
        return {"project": proj.model_dump()}
    except DeveloperPlatformException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.patch("/v1/developers/projects/{id}")
async def transition_project(id: str, data: TransitionProjectSchema, mgr: DeveloperPlatformManager = Depends(get_dev_platform)):
    try:
        proj = mgr.project_manager.transition_lifecycle(id, data.target_state)
        return {"status": "updated", "project": proj.model_dump()}
    except DeveloperPlatformException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


# Event & Webhook Endpoints
@router.post("/v1/events/subscriptions", status_code=status.HTTP_201_CREATED)
async def create_subscription(data: CreateSubscriptionSchema, mgr: DeveloperPlatformManager = Depends(get_dev_platform)):
    sub = mgr.event_engine.create_subscription(
        developer_id=data.developer_id,
        target_url=data.target_url,
        event_types=data.event_types,
        tenant_id=data.tenant_id,
    )
    return {"status": "created", "subscription": sub.model_dump()}


@router.get("/v1/events/subscriptions")
async def list_subscriptions(tenant_id: Optional[str] = None, developer_id: Optional[str] = None, mgr: DeveloperPlatformManager = Depends(get_dev_platform)):
    subs = mgr.event_engine.list_subscriptions(tenant_id=tenant_id, developer_id=developer_id)
    return {"subscriptions": [s.model_dump() for s in subs]}


@router.delete("/v1/events/subscriptions/{id}")
async def delete_subscription(id: str, mgr: DeveloperPlatformManager = Depends(get_dev_platform)):
    try:
        mgr.event_engine.delete_subscription(id)
        return {"status": "deleted"}
    except DeveloperPlatformException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
