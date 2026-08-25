"""SQLAlchemy Database ORM Models for Reliability Platform (Phase 5.31)."""

from sqlalchemy import Column, String, Float, DateTime, JSON, Text, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone

Base = declarative_base()


class ReliabilityServiceModel(Base):
    __tablename__ = "reliability_services"

    service_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    name = Column(String(128), nullable=False)
    tier = Column(String(32), nullable=False)
    status = Column(String(32), nullable=False)
    owner_team = Column(String(64), nullable=False)
    architecture_node_id = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    contract_version = Column(String(16), default="1.0.0")


class SLODefinitionModel(Base):
    __tablename__ = "reliability_slos"

    slo_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    service_id = Column(String(64), nullable=False, index=True)
    name = Column(String(128), nullable=False)
    target_percentage = Column(Float, nullable=False)
    sli_type = Column(String(32), nullable=False)
    consumed_budget_pct = Column(Float, default=0.0)
    remaining_budget_pct = Column(Float, default=100.0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    contract_version = Column(String(16), default="1.0.0")


class ReliabilityIncidentModel(Base):
    __tablename__ = "reliability_incidents"

    incident_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    service_id = Column(String(64), nullable=False, index=True)
    title = Column(String(256), nullable=False)
    severity = Column(String(32), nullable=False)
    status = Column(String(32), nullable=False)
    timeline_json = Column(JSON, nullable=False)
    fingerprint = Column(String(128), nullable=True)
    finalized_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    contract_version = Column(String(16), default="1.0.0")


class PostmortemReportModel(Base):
    __tablename__ = "reliability_postmortems"

    report_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    incident_id = Column(String(64), nullable=False, index=True)
    summary = Column(Text, nullable=False)
    root_cause = Column(Text, nullable=False)
    status = Column(String(32), nullable=False)
    fingerprint = Column(String(128), nullable=True)
    finalized_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    contract_version = Column(String(16), default="1.0.0")


class RemediationPlanModel(Base):
    __tablename__ = "reliability_remediations"

    plan_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    incident_id = Column(String(64), nullable=False, index=True)
    idempotency_key = Column(String(128), nullable=False)
    actions_json = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    contract_version = Column(String(16), default="1.0.0")
