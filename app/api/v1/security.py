"""FastAPI Router for Security & API Key Management (/v1/security)."""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field

from app.security.api_keys import APIKeyManager, APIKeyPolicy
from app.security.exceptions import InvalidAPIKeyError

router = APIRouter(prefix="/v1/security", tags=["security"])

_global_key_manager = APIKeyManager()


def get_key_manager() -> APIKeyManager:
    return _global_key_manager


class CreateAPIKeySchema(BaseModel):
    name: str
    tenant_id: str = "global"
    organization_id: Optional[str] = None
    workspace_id: Optional[str] = None
    user_id: Optional[str] = None
    expires_in_days: Optional[int] = None
    scopes: List[str] = Field(default_factory=lambda: ["read", "write"])


@router.post("/api-keys", status_code=status.HTTP_201_CREATED)
async def create_api_key(data: CreateAPIKeySchema, manager: APIKeyManager = Depends(get_key_manager)):
    """Create a new API key."""
    pol = APIKeyPolicy(scopes=data.scopes)
    res = manager.generate_api_key(
        name=data.name,
        tenant_id=data.tenant_id,
        organization_id=data.organization_id,
        workspace_id=data.workspace_id,
        user_id=data.user_id,
        policy=pol,
        expires_in_days=data.expires_in_days,
    )
    return {"status": "created", "api_key": res}


@router.get("/api-keys")
async def list_api_keys(tenant_id: str = "global", manager: APIKeyManager = Depends(get_key_manager)):
    """List API keys metadata."""
    keys = manager.list_api_keys(tenant_id=tenant_id)
    return {"api_keys": [k.model_dump() for k in keys]}


@router.delete("/api-keys/{id}")
async def revoke_api_key(id: str, manager: APIKeyManager = Depends(get_key_manager)):
    """Revoke an API key by ID."""
    try:
        key = manager.revoke_api_key(id)
        return {"status": "revoked", "key_id": id}
    except InvalidAPIKeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"API key '{id}' not found")


@router.post("/api-keys/{id}/rotate")
async def rotate_api_key(id: str, expires_in_days: Optional[int] = None, manager: APIKeyManager = Depends(get_key_manager)):
    """Rotate an API key, issuing a new key with identical policy while revoking the old one."""
    try:
        res = manager.rotate_api_key(id, expires_in_days=expires_in_days)
        return {"status": "rotated", "api_key": res}
    except InvalidAPIKeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"API key '{id}' not found")
