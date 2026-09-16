from typing import List

from fastapi import APIRouter, Depends

from app.api.dependencies import get_container
from app.billing.schemas import SubscriptionPlanOut
from app.core.container import ServiceContainer

router = APIRouter(prefix="/plans", tags=["Billing Plans"])


@router.get("", response_model=List[SubscriptionPlanOut])
async def list_plans(container: ServiceContainer = Depends(get_container)):
    """List all available subscription plans."""
    plans = await container.plan_service.get_all_plans()
    return plans
