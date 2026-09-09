"""SQLAlchemy ORM models for Capacity Intelligence (Phase 5.56)."""

from sqlalchemy import Column, String, Float, Boolean, DateTime, JSON, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone

Base = declarative_base()


class ORMResourceProfile(Base):
    __tablename__ = "ai_capacity_resource_profiles"

    profile_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    resource_id = Column(String(64), nullable=False)
    resource_type = Column(String(64), nullable=False)
    total_capacity = Column(Float, nullable=False)
    unit = Column(String(32), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ORMCapacityAssessment(Base):
    __tablename__ = "ai_capacity_assessments"

    assessment_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    resource_id = Column(String(64), nullable=False)
    status = Column(String(32), nullable=False)
    consumed_percentage = Column(Float, nullable=False)
    headroom_percentage = Column(Float, nullable=False)
    saturation_risk_score = Column(Float, nullable=False)
    evaluated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ORMCapacityEvidenceBundle(Base):
    __tablename__ = "ai_capacity_evidence_bundles"

    evidence_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    assessment_id = Column(String(64), nullable=False)
    integrity_hash = Column(String(64), nullable=False)
    is_sealed = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
