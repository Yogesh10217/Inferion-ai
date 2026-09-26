"""SQLAlchemy Persistence Models for FinOps Platform."""

from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, Numeric, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def _now() -> datetime:
    return datetime.now(timezone.utc)


class CostLedgerEntryModel(Base):
    __tablename__ = "finops_cost_ledger_entries"

    id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    organization_id = Column(String(64), nullable=True)
    workspace_id = Column(String(64), nullable=True)
    project_id = Column(String(64), nullable=True)

    component = Column(String(64), nullable=False)
    provider = Column(String(64), default="internal")
    model_id = Column(String(128), nullable=True)
    cost_category = Column(String(64), nullable=False)

    quantity = Column(Numeric(18, 6), nullable=False)
    unit = Column(String(32), default="units")
    unit_price = Column(Numeric(18, 6), nullable=False)
    total_cost = Column(Numeric(18, 6), nullable=False)
    currency = Column(String(8), default="USD")

    extra_metadata = Column("metadata", JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=_now, index=True)


class CostAdjustmentModel(Base):
    __tablename__ = "finops_cost_adjustments"

    id = Column(String(64), primary_key=True)
    original_cost_id = Column(String(64), nullable=False, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    adjustment_amount = Column(Numeric(18, 6), nullable=False)
    reason = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_now)


class BudgetModel(Base):
    __tablename__ = "finops_budgets"

    id = Column(String(64), primary_key=True)
    name = Column(String(128), nullable=False)
    tenant_id = Column(String(64), nullable=False, index=True)
    scope = Column(String(64), default="TENANT")
    period = Column(String(32), default="MONTHLY")

    limit_amount = Column(Numeric(18, 6), nullable=False)
    current_usage = Column(Numeric(18, 6), default=0)
    enforcement_action = Column(String(64), default="WARN")
    status = Column(String(32), default="HEALTHY")

    created_at = Column(DateTime(timezone=True), default=_now)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)
