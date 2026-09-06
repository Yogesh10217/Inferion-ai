"""SQLAlchemy production ORM models for Identity Assurance entities."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, Integer, DateTime, JSON, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class IdentityORM(Base):
    __tablename__ = "identity_references"

    identity_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(64), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    identity_type = Column(String(64), nullable=False)
    category = Column(String(64), nullable=False)
    status = Column(String(64), nullable=False)
    external_id = Column(String(255), nullable=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class IdentityProfileORM(Base):
    __tablename__ = "identity_profiles"

    profile_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(64), nullable=False, index=True)
    identity_id = Column(String(64), nullable=False, index=True)
    purpose = Column(String(255), nullable=False)
    criticality = Column(String(64), nullable=False)
    trust_posture = Column(Float, default=0.85)
    attributes_json = Column(JSON, nullable=True)
    assessed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class IdentityTrustORM(Base):
    __tablename__ = "identity_trust_scores"

    score_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(64), nullable=False, index=True)
    identity_id = Column(String(64), nullable=False, index=True)
    overall_trust_score = Column(Float, nullable=False)
    is_trusted = Column(Boolean, default=True)
    risk_level = Column(String(64), nullable=False)
    factors_json = Column(JSON, nullable=True)
    calculated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class IdentityPrivilegeORM(Base):
    __tablename__ = "identity_privileges"

    privilege_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(64), nullable=False, index=True)
    identity_id = Column(String(64), nullable=False, index=True)
    risk_score = Column(Float, default=0.1)
    is_excessive = Column(Boolean, default=False)
    is_concentrated = Column(Boolean, default=False)
    privileges_json = Column(JSON, nullable=True)
    evaluated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class IdentityAnomalyORM(Base):
    __tablename__ = "identity_anomalies"

    anomaly_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(64), nullable=False, index=True)
    identity_id = Column(String(64), nullable=False, index=True)
    anomaly_type = Column(String(64), nullable=False)
    severity = Column(String(64), nullable=False)
    status = Column(String(64), nullable=False)
    evidence_json = Column(JSON, nullable=True)
    detected_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class AccessReviewORM(Base):
    __tablename__ = "identity_access_reviews"

    review_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(64), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    review_type = Column(String(64), nullable=False)
    status = Column(String(64), nullable=False)
    findings_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class IdentityInvestigationORM(Base):
    __tablename__ = "identity_investigations"

    investigation_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(64), nullable=False, index=True)
    identity_id = Column(String(64), nullable=False, index=True)
    status = Column(String(64), nullable=False)
    snapshot_id = Column(String(64), nullable=True)
    findings_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class IdentityEvidenceORM(Base):
    __tablename__ = "identity_evidence_bundles"

    bundle_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(64), nullable=False, index=True)
    identity_id = Column(String(64), nullable=False, index=True)
    sha256_checksum = Column(String(128), nullable=False)
    is_finalized = Column(Boolean, default=True)
    evidence_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class IdentityLearningORM(Base):
    __tablename__ = "identity_learning_records"

    record_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(64), nullable=False, index=True)
    patterns_json = Column(JSON, nullable=True)
    recommendations_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
