"""SQLAlchemy Production ORM Models for Access Intelligence Subsystem (Phase 5.39)."""

from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    String,
    Text,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class AccessIdentityModel(Base):
    __tablename__ = "access_intelligence_identities"

    identity_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    name = Column(String(256), nullable=False)
    identity_type = Column(String(64), nullable=False, index=True)
    status = Column(String(64), nullable=False, default="ACTIVE")
    risk_level = Column(String(64), nullable=False, default="LOW")
    reference_json = Column(JSON, nullable=True)
    tags_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class EntitlementModel(Base):
    __tablename__ = "access_intelligence_entitlements"

    entitlement_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    code = Column(String(128), nullable=False, index=True)
    name = Column(String(256), nullable=False)
    entitlement_type = Column(String(64), nullable=False)
    scope = Column(String(64), nullable=False, default="TENANT")
    criticality = Column(String(64), nullable=False, default="MEDIUM")
    status = Column(String(64), nullable=False, default="ACTIVE")
    is_privileged = Column(Boolean, default=False)
    reference_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class AccessRelationshipModel(Base):
    __tablename__ = "access_intelligence_relationships"

    relationship_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    source_identity_id = Column(String(64), nullable=False, index=True)
    target_resource_id = Column(String(64), nullable=False, index=True)
    relationship_type = Column(String(64), nullable=False)
    strength = Column(String(64), nullable=False, default="DIRECT")
    status = Column(String(64), nullable=False, default="ACTIVE")
    entitlement_id = Column(String(64), nullable=True)
    is_active = Column(Boolean, default=True)
    assigned_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), nullable=True)


class PrivilegedAccessRequestModel(Base):
    __tablename__ = "access_intelligence_privileged_requests"

    request_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    requester_identity_id = Column(String(64), nullable=False)
    target_role_or_entitlement = Column(String(128), nullable=False)
    scope = Column(String(64), nullable=False)
    justification = Column(Text, nullable=False)
    status = Column(String(64), nullable=False, default="PENDING_APPROVAL")
    requires_approval = Column(Boolean, default=True)
    approval_id = Column(String(64), nullable=True)
    requested_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    activated_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)


class EmergencyAccessRequestModel(Base):
    __tablename__ = "access_intelligence_emergency_requests"

    request_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    requester_identity_id = Column(String(64), nullable=False)
    reason = Column(String(64), nullable=False)
    justification = Column(Text, nullable=False)
    status = Column(String(64), nullable=False, default="REQUESTED")
    audit_fingerprint = Column(String(128), nullable=False)
    requested_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    activated_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)


class AccessReviewModel(Base):
    __tablename__ = "access_intelligence_reviews"

    review_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    title = Column(String(256), nullable=False)
    reviewer_identity_id = Column(String(64), nullable=False)
    target_identity_id = Column(String(64), nullable=False)
    target_entitlement_id = Column(String(64), nullable=False)
    scope = Column(String(64), nullable=False, default="IDENTITY")
    status = Column(String(64), nullable=False, default="DRAFT")
    decision = Column(String(64), nullable=True)
    is_finalized = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    finalized_at = Column(DateTime(timezone=True), nullable=True)


class AccessCertificationModel(Base):
    __tablename__ = "access_intelligence_certifications"

    certification_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    name = Column(String(256), nullable=False)
    certifier_identity_id = Column(String(64), nullable=False)
    scope = Column(String(64), nullable=False, default="ENTERPRISE")
    status = Column(String(64), nullable=False, default="DRAFT")
    decision = Column(String(64), nullable=True)
    fingerprint = Column(String(128), nullable=True)
    is_finalized = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    finalized_at = Column(DateTime(timezone=True), nullable=True)


class AccessAnomalyModel(Base):
    __tablename__ = "access_intelligence_anomalies"

    anomaly_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    subject_identity_id = Column(String(64), nullable=False)
    anomaly_type = Column(String(64), nullable=False)
    severity = Column(String(64), nullable=False, default="HIGH")
    confidence = Column(String(64), nullable=False, default="HIGH")
    title = Column(String(256), nullable=False)
    evidence_json = Column(JSON, nullable=True)
    detected_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    is_resolved = Column(Boolean, default=False)


class AccessInvestigationModel(Base):
    __tablename__ = "access_intelligence_investigations"

    investigation_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    title = Column(String(256), nullable=False)
    target_identity_id = Column(String(64), nullable=False)
    status = Column(String(64), nullable=False, default="OPEN")
    remediation_plan_id = Column(String(64), nullable=True)
    is_concluded = Column(Boolean, default=False)
    snapshot_id = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    concluded_at = Column(DateTime(timezone=True), nullable=True)


class AccessRemediationPlanModel(Base):
    __tablename__ = "access_intelligence_remediation_plans"

    plan_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    target_identity_id = Column(String(64), nullable=False)
    action = Column(String(64), nullable=False)
    target_entitlement_id = Column(String(64), nullable=False)
    priority = Column(String(64), nullable=False, default="HIGH")
    status = Column(String(64), nullable=False, default="PLANNED")
    requires_approval = Column(Boolean, default=False)
    approval_id = Column(String(64), nullable=True)
    delegation_request_id = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class AccessEvidenceBundleModel(Base):
    __tablename__ = "access_intelligence_evidence_bundles"

    bundle_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    title = Column(String(256), nullable=False)
    sha256_hash = Column(String(128), nullable=True)
    is_finalized = Column(Boolean, default=False)
    items_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    finalized_at = Column(DateTime(timezone=True), nullable=True)


class AccessLearningModel(Base):
    __tablename__ = "access_intelligence_learning_records"

    record_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    identity_id = Column(String(64), nullable=False)
    patterns_json = Column(JSON, nullable=True)
    recommendations_json = Column(JSON, nullable=True)
    recorded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
