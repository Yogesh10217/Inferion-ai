"""SQLAlchemy Production Models for Operations Intelligence (Phase 5.41)."""

from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ServiceModel(Base):
    __tablename__ = "operations_services"

    service_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    owner_team = Column(String(255), nullable=False)
    criticality = Column(String(64), nullable=False, default="BUSINESS_CRITICAL")
    tier = Column(String(64), nullable=False, default="TIER_1")
    health_status = Column(String(64), nullable=False, default="HEALTHY")
    dependencies = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class IncidentModel(Base):
    __tablename__ = "operations_incidents"

    incident_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    affected_service_id = Column(String(64), nullable=False)
    severity = Column(String(64), nullable=False, default="P2_HIGH")
    priority = Column(String(64), nullable=False, default="P2")
    status = Column(String(64), nullable=False, default="DETECTED")
    external_itsm_ref = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)


class MajorIncidentModel(Base):
    __tablename__ = "operations_major_incidents"

    major_incident_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    incident_id = Column(String(64), nullable=False)
    title = Column(String(255), nullable=False)
    impact = Column(String(64), nullable=False)
    status = Column(String(64), nullable=False, default="DECLARED")
    requires_human_oversight = Column(Boolean, default=True)
    approval_id = Column(String(64), nullable=True)
    declared_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime(timezone=True), nullable=True)


class AlertModel(Base):
    __tablename__ = "operations_alerts"

    alert_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    source_system = Column(String(128), nullable=False)
    service_id = Column(String(64), nullable=False)
    alert_name = Column(String(255), nullable=False)
    fingerprint = Column(String(128), nullable=False, index=True)
    severity = Column(String(64), nullable=False, default="HIGH")
    status = Column(String(64), nullable=False, default="ACTIVE")
    duplicate_count = Column(Integer, default=1)
    ingested_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ProblemModel(Base):
    __tablename__ = "operations_problems"

    problem_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    associated_incident_ids = Column(JSON, nullable=True)
    status = Column(String(64), nullable=False, default="OPEN")
    workaround_details = Column(Text, nullable=True)
    root_cause_analysis_id = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime(timezone=True), nullable=True)


class KnownErrorModel(Base):
    __tablename__ = "operations_known_errors"

    known_error_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    problem_id = Column(String(64), nullable=True)
    workaround = Column(Text, nullable=False)
    remediation_reference = Column(String(255), nullable=True)
    status = Column(String(64), nullable=False, default="PUBLISHED")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class InvestigationModel(Base):
    __tablename__ = "operations_investigations"

    investigation_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    target_incident_id = Column(String(64), nullable=False)
    status = Column(String(64), nullable=False, default="OPEN")
    findings = Column(JSON, nullable=True)
    root_cause_analysis_id = Column(String(64), nullable=True)
    is_concluded = Column(Boolean, default=False)
    snapshot_id = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    concluded_at = Column(DateTime(timezone=True), nullable=True)


class RemediationPlanModel(Base):
    __tablename__ = "operations_remediation_plans"

    plan_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    incident_id = Column(String(64), nullable=False)
    idempotency_key = Column(String(128), nullable=False)
    status = Column(String(64), nullable=False, default="PLANNED")
    priority = Column(String(64), nullable=False, default="P2")
    actions = Column(JSON, nullable=False)
    requires_approval = Column(Boolean, default=False)
    approval_id = Column(String(64), nullable=True)
    delegation_request_id = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class RootCauseModel(Base):
    __tablename__ = "operations_root_cause_analyses"

    analysis_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    incident_id = Column(String(64), nullable=False)
    primary_root_cause = Column(Text, nullable=False)
    confidence = Column(String(64), nullable=False, default="HIGH")
    hypotheses = Column(JSON, nullable=True)
    evidence = Column(JSON, nullable=True)
    analyzed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class EvidenceBundleModel(Base):
    __tablename__ = "operations_evidence_bundles"

    bundle_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    items = Column(JSON, nullable=False)
    sha256_hash = Column(String(64), nullable=True)
    is_finalized = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class LearningRecordModel(Base):
    __tablename__ = "operations_learning_records"

    record_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    pattern_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    recommendations = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
