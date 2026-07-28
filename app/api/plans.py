from fastapi import APIRouter, Depends
from typing import List

from app.core.container import ServiceContainer
from app.api.dependencies import get_container
from app.billing.schemas import SubscriptionPlanOut
from app.auth.middleware import require_roles

router = APIRouter(prefix="/plans", tags=["Billing Plans"])

@router.get("", response_model=List[SubscriptionPlanOut])
async def list_plans(container: ServiceContainer = Depends(get_container)):
    """List all available subscription plans."""
    plans = await container.plan_service.get_all_plans()
    return plans
