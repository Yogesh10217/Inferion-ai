"""FastAPI Router for Enterprise Control Plane (/v1/control-plane)."""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.control_plane.configuration import ConfigurationScope
from app.control_plane.exceptions import ApprovalRequiredException, ControlPlaneException
from app.control_plane.manager import ControlPlaneManager
from app.control_plane.policy_manager import PolicyTargetType
from app.control_plane.resource_registry import ResourceType
from app.control_plane.workspace import WorkspaceEnvironment

router = APIRouter(prefix="/v1/control-plane", tags=["control-plane"])

_global_control_plane = ControlPlaneManager()


def get_control_plane() -> ControlPlaneManager:
    return _global_control_plane


# Schemas
class CreateTenantSchema(BaseModel):
    name: str
    slug: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CreateOrgSchema(BaseModel):
    name: str
    tenant_id: str = "global"
    slug: Optional[str] = None


class CreateWorkspaceSchema(BaseModel):
    name: str
    organization_id: str
    tenant_id: str = "global"
    environment: WorkspaceEnvironment = WorkspaceEnvironment.DEVELOPMENT


class ConfigUpdateSchema(BaseModel):
    scope: ConfigurationScope
    target_id: str
    settings: Dict[str, Any]


class CreatePolicySchema(BaseModel):
    name: str
    target_type: PolicyTargetType
    tenant_id: str = "global"
    rules: Dict[str, Any] = Field(default_factory=dict)


class AdminOpSchema(BaseModel):
    action: str
    target_id: str
    tenant_id: str = "global"
    approved: bool = False


# Summary Endpoint
@router.get("/summary")
async def get_summary(cp: ControlPlaneManager = Depends(get_control_plane)):
    return cp.get_summary()


# Tenant Endpoints
@router.post("/tenants", status_code=status.HTTP_201_CREATED)
async def create_tenant(data: CreateTenantSchema, cp: ControlPlaneManager = Depends(get_control_plane)):
    bundle = cp.provisioning_engine.provision_new_tenant(tenant_name=data.name, org_name=data.slug)
    return {"status": "created", "tenant_bundle": bundle.model_dump()}


@router.get("/tenants")
async def list_tenants(cp: ControlPlaneManager = Depends(get_control_plane)):
    tenants = cp.tenant_manager.list_tenants()
    return {"tenants": [t.model_dump() for t in tenants]}


@router.get("/tenants/{id}")
async def get_tenant(id: str, cp: ControlPlaneManager = Depends(get_control_plane)):
    try:
        t = cp.tenant_manager.get_tenant(id)
        return {"tenant": t.model_dump()}
    except ControlPlaneException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/tenants/{id}/suspend")
async def suspend_tenant(id: str, cp: ControlPlaneManager = Depends(get_control_plane)):
    try:
        t = cp.tenant_manager.suspend_tenant(id)
        return {"status": "suspended", "tenant": t.model_dump()}
    except ControlPlaneException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/tenants/{id}/activate")
async def activate_tenant(id: str, cp: ControlPlaneManager = Depends(get_control_plane)):
    try:
        t = cp.tenant_manager.activate_tenant(id)
        return {"status": "activated", "tenant": t.model_dump()}
    except ControlPlaneException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


# Organization Endpoints
@router.post("/organizations", status_code=status.HTTP_201_CREATED)
async def create_organization(data: CreateOrgSchema, cp: ControlPlaneManager = Depends(get_control_plane)):
    org = cp.organization_manager.create_organization(name=data.name, tenant_id=data.tenant_id, slug=data.slug)
    return {"status": "created", "organization": org.model_dump()}


@router.get("/organizations")
async def list_organizations(tenant_id: Optional[str] = None, cp: ControlPlaneManager = Depends(get_control_plane)):
    orgs = cp.organization_manager.list_organizations(tenant_id=tenant_id)
    return {"organizations": [o.model_dump() for o in orgs]}


# Workspace Endpoints
@router.post("/workspaces", status_code=status.HTTP_201_CREATED)
async def create_workspace(data: CreateWorkspaceSchema, cp: ControlPlaneManager = Depends(get_control_plane)):
    ws = cp.provisioning_engine.provision_new_workspace(
        workspace_name=data.name,
        organization_id=data.organization_id,
        tenant_id=data.tenant_id,
        environment=data.environment,
    )
    return {"status": "created", "workspace": ws.model_dump()}


