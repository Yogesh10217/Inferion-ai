"""SQLAlchemy ORM models for Runtime Intelligence (Phase 5.54)."""

from sqlalchemy import Column, String, Float, Boolean, DateTime, JSON, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone

Base = declarative_base()


class ORMRuntimeSignal(Base):
    __tablename__ = "ai_runtime_signals"

    signal_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    signal_type = Column(String(64), nullable=False)
    severity = Column(String(32), nullable=False)
    payload = Column(JSON, nullable=False)
    source_domain = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ORMRuntimeHealthAssessment(Base):
    __tablename__ = "ai_runtime_health_assessments"

    assessment_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    overall_status = Column(String(32), nullable=False)
    overall_score = Column(Float, nullable=False)
    dimensions = Column(JSON, nullable=False)
    evaluated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ORMRuntimeEvidenceBundle(Base):
    __tablename__ = "ai_runtime_evidence_bundles"

    evidence_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    assessment_id = Column(String(64), nullable=False)
    integrity_hash = Column(String(64), nullable=False)
    is_sealed = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
