"""SQLAlchemy ORM Models for Decision Intelligence Platform (Phase 5.29)."""

from datetime import datetime, timezone
import uuid
from typing import Optional, Dict, Any

from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Integer, Float, Boolean, Text
from sqlalchemy.orm import mapped_column, Mapped

from app.core.database import Base


def _now():
    return datetime.now(timezone.utc)


class DecisionContextModel(Base):
    __tablename__ = "dec_contexts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"ctx_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    context_type: Mapped[str] = mapped_column(String, default="CROSS_DOMAIN")
    scope: Mapped[str] = mapped_column(String, default="ENTERPRISE")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class DecisionEvidenceModel(Base):
    __tablename__ = "dec_evidence"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"evcol_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    context_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    quality_score: Mapped[float] = mapped_column(Float, default=90.0)


class DecisionScenarioModel(Base):
    __tablename__ = "dec_scenarios"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"scen_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    context_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    scenario_type: Mapped[str] = mapped_column(String, default="BASELINE")
    title: Mapped[str] = mapped_column(String, nullable=False)


class DecisionAlternativeModel(Base):
    __tablename__ = "dec_alternatives"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"alt_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    context_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default="PROPOSED")


class DecisionRecommendationModel(Base):
    __tablename__ = "dec_recommendations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"rec_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    context_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    recommendation_type: Mapped[str] = mapped_column(String, default="PROCEED")
    confidence: Mapped[str] = mapped_column(String, default="HIGH")


class DecisionRecordModel(Base):
    __tablename__ = "dec_records"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"dec_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default="DRAFT")
    is_finalized: Mapped[bool] = mapped_column(Boolean, default=False)
    decision_fingerprint: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class DecisionOutcomeModel(Base):
    __tablename__ = "dec_outcomes"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"out_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    decision_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String, default="ACHIEVED")


class DecisionTrustScoreModel(Base):
    __tablename__ = "dec_trust_scores"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"dectrust_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    context_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    overall_score: Mapped[float] = mapped_column(Float, default=90.0)


class DecisionDelegationModel(Base):
    __tablename__ = "dec_delegations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"del_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    decision_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    target: Mapped[str] = mapped_column(String, default="PORTFOLIO_PLATFORM")
