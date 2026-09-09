"""SQLAlchemy ORM models for Continuous Assurance (Phase 5.54)."""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, DateTime, JSON, Text, Index
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class RuntimeObservationORM(Base):
    __tablename__ = "continuous_assurance_observations"

    observation_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    source_domain = Column(String(64), nullable=False)
    observation_type = Column(String(64), nullable=False)
    severity = Column(String(32), nullable=False)
    status = Column(String(32), nullable=False, default="UNPROCESSED")
    payload = Column(JSON, nullable=False)
    observed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_ca_obs_tenant_domain", "tenant_id", "source_domain"),
    )


class ContinuousAssuranceAssessmentORM(Base):
    __tablename__ = "continuous_assurance_assessments"

    assessment_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    overall_score = Column(Float, nullable=False)
    state = Column(String(32), nullable=False)
    findings = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_ca_ass_tenant_created", "tenant_id", "created_at"),
    )


class AssuranceDriftORM(Base):
    __tablename__ = "continuous_assurance_drift"

    drift_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    drift_type = Column(String(64), nullable=False)
    severity = Column(String(32), nullable=False)
    status = Column(String(32), nullable=False, default="DETECTED")
    difference_summary = Column(Text, nullable=False)
    expected_state = Column(JSON, nullable=False)
    observed_state = Column(JSON, nullable=False)
    confidence = Column(Float, nullable=False, default=0.95)
    detected_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_ca_drift_tenant_status", "tenant_id", "status"),
    )


class ContinuousVerificationORM(Base):
    __tablename__ = "continuous_assurance_verifications"

    verification_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    target_resource_id = Column(String(128), nullable=False)
    status = Column(String(32), nullable=False)
    expected_hash = Column(String(128), nullable=False)
    observed_hash = Column(String(128), nullable=False)
    verification_details = Column(JSON, nullable=False)
    verified_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ContinuousAssuranceEvidenceORM(Base):
    __tablename__ = "continuous_assurance_evidence"

    evidence_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    assessment_id = Column(String(64), nullable=False)
    integrity_hash = Column(String(128), nullable=False)
    is_sealed = Column(Boolean, nullable=False, default=True)
    observation_ids = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
