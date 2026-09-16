from typing import List, Optional

from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter(prefix="/quotas", tags=["quotas"])


class QuotaCreate(BaseModel):
    name: str
    organization_id: Optional[str] = None
    workspace_id: Optional[str] = None
    user_id: Optional[str] = None
    api_key_id: Optional[str] = None
    requests_per_minute: Optional[int] = None
    requests_per_day: Optional[int] = None
    tokens_per_day: Optional[int] = None
    tokens_per_month: Optional[int] = None
    concurrent_requests: Optional[int] = None


class QuotaResponse(QuotaCreate):
    id: str
    enabled: bool


@router.post("", response_model=QuotaResponse, status_code=status.HTTP_201_CREATED)
async def create_quota(quota: QuotaCreate):
    # Dummy implementation for walkthrough
    return QuotaResponse(id="q_123", enabled=True, **quota.dict())


@router.get("", response_model=List[QuotaResponse])
async def list_quotas(organization_id: Optional[str] = None):
    # Dummy implementation for walkthrough
    return []


@router.patch("/{quota_id}", response_model=QuotaResponse)
async def update_quota(quota_id: str, quota: QuotaCreate):
    return QuotaResponse(id=quota_id, enabled=True, **quota.dict())


@router.delete("/{quota_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quota(quota_id: str):
    pass
