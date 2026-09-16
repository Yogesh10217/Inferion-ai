"""FastAPI Router for Extension Framework (/v1/extensions)."""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.extensions.exceptions import ExtensionFrameworkException
from app.extensions.manager import ExtensionManager

router = APIRouter(prefix="/v1/extensions", tags=["extensions"])

_global_ext_manager = ExtensionManager()


def get_extension_framework() -> ExtensionManager:
    return _global_ext_manager


# Schemas
class RegisterExtensionSchema(BaseModel):
    manifest: Dict[str, Any]
    tenant_id: str = "global"
    developer_id: str = "system"


class RollbackExtensionSchema(BaseModel):
    target_version: str


# Endpoints
@router.post("", status_code=status.HTTP_201_CREATED)
async def register_extension(data: RegisterExtensionSchema, mgr: ExtensionManager = Depends(get_extension_framework)):
    try:
        ext = mgr.loader.load_extension_from_manifest(data.manifest, tenant_id=data.tenant_id, developer_id=data.developer_id)
        mgr.registry.register_extension(ext)
        return {"status": "registered", "extension": ext.model_dump()}
    except ExtensionFrameworkException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("")
async def list_extensions(tenant_id: Optional[str] = None, extension_type: Optional[str] = None, mgr: ExtensionManager = Depends(get_extension_framework)):
    exts = mgr.registry.list_extensions(tenant_id=tenant_id)
    return {"extensions": [e.model_dump() for e in exts]}


@router.get("/{id}")
async def get_extension(id: str, mgr: ExtensionManager = Depends(get_extension_framework)):
    try:
        ext = mgr.registry.get_extension(id)
        return {"extension": ext.model_dump()}
    except ExtensionFrameworkException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/{id}/install")
async def install_extension(id: str, mgr: ExtensionManager = Depends(get_extension_framework)):
    try:
        ext = mgr.registry.get_extension(id)
        mgr.lifecycle_manager.transition(ext, mgr.lifecycle_manager.get_state(id), "Installed")
        return {"status": "installed", "extension": ext.model_dump()}
    except ExtensionFrameworkException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/{id}/enable")
async def enable_extension(id: str, mgr: ExtensionManager = Depends(get_extension_framework)):
    try:
        ext = mgr.registry.get_extension(id)
        mgr.lifecycle_manager.enable_extension(ext)
        return {"status": "enabled", "extension": ext.model_dump()}
    except ExtensionFrameworkException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/{id}/disable")
async def disable_extension(id: str, mgr: ExtensionManager = Depends(get_extension_framework)):
    try:
        ext = mgr.registry.get_extension(id)
        mgr.lifecycle_manager.disable_extension(ext)
        return {"status": "disabled", "extension": ext.model_dump()}
    except ExtensionFrameworkException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/{id}/rollback")
async def rollback_extension(id: str, data: RollbackExtensionSchema, mgr: ExtensionManager = Depends(get_extension_framework)):
    try:
        ext = mgr.registry.get_extension(id)
        mgr.lifecycle_manager.rollback_extension(ext, data.target_version)
        return {"status": "rolled_back", "extension": ext.model_dump()}
    except ExtensionFrameworkException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
