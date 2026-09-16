from fastapi import APIRouter, Depends, HTTPException, Request

from app.api.dependencies import get_container
from app.auth.middleware import require_roles
from app.billing.exceptions import InvalidPlanException
from app.core.container import ServiceContainer

router = APIRouter(prefix="/subscriptions", tags=["Billing Subscriptions"])


@router.get("", response_model=dict)
@require_roles(["admin", "org_admin"])
async def get_active_subscription(request: Request, container: ServiceContainer = Depends(get_container)):
    """Get active subscription for the current organization."""
    org_id = request.state.organization_id
    sub = await container.subscription_service.get_active_subscription(org_id)
    if not sub:
        raise HTTPException(status_code=404, detail="No active subscription found")
    return {
        "id": sub.id,
        "organization_id": sub.organization_id,
        "plan": {
            "id": sub.plan.id,
            "name": sub.plan.name,
            "monthly_price": sub.plan.monthly_price
        },
        "status": sub.status,
        "expires_at": sub.expires_at
    }


@router.post("/{plan_id}")
@require_roles(["admin", "org_admin"])
async def assign_subscription(plan_id: str, request: Request, container: ServiceContainer = Depends(get_container)):
    """Assign or switch the subscription plan for the current organization."""
    org_id = request.state.organization_id
    try:
        sub = await container.subscription_service.assign_plan(org_id, plan_id)
        return {"status": "success", "subscription_id": sub.id}
    except InvalidPlanException as e:
        raise HTTPException(status_code=400, detail=str(e))
