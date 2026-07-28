from datetime import datetime, timezone
import uuid
from typing import Optional

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Float, Enum as SQLAlchemyEnum
from sqlalchemy.orm import mapped_column, Mapped, relationship
import enum

from app.core.database import Base


def _now():
    return datetime.now(timezone.utc)


class InvoiceStatus(str, enum.Enum):
    DRAFT = "draft"
    GENERATED = "generated"
    SENT = "sent"
    PAID = "paid"
    ARCHIVED = "archived"


class SubscriptionPlan(Base):
    """Available subscription tiers."""
    __tablename__ = "subscription_plans"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    monthly_price: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Instead of direct limits, we link to a template quota policy that gets cloned for the tenant
    quota_policy_template_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    max_users: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_workspaces: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    priority_support: Mapped[bool] = mapped_column(Boolean, default=False)
    
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class OrganizationSubscription(Base):
    """Maps an organization to its active subscription."""
    __tablename__ = "organization_subscriptions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(String, index=True, nullable=False, unique=True)
    plan_id: Mapped[str] = mapped_column(ForeignKey("subscription_plans.id"), nullable=False)
    
    status: Mapped[str] = mapped_column(String, default="active")
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    renewal_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    plan: Mapped[SubscriptionPlan] = relationship(lazy="joined")


class PricingRule(Base):
    """Cost mapping for providers/models per 1000 tokens."""
    __tablename__ = "pricing_rules"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    provider: Mapped[str] = mapped_column(String, index=True, nullable=False)
    model: Mapped[str] = mapped_column(String, index=True, nullable=False)
    
    input_cost_per_1k_tokens: Mapped[float] = mapped_column(Float, default=0.0)
    output_cost_per_1k_tokens: Mapped[float] = mapped_column(Float, default=0.0)
    currency: Mapped[str] = mapped_column(String, default="USD")
    
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class Invoice(Base):
    """Monthly billing record."""
    __tablename__ = "invoices"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"INV-{uuid.uuid4().hex[:8]}")
    organization_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    
    billing_period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    billing_period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    subtotal: Mapped[float] = mapped_column(Float, default=0.0)
    tax: Mapped[float] = mapped_column(Float, default=0.0)
    discount: Mapped[float] = mapped_column(Float, default=0.0)
    total: Mapped[float] = mapped_column(Float, default=0.0)
    currency: Mapped[str] = mapped_column(String, default="USD")
    
    status: Mapped[InvoiceStatus] = mapped_column(SQLAlchemyEnum(InvoiceStatus), default=InvoiceStatus.DRAFT)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class InvoiceLineItem(Base):
    """Detailed breakdowns on an invoice."""
    __tablename__ = "invoice_line_items"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    invoice_id: Mapped[str] = mapped_column(ForeignKey("invoices.id"), index=True, nullable=False)
    
    provider: Mapped[str] = mapped_column(String, nullable=False)
    model: Mapped[str] = mapped_column(String, nullable=False)
    
    requests: Mapped[int] = mapped_column(Integer, default=0)
    tokens: Mapped[int] = mapped_column(Integer, default=0)
    cost: Mapped[float] = mapped_column(Float, default=0.0)


class Budget(Base):
    """Spending limits at org or workspace level."""
    __tablename__ = "budgets"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    workspace_id: Mapped[Optional[str]] = mapped_column(String, index=True, nullable=True)
    
    # 0 implies no limit
    hard_limit: Mapped[float] = mapped_column(Float, default=0.0)
    critical_threshold: Mapped[float] = mapped_column(Float, default=0.0)
    warning_threshold: Mapped[float] = mapped_column(Float, default=0.0)
    
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class BudgetAlert(Base):
    """History of budget alerts triggered."""
    __tablename__ = "budget_alerts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    budget_id: Mapped[str] = mapped_column(ForeignKey("budgets.id"), index=True, nullable=False)
    triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    threshold: Mapped[str] = mapped_column(String, nullable=False)  # 'warning', 'critical', 'hard'
    current_usage: Mapped[float] = mapped_column(Float, nullable=False)


class PaymentHistory(Base):
    """Provider-agnostic payment tracking."""
    __tablename__ = "payment_history"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    invoice_id: Mapped[str] = mapped_column(ForeignKey("invoices.id"), index=True, nullable=False)
    
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    provider_reference: Mapped[str] = mapped_column(String, nullable=False)
    paid_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
