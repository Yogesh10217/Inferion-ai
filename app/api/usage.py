from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter(prefix="/usage", tags=["usage"])


class UsageSummary(BaseModel):
    total_requests: int
    total_tokens: int
    average_latency_ms: int
    total_errors: int


@router.get("", response_model=List[dict])
async def list_usage(
    organization_id: Optional[str] = None,
    workspace_id: Optional[str] = None,
    user_id: Optional[str] = None,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(default=50, le=100),
):
    # Dummy implementation for walkthrough
    return []


@router.get("/summary", response_model=UsageSummary)
async def get_usage_summary(
    organization_id: Optional[str] = None,
    workspace_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
):
    # Dummy implementation for walkthrough
    return UsageSummary(total_requests=0, total_tokens=0, average_latency_ms=0, total_errors=0)


@router.get("/organizations/{org_id}", response_model=UsageSummary)
async def get_org_usage(org_id: str):
    return UsageSummary(total_requests=0, total_tokens=0, average_latency_ms=0, total_errors=0)


@router.get("/workspaces/{workspace_id}", response_model=UsageSummary)
async def get_workspace_usage(workspace_id: str):
    return UsageSummary(total_requests=0, total_tokens=0, average_latency_ms=0, total_errors=0)
