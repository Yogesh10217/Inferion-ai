"""SQLAlchemy ORM Persistence Models for Knowledge Intelligence Platform (Phase 5.35)."""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, DateTime, Text, Index
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class KnowledgeItemModel(Base):
    __tablename__ = "ki_knowledge_items"

    item_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    knowledge_type = Column(String(64), nullable=False)
    status = Column(String(64), nullable=False, index=True)
    classification = Column(String(64), nullable=False)
    origin = Column(String(64), nullable=False)
    title = Column(String(256), nullable=False)
    summary = Column(Text, nullable=True)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_ki_items_tenant_status", "tenant_id", "status"),
        Index("idx_ki_items_tenant_type", "tenant_id", "knowledge_type"),
    )


class KnowledgeSourceModel(Base):
    __tablename__ = "ki_knowledge_sources"

    source_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    name = Column(String(256), nullable=False)
    source_type = Column(String(64), nullable=False)
    status = Column(String(64), nullable=False, index=True)
    reference_json = Column(Text, nullable=True)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    __table_args__ = (
        Index("idx_ki_sources_tenant_type", "tenant_id", "source_type"),
    )


class KnowledgeProvenanceModel(Base):
    __tablename__ = "ki_provenance_records"

    record_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    target_id = Column(String(64), nullable=False, index=True)
    provenance_type = Column(String(64), nullable=False)
    upstream_json = Column(Text, nullable=True)
    transformation = Column(Text, nullable=True)
    fingerprint = Column(String(128), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    __table_args__ = (
        Index("idx_ki_prov_tenant_target", "tenant_id", "target_id"),
    )


class KnowledgeRelationshipModel(Base):
    __tablename__ = "ki_relationships"

    relationship_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    source_id = Column(String(64), nullable=False, index=True)
    target_id = Column(String(64), nullable=False, index=True)
    relationship_type = Column(String(64), nullable=False)
    strength = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    __table_args__ = (
        Index("idx_ki_rel_tenant_src_tgt", "tenant_id", "source_id", "target_id"),
    )


class KnowledgeContradictionModel(Base):
    __tablename__ = "ki_contradictions"

    contradiction_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    item_a_id = Column(String(64), nullable=False, index=True)
    item_b_id = Column(String(64), nullable=False, index=True)
    contradiction_type = Column(String(64), nullable=False)
    severity = Column(String(64), nullable=False)
    status = Column(String(64), nullable=False, index=True)
    detected_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class KnowledgeRecommendationModel(Base):
    __tablename__ = "ki_recommendations"

    recommendation_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    target_id = Column(String(64), nullable=False, index=True)
    recommendation_type = Column(String(64), nullable=False)
    priority = Column(String(64), nullable=False)
    status = Column(String(64), nullable=False, index=True)
    title = Column(String(256), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class KnowledgeInvestigationModel(Base):
    __tablename__ = "ki_investigations"

    investigation_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    target_id = Column(String(64), nullable=False, index=True)
    status = Column(String(64), nullable=False, index=True)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class OrganizationalMemoryModel(Base):
    __tablename__ = "ki_org_memory"

    memory_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    memory_type = Column(String(64), nullable=False)
    scope = Column(String(64), nullable=False)
    retention_status = Column(String(64), nullable=False, index=True)
    key = Column(String(256), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class KnowledgeLearningModel(Base):
    __tablename__ = "ki_learning_records"

    record_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    target_id = Column(String(64), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
