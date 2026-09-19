"""SQLAlchemy ORM models for Reliability Intelligence (Phase 5.55)."""

from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, Index, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ServiceHealthORM(Base):
    __tablename__ = "reliability_service_health"

    assessment_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    service_id = Column(String(128), nullable=False, index=True)
    status = Column(String(32), nullable=False)
    overall_score = Column(Float, nullable=False)
    dimensions = Column(JSON, nullable=False)
    evaluated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (Index("idx_rel_health_tenant_service", "tenant_id", "service_id"),)


class ReliabilityAssessmentORM(Base):
    __tablename__ = "reliability_assessments"

    assessment_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    overall_score = Column(Float, nullable=False)
    state = Column(String(32), nullable=False)
    findings = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class FailurePredictionORM(Base):
    __tablename__ = "reliability_failure_predictions"

    prediction_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    service_id = Column(String(128), nullable=False, index=True)
    predicted_failure_type = Column(String(64), nullable=False)
    probability = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    explanation = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ServiceLevelObjectiveORM(Base):
    __tablename__ = "reliability_slos"

    slo_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    service_id = Column(String(128), nullable=False, index=True)
    indicator_type = Column(String(64), nullable=False)
    target_percentage = Column(Float, nullable=False)
    current_percentage = Column(Float, nullable=False)
    is_breached = Column(Boolean, nullable=False, default=False)


class ReliabilityEvidenceORM(Base):
    __tablename__ = "reliability_evidence"

    evidence_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    assessment_id = Column(String(64), nullable=False)
    integrity_hash = Column(String(128), nullable=False)
    is_sealed = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
