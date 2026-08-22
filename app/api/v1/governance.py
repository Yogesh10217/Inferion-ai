"""FastAPI Router for Governance & Quotas (/v1/governance)."""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends
from app.governance.quota_manager import QuotaManager
from app.governance.resource_governance import ResourceGovernanceEngine

router = APIRouter(prefix="/v1/governance", tags=["governance"])

_global_quota_manager = QuotaManager()
_global_resource_governance = ResourceGovernanceEngine(quota_manager=_global_quota_manager)


def get_quota_manager() -> QuotaManager:
    return _global_quota_manager


def get_resource_governance() -> ResourceGovernanceEngine:
    return _global_resource_governance


@router.get("/usage")
async def get_usage(tenant_id: str = "global", manager: QuotaManager = Depends(get_quota_manager)):
    """Retrieve usage metrics for a tenant."""
    usage = manager.get_usage(tenant_id)
    return {"tenant_id": tenant_id, "usage": usage.model_dump()}


@router.get("/quotas")
async def get_quotas(tenant_id: str = "global", manager: QuotaManager = Depends(get_quota_manager)):
    """Retrieve quota limits and remaining allocations for a tenant."""
    defn = manager.get_definition(tenant_id)
    rem = manager.get_remaining(tenant_id)
    return {"definition": defn.model_dump(), "remaining": rem}


@router.get("/rate-limits")
async def get_rate_limits(gov: ResourceGovernanceEngine = Depends(get_resource_governance)):
    """Retrieve hardware and operational governance metrics."""
    health = gov.check_hardware_health()
    return {"status": "ok", "hardware_health": health}
