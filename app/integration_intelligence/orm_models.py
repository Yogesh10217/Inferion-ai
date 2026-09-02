"""SQLAlchemy Production ORM Models for Integration Intelligence (Phase 5.40)."""

from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Boolean, Float, JSON, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class IntegrationConnectorModel(Base):
    __tablename__ = "ai_integration_connectors"

    connector_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    connector_type = Column(String(64), nullable=False)
    status = Column(String(64), nullable=False, default="ACTIVE")
    external_system_id = Column(String(255), nullable=False)
    provider_name = Column(String(255), nullable=False)
    base_endpoint_url = Column(String(512), nullable=False)
    capabilities = Column(JSON, nullable=False, default=list)
    sanitized_metadata = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class IntegrationWorkflowModel(Base):
    __tablename__ = "ai_integration_workflows"

    workflow_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    workflow_type = Column(String(64), nullable=False, default="SYNC_API")
    status = Column(String(64), nullable=False, default="DRAFT")
    steps = Column(JSON, nullable=False, default=list)
    is_finalized = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class IntegrationExecutionModel(Base):
    __tablename__ = "ai_integration_executions"

    execution_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    workflow_id = Column(String(64), nullable=False, index=True)
    idempotency_key = Column(String(128), nullable=False, index=True)
    replay_token = Column(String(128), nullable=True)
    status = Column(String(64), nullable=False, default="REQUESTED")
    requires_approval = Column(Boolean, default=False)
    approval_id = Column(String(64), nullable=True)
    delegation_request_id = Column(String(64), nullable=True)
    fingerprint = Column(String(128), nullable=False, default="")
    is_finalized = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class IntegrationFailureModel(Base):
    __tablename__ = "ai_integration_failures"

    failure_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    execution_id = Column(String(64), nullable=False)
    connector_id = Column(String(64), nullable=False)
    failure_type = Column(String(64), nullable=False)
    severity = Column(String(64), nullable=False, default="HIGH")
    evidence = Column(JSON, nullable=False, default=dict)
    failed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class IntegrationRecoveryModel(Base):
    __tablename__ = "ai_integration_recoveries"

    plan_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    failure_id = Column(String(64), nullable=False)
    status = Column(String(64), nullable=False, default="PLANNED")
    steps = Column(JSON, nullable=False, default=list)
    delegation_request_id = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class IntegrationInvestigationModel(Base):
    __tablename__ = "ai_integration_investigations"

    investigation_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    target_workflow_id = Column(String(64), nullable=False)
    status = Column(String(64), nullable=False, default="OPEN")
    findings = Column(JSON, nullable=False, default=list)
    is_concluded = Column(Boolean, default=False)
    snapshot_id = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class IntegrationEvidenceModel(Base):
    __tablename__ = "ai_integration_evidence"

    bundle_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    items = Column(JSON, nullable=False, default=list)
    integrity = Column(JSON, nullable=True)
    is_finalized = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class IntegrationLearningModel(Base):
    __tablename__ = "ai_integration_learning"

    record_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    patterns = Column(JSON, nullable=False, default=list)
    recommendations = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
