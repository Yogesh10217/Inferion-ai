"""FastAPI Router for Marketplace Platform (/v1/marketplace)."""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.extensions.extension import ExtensionManifest
from app.marketplace.exceptions import MarketplaceException
from app.marketplace.manager import MarketplaceManager
from app.marketplace.marketplace_item import ItemLifecycle, MarketplaceCategory, MarketplaceItem

router = APIRouter(prefix="/v1/marketplace", tags=["marketplace"])

_global_mkt_manager = MarketplaceManager()


def get_marketplace() -> MarketplaceManager:
    return _global_mkt_manager


# Schemas
class CreateItemSchema(BaseModel):
    title: str
    summary: str = ""
    category: MarketplaceCategory
    publisher_id: str
    manifest: Dict[str, Any]


class InstallItemSchema(BaseModel):
    tenant_id: str = "global"
    developer_id: str = "system"


# Endpoints
@router.post("/items", status_code=status.HTTP_201_CREATED)
async def create_item(data: CreateItemSchema, mgr: MarketplaceManager = Depends(get_marketplace)):
    try:
        manifest = ExtensionManifest(**data.manifest)
        item = MarketplaceItem(
            title=data.title,
            summary=data.summary,
            category=data.category,
            publisher_id=data.publisher_id,
            manifest=manifest,
        )
        mgr.registry.register_item(item)
        return {"status": "created", "item": item.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/items")
async def list_items(category: Optional[MarketplaceCategory] = None, mgr: MarketplaceManager = Depends(get_marketplace)):
    items = mgr.registry.list_items(category=category, published_only=False)
    return {"items": [i.model_dump() for i in items]}


@router.get("/items/{id}")
async def get_item(id: str, mgr: MarketplaceManager = Depends(get_marketplace)):
    try:
        item = mgr.registry.get_item(id)
        return {"item": item.model_dump()}
    except MarketplaceException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/items/{id}/submit")
async def submit_item(id: str, mgr: MarketplaceManager = Depends(get_marketplace)):
    try:
        item = mgr.registry.get_item(id)
        res = mgr.review_engine.review_item_submission(item)
        return {"review_result": res.model_dump(), "item": item.model_dump()}
    except MarketplaceException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/items/{id}/approve")
async def approve_item(id: str, mgr: MarketplaceManager = Depends(get_marketplace)):
    try:
        item = mgr.registry.get_item(id)
        item.status = ItemLifecycle.APPROVED
        return {"status": "approved", "item": item.model_dump()}
    except MarketplaceException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/items/{id}/publish")
async def publish_item(id: str, mgr: MarketplaceManager = Depends(get_marketplace)):
    try:
        item = mgr.registry.get_item(id)
        item.status = ItemLifecycle.PUBLISHED
        return {"status": "published", "item": item.model_dump()}
    except MarketplaceException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/items/{id}/install")
async def install_item(id: str, data: InstallItemSchema, mgr: MarketplaceManager = Depends(get_marketplace)):
    try:
        item = mgr.registry.get_item(id)
        ext = mgr.installation_manager.install_marketplace_item(item, tenant_id=data.tenant_id, developer_id=data.developer_id)
        return {"status": "installed", "extension": ext.model_dump()}
    except MarketplaceException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