@router.get("/workspaces")
async def list_workspaces(tenant_id: Optional[str] = None, organization_id: Optional[str] = None, cp: ControlPlaneManager = Depends(get_control_plane)):
    wss = cp.workspace_manager.list_workspaces(tenant_id=tenant_id, organization_id=organization_id)
    return {"workspaces": [w.model_dump() for w in wss]}


# Resource Inventory
@router.get("/resources")
async def list_resources(tenant_id: Optional[str] = None, resource_type: Optional[str] = None, cp: ControlPlaneManager = Depends(get_control_plane)):
    rt = ResourceType(resource_type.upper()) if resource_type else None
    res = cp.resource_registry.list_resources(tenant_id=tenant_id, resource_type=rt)
    return {"resources": [r.model_dump() for r in res]}


# Configuration
@router.get("/configuration")
async def get_configuration(scope: ConfigurationScope, target_id: str, cp: ControlPlaneManager = Depends(get_control_plane)):
    cfg = cp.configuration_manager.get_configuration(scope=scope, target_id=target_id)
    return {"scope": scope.value, "target_id": target_id, "configuration": cfg}


@router.post("/configuration")
async def update_configuration(data: ConfigUpdateSchema, cp: ControlPlaneManager = Depends(get_control_plane)):
    cp.configuration_validator.validate_configuration(data.settings)
    ver = cp.configuration_manager.update_configuration(scope=data.scope, target_id=data.target_id, settings_update=data.settings)
    return {"status": "updated", "version": ver.model_dump()}


@router.post("/configuration/{version}/rollback")
async def rollback_configuration(version: int, scope: ConfigurationScope, target_id: str, cp: ControlPlaneManager = Depends(get_control_plane)):
    ver = cp.configuration_manager.rollback_configuration(scope=scope, target_id=target_id, target_version_number=version)
    return {"status": "rolled_back", "version": ver.model_dump()}


# Policies
@router.post("/policies", status_code=status.HTTP_201_CREATED)
async def create_policy(data: CreatePolicySchema, cp: ControlPlaneManager = Depends(get_control_plane)):
    pol = cp.policy_manager.create_policy(name=data.name, target_type=data.target_type, tenant_id=data.tenant_id, rules=data.rules)
    return {"status": "created", "policy": pol.model_dump()}


@router.get("/policies")
async def list_policies(tenant_id: Optional[str] = None, cp: ControlPlaneManager = Depends(get_control_plane)):
    pols = cp.policy_manager.list_policies(tenant_id=tenant_id)
    return {"policies": [p.model_dump() for p in pols]}


@router.post("/policies/{id}/simulate")
async def simulate_policy(id: str, cp: ControlPlaneManager = Depends(get_control_plane)):
    pol = cp.policy_manager.get_policy(id)
    if not pol:
        raise HTTPException(status_code=404, detail="Policy not found")
    sim = cp.policy_simulator.simulate_policy_impact(name=pol.name, target_type=pol.target_type, rules=pol.rules, tenant_id=pol.tenant_id)
    return {"impact_report": sim.model_dump()}


# Features
@router.get("/features")
async def list_features(cp: ControlPlaneManager = Depends(get_control_plane)):
    flags = cp.feature_manager.list_features()
    return {"features": [f.model_dump() for f in flags]}


# Admin Operations
@router.post("/operations")
async def execute_operation(data: AdminOpSchema, cp: ControlPlaneManager = Depends(get_control_plane)):
    try:
        res = cp.admin_operations.execute_operation(action=data.action, target_id=data.target_id, tenant_id=data.tenant_id, approved=data.approved)
        return {"operation": res.model_dump()}
    except ApprovalRequiredException as e:
        raise HTTPException(status_code=402, detail=e.message)


# Usage & Analytics
@router.get("/usage")
async def get_usage(tenant_id: str = "global", cp: ControlPlaneManager = Depends(get_control_plane)):
    rep = cp.usage_analytics.generate_tenant_report(tenant_id)
    return {"usage_report": rep}
