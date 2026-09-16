"""SQLAlchemy ORM Models for Portfolio Platform (Phase 5.28)."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def _now():
    return datetime.now(timezone.utc)


class StrategyModel(Base):
    __tablename__ = "port_strategies"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"strat_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    horizon: Mapped[str] = mapped_column(String, default="NEAR_TERM")
    status: Mapped[str] = mapped_column(String, default="ACTIVE")
    version: Mapped[str] = mapped_column(String, default="1.0.0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class BusinessObjectiveModel(Base):
    __tablename__ = "port_objectives"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"obj_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    strategy_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    theme: Mapped[str] = mapped_column(String, default="PRODUCT_INNOVATION")


class AIOpportunityModel(Base):
    __tablename__ = "port_opportunities"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"opp_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    source: Mapped[str] = mapped_column(String, default="MANUAL_DISCOVERY")
    status: Mapped[str] = mapped_column(String, default="DISCOVERED")


class AIInitiativeModel(Base):
    __tablename__ = "port_initiatives"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"init_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    initiative_type: Mapped[str] = mapped_column(String, default="APPLICATION")
    status: Mapped[str] = mapped_column(String, default="PROPOSED")
    priority: Mapped[str] = mapped_column(String, default="HIGH")


class BusinessCaseModel(Base):
    __tablename__ = "port_business_cases"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"bc_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    initiative_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    problem_statement: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String, default="SUBMITTED")


class InvestmentModel(Base):
    __tablename__ = "port_investments"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"inv_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    initiative_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    amount_usd: Mapped[float] = mapped_column(Float, default=50000.0)
    risk_level: Mapped[str] = mapped_column(String, default="HIGH")
    status: Mapped[str] = mapped_column(String, default="DRAFT")


class FundingModel(Base):
    __tablename__ = "port_funding"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"fund_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    initiative_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    allocated_amount_usd: Mapped[float] = mapped_column(Float, default=50000.0)
    status: Mapped[str] = mapped_column(String, default="ALLOCATED")


class ValueMeasurementModel(Base):
    __tablename__ = "port_value_measurements"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"val_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    initiative_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    dimension: Mapped[str] = mapped_column(String, nullable=False)
    stage: Mapped[str] = mapped_column(String, default="EXPECTED_VALUE")


class BenefitModel(Base):
    __tablename__ = "port_benefits"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"ben_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    initiative_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default="PLANNED")


class PortfolioSnapshotModel(Base):
    __tablename__ = "port_snapshots"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"snap_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    snapshot_fingerprint: Mapped[str] = mapped_column(String, nullable=False)


class PortfolioDecisionModel(Base):
    __tablename__ = "port_decisions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"portdec_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    decision_fingerprint: Mapped[str] = mapped_column(String, nullable=False)
