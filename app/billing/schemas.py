from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from app.billing.models import InvoiceStatus

class CostBreakdown(BaseModel):
    input_cost: float = 0.0
    output_cost: float = 0.0
    subtotal: float = 0.0
    discount: float = 0.0
    tax: float = 0.0
    total: float = 0.0
    currency: str = "USD"

class InvoiceLineItemOut(BaseModel):
    id: str
    provider: str
    model: str
    requests: int
    tokens: int
    cost: float

class InvoiceOut(BaseModel):
    id: str
    organization_id: str
    billing_period_start: datetime
    billing_period_end: datetime
    subtotal: float
    tax: float
    discount: float
    total: float
    currency: str
    status: InvoiceStatus
    generated_at: datetime
    items: List[InvoiceLineItemOut] = []

class BudgetOut(BaseModel):
    id: str
    organization_id: str
    workspace_id: Optional[str]
    hard_limit: float
    critical_threshold: float
    warning_threshold: float
    enabled: bool

class BudgetAlertOut(BaseModel):
    id: str
    triggered_at: datetime
    threshold: str
    current_usage: float

class BudgetCreate(BaseModel):
    organization_id: str
    workspace_id: Optional[str] = None
    hard_limit: float = 0.0
    critical_threshold: float = 0.0
    warning_threshold: float = 0.0
    enabled: bool = True

class BudgetUpdate(BaseModel):
    hard_limit: Optional[float] = None
    critical_threshold: Optional[float] = None
    warning_threshold: Optional[float] = None
    enabled: Optional[bool] = None

class SubscriptionPlanOut(BaseModel):
    id: str
    name: str
    description: Optional[str]
    monthly_price: float
    max_users: Optional[int]
    max_workspaces: Optional[int]
    priority_support: bool

class PricingRuleOut(BaseModel):
    id: str
    provider: str
    model: str
    input_cost_per_1k_tokens: float
    output_cost_per_1k_tokens: float
    currency: str
    effective_from: datetime
