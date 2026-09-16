"""SQLAlchemy production ORM models for Knowledge Assurance entities."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class KnowledgeReferenceORM(Base):
    __tablename__ = "knowledge_references"

    reference_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(64), nullable=False, index=True)
    external_key = Column(String(255), nullable=False)
    resource_type = Column(String(64), nullable=False)
    status = Column(String(64), nullable=False)
    classification = Column(String(64), nullable=False)
    sha256_checksum = Column(String(128), nullable=True)
    is_immutable = Column(Boolean, default=False)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class KnowledgeSourceORM(Base):
    __tablename__ = "knowledge_sources"

    source_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(64), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    source_type = Column(String(64), nullable=False)
    status = Column(String(64), nullable=False)
    authority = Column(String(64), nullable=False)
    reliability_score = Column(Float, default=0.9)
    authority_score = Column(Float, default=0.9)
    freshness_score = Column(Float, default=1.0)
    trust_score = Column(Float, default=0.9)
    last_verified_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class KnowledgeContextORM(Base):
    __tablename__ = "knowledge_contexts"

    context_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(64), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    context_type = Column(String(64), nullable=False)
    scope = Column(String(64), nullable=False)
    priority = Column(String(64), nullable=False)
    status = Column(String(64), nullable=False)
    sha256_fingerprint = Column(String(128), nullable=True)
    is_finalized = Column(Boolean, default=False)
    payload_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class KnowledgeProvenanceORM(Base):
    __tablename__ = "knowledge_provenance"

    provenance_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(64), nullable=False, index=True)
    target_resource_id = Column(String(64), nullable=False, index=True)
    status = Column(String(64), nullable=False)
    sha256_fingerprint = Column(String(128), nullable=True)
    chain_json = Column(JSON, nullable=True)
    evidence_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class KnowledgeConflictORM(Base):
    __tablename__ = "knowledge_conflicts"

    conflict_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(64), nullable=False, index=True)
    conflict_type = Column(String(64), nullable=False)
    severity = Column(String(64), nullable=False)
    status = Column(String(64), nullable=False)
    target_resource_id = Column(String(64), nullable=False)
    requires_approval = Column(Boolean, default=False)
    competing_sources_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class KnowledgeGapORM(Base):
    __tablename__ = "knowledge_gaps"

    gap_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(64), nullable=False, index=True)
    domain = Column(String(255), nullable=False)
    gap_type = Column(String(64), nullable=False)
    severity = Column(String(64), nullable=False)
    missing_elements_json = Column(JSON, nullable=True)
    recommendations_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class KnowledgeEvidenceBundleORM(Base):
    __tablename__ = "knowledge_evidence_bundles"

    bundle_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(64), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    is_finalized = Column(Boolean, default=False)
    sha256_fingerprint = Column(String(128), nullable=True)
    evidences_json = Column(JSON, nullable=True)
    finalized_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class KnowledgeInvestigationORM(Base):
    __tablename__ = "knowledge_investigations"

    investigation_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(64), nullable=False, index=True)
    target_resource_id = Column(String(64), nullable=False)
    resource_type = Column(String(64), nullable=False)
    status = Column(String(64), nullable=False)
    snapshot_id = Column(String(64), nullable=True)
    findings_json = Column(JSON, nullable=True)
    evidence_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    concluded_at = Column(DateTime(timezone=True), nullable=True)


class KnowledgeTrustAssessmentORM(Base):
    __tablename__ = "knowledge_trust_assessments"

    assessment_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(64), nullable=False, index=True)
    target_resource_id = Column(String(64), nullable=False)
    overall_score = Column(Float, default=0.9)
    trust_band = Column(String(64), nullable=False)
    dimensions_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class KnowledgeAssuranceAssessmentORM(Base):
    __tablename__ = "knowledge_assurance_assessments"

    assessment_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(64), nullable=False, index=True)
    target_resource_id = Column(String(64), nullable=False)
    overall_score = Column(Float, default=0.9)
    assurance_level = Column(String(64), nullable=False)
    dimension_scores_json = Column(JSON, nullable=True)
    factors_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class KnowledgeLearningRecordORM(Base):
    __tablename__ = "knowledge_learning_records"

    record_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(64), nullable=False, index=True)
    source_event = Column(String(255), nullable=False)
    patterns_json = Column(JSON, nullable=True)
    recommendations_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class KnowledgeAssuranceSnapshotORM(Base):
    __tablename__ = "knowledge_assurance_snapshots"

    assurance_snapshot_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(64), nullable=False, index=True)
    target_resource_id = Column(String(64), nullable=False)
    snapshot_type = Column(String(64), nullable=False)
    platform_snapshot_id = Column(String(64), nullable=False)
    status = Column(String(64), nullable=False)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
