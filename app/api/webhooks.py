from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_admin
from app.auth.models import User
from app.core.database import async_session_maker, get_db_session
from app.events import (
    DeadLetterQueue,
    DeliveryService,
    EndpointNotFoundException,
    EventStorage,
    WebhookService,
)

router = APIRouter(
    prefix="/webhooks",
    tags=["Webhooks"],
    dependencies=[Depends(require_admin)],
)


def _get_webhook_service(db: AsyncSession) -> WebhookService:
    storage = EventStorage(db)
    delivery_svc = DeliveryService(storage)
    dlq = DeadLetterQueue(storage, delivery_svc)
    return WebhookService(storage, delivery_svc, dlq)


# Pydantic Schemas

class WebhookEndpointCreate(BaseModel):
    organization_id: str
    url: str
    event_types: List[str]
    secret: Optional[str] = None
    enabled: bool = True
    retry_policy: Optional[Dict[str, Any]] = None


class WebhookEndpointUpdate(BaseModel):
    url: Optional[str] = None
    event_types: Optional[List[str]] = None
    secret: Optional[str] = None
    enabled: Optional[bool] = None
    retry_policy: Optional[Dict[str, Any]] = None


# Endpoints

@router.get("", response_model=List[Dict[str, Any]])
async def list_webhook_endpoints(
    organization_id: Optional[str] = Query(None),
    limit: int = Query(100),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db_session),
):
    service = _get_webhook_service(db)
    endpoints = await service.list_endpoints(organization_id=organization_id, limit=limit, offset=offset)
    return [
        {
            "id": ep.id,
            "organization_id": ep.organization_id,
            "url": ep.url,
            "enabled": ep.enabled,
            "event_types": ep.event_types,
            "created_at": ep.created_at,
            "updated_at": ep.updated_at,
        }
        for ep in endpoints
    ]


@router.post("", status_code=201)
async def create_webhook_endpoint(
    data: WebhookEndpointCreate,
    db: AsyncSession = Depends(get_db_session),
):
    service = _get_webhook_service(db)
    ep = await service.create_endpoint(
        organization_id=data.organization_id,
        url=data.url,
        event_types=data.event_types,
        secret=data.secret,
        enabled=data.enabled,
        retry_policy=data.retry_policy,
    )
    return {
        "id": ep.id,
        "organization_id": ep.organization_id,
        "url": ep.url,
        "secret": ep.secret,
        "enabled": ep.enabled,
        "event_types": ep.event_types,
        "created_at": ep.created_at,
    }


@router.patch("/{id}")
async def update_webhook_endpoint(
    data: WebhookEndpointUpdate,
    id: str = Path(...),
    db: AsyncSession = Depends(get_db_session),
):
    service = _get_webhook_service(db)
    try:
        kwargs = {k: v for k, v in data.model_dump().items() if v is not None}
        ep = await service.update_endpoint(id, **kwargs)
        return {
            "id": ep.id,
            "url": ep.url,
            "enabled": ep.enabled,
            "event_types": ep.event_types,
            "updated_at": ep.updated_at,
        }
    except EndpointNotFoundException as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.delete("/{id}")
async def delete_webhook_endpoint(
    id: str = Path(...),
    db: AsyncSession = Depends(get_db_session),
):
    service = _get_webhook_service(db)
    try:
        await service.delete_endpoint(id)
        return {"status": "deleted", "id": id}
    except EndpointNotFoundException as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/deliveries")
async def list_webhook_deliveries(
    endpoint_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db_session),
):
    service = _get_webhook_service(db)
    deliveries = await service.list_deliveries(endpoint_id=endpoint_id, status=status, limit=limit, offset=offset)
    return [
        {
            "id": d.id,
            "endpoint_id": d.endpoint_id,
            "event_id": d.event_id,
            "status": d.status,
            "attempts": d.attempts,
            "latency_ms": d.latency_ms,
            "response_code": d.response_code,
            "is_replay": d.is_replay,
            "delivered_at": d.delivered_at,
            "created_at": d.created_at,
        }
        for d in deliveries
    ]


@router.get("/events")
async def list_webhook_events(
    organization_id: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    limit: int = Query(100),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db_session),
):
    service = _get_webhook_service(db)
    events = await service.list_events(organization_id=organization_id, event_type=event_type, limit=limit, offset=offset)
    return [
        {
            "id": e.id,
            "event_type": e.event_type,
            "version": e.version,
            "organization_id": e.organization_id,
            "workspace_id": e.workspace_id,
            "source": e.source,
            "correlation_id": e.correlation_id,
            "timestamp": e.timestamp,
            "payload": e.payload,
        }
        for e in events
    ]


@router.post("/replay/{delivery_id}")
async def replay_webhook_delivery(
    delivery_id: str = Path(...),
    db: AsyncSession = Depends(get_db_session),
):
    service = _get_webhook_service(db)
    try:
        new_delivery = await service.replay_delivery(delivery_id)
        return {
            "replayed_delivery_id": delivery_id,
            "new_delivery_id": new_delivery.id,
            "status": new_delivery.status,
            "attempts": new_delivery.attempts,
            "is_replay": new_delivery.is_replay,
        }
    except EndpointNotFoundException as exc:
        raise HTTPException(status_code=404, detail=str(exc))
