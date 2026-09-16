from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, Request

from app.api.dependencies import get_container
from app.auth.middleware import require_roles
from app.billing.schemas import InvoiceOut, PricingRuleOut
from app.core.container import ServiceContainer

router = APIRouter(prefix="/billing", tags=["Billing"])


@router.get("/invoices", response_model=List[InvoiceOut])
@require_roles(["admin", "org_admin"])
async def list_invoices(
    request: Request,
    status: Optional[str] = Query(None, description="Filter by status"),
    container: ServiceContainer = Depends(get_container)
):
    """List invoices for the current organization."""
    org_id = request.state.organization_id
    invoices = await container.invoice_service.list_invoices(org_id)

    if status:
        invoices = [i for i in invoices if i.status.value == status.lower()]

    return invoices


@router.post("/invoices/generate", response_model=InvoiceOut)
@require_roles(["admin"])
async def generate_invoice_manually(
    request: Request,
    organization_id: str,
    start_time: datetime,
    end_time: datetime,
    container: ServiceContainer = Depends(get_container)
):
    """Manually trigger invoice generation. (Admin only)"""
    # Generate timezone aware dates if needed
    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=timezone.utc)
    if end_time.tzinfo is None:
        end_time = end_time.replace(tzinfo=timezone.utc)

    org_id = request.state.organization_id
    invoice = await container.invoice_service.generate_invoice(org_id, start_time, end_time)
    return invoice


@router.get("/pricing", response_model=List[PricingRuleOut])
async def get_pricing(container: ServiceContainer = Depends(get_container)):
    """List all active pricing rules."""
    rules = await container.pricing_service.get_all_rules()
    return rules
