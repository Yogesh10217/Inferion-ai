"""SQLAlchemy ORM Persistence Models for Platform Operations."""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, JSON, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def _now():
    return datetime.now(timezone.utc)


class ServiceModel(Base):
    """SQLAlchemy model for Service catalog entries."""
    __tablename__ = "platform_services"

    service_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    name = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    service_tier = Column(String(32), nullable=False)
    health = Column(String(32), nullable=False)
    status = Column(String(32), nullable=False)
    owner_team = Column(String(128), nullable=True)
    operational_contact = Column(String(128), nullable=True)
    slo_ids = Column(JSON, nullable=False, default=list)
    resource_references = Column(JSON, nullable=False, default=list)
    extra_metadata = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), default=_now)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)


class ServiceDependencyModel(Base):
    """SQLAlchemy model for Service Dependency relationships."""
    __tablename__ = "platform_service_dependencies"

    dependency_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    source_service_id = Column(String(64), nullable=False, index=True)
    target_service_id = Column(String(64), nullable=False, index=True)
    dependency_type = Column(String(32), nullable=False)
    is_critical = Column(Boolean, default=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=_now)


class OperationalSignalModel(Base):
    """SQLAlchemy model for Operational Signals."""
    __tablename__ = "platform_operational_signals"

    signal_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    source = Column(String(64), nullable=False)
    signal_type = Column(String(64), nullable=False)
    severity = Column(String(32), nullable=False)
    service_id = Column(String(64), nullable=True, index=True)
    resource_id = Column(String(64), nullable=True)
    correlation_id = Column(String(64), nullable=True, index=True)
    trace_id = Column(String(64), nullable=True)
    message = Column(Text, nullable=False)
    metrics = Column(JSON, nullable=False, default=dict)
    payload = Column(JSON, nullable=False, default=dict)
    timestamp = Column(DateTime(timezone=True), default=_now)


class RemediationPlanModel(Base):
    """SQLAlchemy model for Remediation Plans."""
    __tablename__ = "platform_remediation_plans"

    plan_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    incident_id = Column(String(64), nullable=False, index=True)
    service_id = Column(String(64), nullable=False)
    overall_risk_level = Column(String(32), nullable=False)
    status = Column(String(32), nullable=False)
    steps = Column(JSON, nullable=False, default=list)
    approval_request_id = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), default=_now)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)
