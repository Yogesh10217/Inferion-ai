from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request

from app.api.dependencies import get_container
from app.auth.middleware import require_roles
from app.billing.schemas import BudgetCreate, BudgetOut
from app.core.container import ServiceContainer

router = APIRouter(prefix="/budgets", tags=["Billing Budgets"])


@router.get("", response_model=List[BudgetOut])
@require_roles(["admin", "org_admin"])
async def list_budgets(request: Request, workspace_id: Optional[str] = None, container: ServiceContainer = Depends(get_container)):
    org_id = request.state.organization_id
    budget = await container.budget_service.get_budget(org_id, workspace_id)
    if not budget:
        return []
    return [budget]


@router.post("", response_model=BudgetOut)
@require_roles(["admin", "org_admin"])
async def set_budget(payload: BudgetCreate, request: Request, container: ServiceContainer = Depends(get_container)):
    org_id = request.state.organization_id
    # Security: Ensure they can only set budget for their org
    if payload.organization_id != org_id:
        raise HTTPException(status_code=403, detail="Cannot set budget for another organization")

    budget = await container.budget_service.create_or_update_budget(
        org_id=payload.organization_id,
        workspace_id=payload.workspace_id,
        hard_limit=payload.hard_limit,
        warning=payload.warning_threshold,
        critical=payload.critical_threshold
    )
    return budget
