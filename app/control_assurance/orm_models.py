"""SQLAlchemy Production ORM Models for Control Assurance Subsystem (Phase 5.38)."""

from datetime import datetime, timezone
from typing import Any, Dict

from sqlalchemy import (
    Column,
    String,
    Boolean,
    Float,
    Integer,
    DateTime,
    JSON,
    Text,
    Enum as SQLEnum,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ControlModel(Base):
    __tablename__ = "control_assurance_controls"

    control_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    code = Column(String(128), nullable=False, index=True)
    name = Column(String(256), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(64), nullable=False, index=True)
    control_type = Column(String(64), nullable=False)
    criticality = Column(String(64), nullable=False)
    status = Column(String(64), nullable=False, default="ACTIVE")
    definition_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ControlFrameworkModel(Base):
    __tablename__ = "control_assurance_frameworks"

    framework_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    code = Column(String(128), nullable=False)
    name = Column(String(256), nullable=False)
    framework_type = Column(String(64), nullable=False)
    is_active = Column(Boolean, default=True)
    requirements_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ControlEvaluationModel(Base):
    __tablename__ = "control_assurance_evaluations"

    evaluation_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    control_id = Column(String(64), nullable=False, index=True)
    scope_target_id = Column(String(128), nullable=False)
    status = Column(String(64), nullable=False, index=True)
    score = Column(Float, default=100.0)
    result_json = Column(JSON, nullable=True)
    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True), nullable=True)


class ControlViolationModel(Base):
    __tablename__ = "control_assurance_violations"

    violation_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    control_id = Column(String(64), nullable=False, index=True)
    severity = Column(String(64), nullable=False, index=True)
    status = Column(String(64), nullable=False, index=True)
    finding_code = Column(String(128), nullable=False)
    finding_message = Column(Text, nullable=False)
    impact_score = Column(Float, default=0.0)
    is_closed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ControlEvidenceModel(Base):
    __tablename__ = "control_assurance_evidence"

    evidence_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    evidence_type = Column(String(64), nullable=False)
    source_reference = Column(String(256), nullable=False)
    checksum_sha256 = Column(String(64), nullable=False)
    sanitized_payload = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ControlExceptionModel(Base):
    __tablename__ = "control_assurance_exceptions"

    exception_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    control_id = Column(String(64), nullable=False, index=True)
    status = Column(String(64), nullable=False, index=True)
    is_critical_control = Column(Boolean, default=False)
    business_reason = Column(Text, nullable=False)
    approver_id = Column(String(64), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ControlRemediationPlanModel(Base):
    __tablename__ = "control_assurance_remediation_plans"

    plan_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    violation_id = Column(String(64), nullable=False, index=True)
    control_id = Column(String(64), nullable=False, index=True)
    priority = Column(String(64), nullable=False)
    status = Column(String(64), nullable=False)
    delegation_id = Column(String(64), nullable=True)
    actions_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ControlVerificationModel(Base):
    __tablename__ = "control_assurance_verifications"

    verification_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    remediation_plan_id = Column(String(64), nullable=False, index=True)
    control_id = Column(String(64), nullable=False, index=True)
    result = Column(String(64), nullable=False)
    checks_json = Column(JSON, nullable=True)
    verified_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ControlAttestationModel(Base):
    __tablename__ = "control_assurance_attestations"

    attestation_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    control_id = Column(String(64), nullable=False, index=True)
    status = Column(String(64), nullable=False, index=True)
    attestor_id = Column(String(64), nullable=True)
    fingerprint_sha256 = Column(String(64), nullable=False)
    is_finalized = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ControlAssuranceSnapshotModel(Base):
    __tablename__ = "control_assurance_snapshots"

    snapshot_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    control_id = Column(String(64), nullable=False, index=True)
    fingerprint_sha256 = Column(String(64), nullable=False)
    platform_snapshot_id = Column(String(64), nullable=False)
    state_payload = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ControlLearningModel(Base):
    __tablename__ = "control_assurance_learnings"

    record_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    control_id = Column(String(64), nullable=False, index=True)
    patterns_json = Column(JSON, nullable=True)
    recommendations_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
