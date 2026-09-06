"""SQLAlchemy production ORM models for Decision Governance entities."""

from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Float, Boolean, Integer, DateTime, JSON, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class DecisionRecordORM(Base):
    __tablename__ = "decision_records"

    decision_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(64), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    decision_type = Column(String(64), nullable=False)
    status = Column(String(64), nullable=False)
    priority = Column(String(64), nullable=False)
    outcome = Column(String(64), nullable=True)
    confidence = Column(Float, default=0.0)
    risk_score = Column(Float, default=0.0)
    fingerprint = Column(String(128), nullable=True)
    is_immutable = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    finalized_at = Column(DateTime(timezone=True), nullable=True)
    context_data = Column(JSON, nullable=True)
    factors_data = Column(JSON, nullable=True)
    metadata_json = Column(JSON, nullable=True)


class DecisionPlanORM(Base):
    __tablename__ = "decision_plans"

    plan_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    decision_id = Column(String(64), nullable=False, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    status = Column(String(64), nullable=False)
    priority = Column(String(64), nullable=False)
    overall_risk = Column(String(64), nullable=False)
    strategy = Column(String(64), nullable=False)
    steps_json = Column(JSON, nullable=True)
    feasibility_score = Column(Float, default=1.0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class DecisionRecommendationORM(Base):
    __tablename__ = "decision_recommendations"

    recommendation_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    decision_id = Column(String(64), nullable=False, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    recommendation_type = Column(String(64), nullable=False)
    priority = Column(String(64), nullable=False)
    confidence = Column(String(64), nullable=False)
    confidence_score = Column(Float, default=0.85)
    expected_impact_score = Column(Float, default=0.80)
    status = Column(String(64), nullable=False)
    rationale = Column(Text, nullable=True)
    tradeoffs_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class DecisionEvidenceBundleORM(Base):
    __tablename__ = "decision_evidence_bundles"

    bundle_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    decision_id = Column(String(64), nullable=False, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    bundle_fingerprint = Column(String(128), nullable=True)
    is_immutable = Column(Boolean, default=False)
    items_json = Column(JSON, nullable=True)
    finalized_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
