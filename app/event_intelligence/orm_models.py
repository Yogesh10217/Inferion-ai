"""SQLAlchemy Database ORM Models for Event Intelligence Platform (Phase 5.34)."""

from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class EnterpriseEventModel(Base):
    __tablename__ = "enterprise_events"

    event_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    source_id = Column(String(64), nullable=False)
    source_name = Column(String(128), nullable=False)
    event_type = Column(String(64), nullable=False)
    category = Column(String(32), nullable=False)
    severity = Column(String(32), nullable=False)
    priority = Column(String(32), nullable=False)
    status = Column(String(32), nullable=False)
    metadata_json = Column(JSON, nullable=False)
    correlation_reference = Column(String(64), nullable=True)
    idempotency_reference = Column(String(128), nullable=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    contract_version = Column(String(16), default="1.0.0")


class EventCorrelationModel(Base):
    __tablename__ = "event_correlations"

    group_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    title = Column(String(256), nullable=False)
    correlation_type = Column(String(32), nullable=False)
    event_ids_json = Column(JSON, nullable=False)
    confidence_score = Column(Float, nullable=False, default=0.9)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    contract_version = Column(String(16), default="1.0.0")


class AutomationRuleModel(Base):
    __tablename__ = "event_automation_rules"

    rule_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    name = Column(String(128), nullable=False)
    status = Column(String(32), nullable=False)
    conditions_json = Column(JSON, nullable=False)
    actions_json = Column(JSON, nullable=False)
    fingerprint = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    contract_version = Column(String(16), default="1.0.0")


class AutomationPlanModel(Base):
    __tablename__ = "event_automation_plans"

    plan_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    event_id = Column(String(64), nullable=False, index=True)
    action = Column(String(64), nullable=False)
    status = Column(String(32), nullable=False)
    requires_approval = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    contract_version = Column(String(16), default="1.0.0")


class EventInvestigationModel(Base):
    __tablename__ = "event_investigations"

    investigation_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    event_id = Column(String(64), nullable=False, index=True)
    status = Column(String(32), nullable=False)
    findings_json = Column(JSON, nullable=False)
    conclusion_json = Column(JSON, nullable=True)
    snapshot_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    contract_version = Column(String(16), default="1.0.0")


class EventResponsePlanModel(Base):
    __tablename__ = "event_response_plans"

    plan_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    event_id = Column(String(64), nullable=False, index=True)
    actions_json = Column(JSON, nullable=False)
    status = Column(String(32), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    contract_version = Column(String(16), default="1.0.0")


class EventResolutionModel(Base):
    __tablename__ = "event_resolutions"

    resolution_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    event_id = Column(String(64), nullable=False, index=True)
    status = Column(String(32), nullable=False)
    fingerprint = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    contract_version = Column(String(16), default="1.0.0")


class EventLearningModel(Base):
    __tablename__ = "event_learnings"

    record_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    pattern_json = Column(JSON, nullable=False)
    recommendations_json = Column(JSON, nullable=False)
    learned_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    contract_version = Column(String(16), default="1.0.0")
