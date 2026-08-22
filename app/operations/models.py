"""SQLAlchemy Persistence Models for Operations Platform."""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Numeric, DateTime, JSON, Text, Boolean, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def _now() -> datetime:
    return datetime.now(timezone.utc)


class TelemetryEventModel(Base):
    __tablename__ = "operations_telemetry_events"

    id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    telemetry_type = Column(String(32), nullable=False)
    severity = Column(String(32), nullable=False)
    source_service = Column(String(64), nullable=False)

    trace_id = Column(String(64), nullable=True, index=True)
    request_id = Column(String(64), nullable=True, index=True)
    execution_id = Column(String(64), nullable=True, index=True)

    message = Column(Text, nullable=False)
    payload = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=_now, index=True)


class ServiceLevelObjectiveModel(Base):
    __tablename__ = "operations_slos"

    id = Column(String(64), primary_key=True)
    name = Column(String(128), nullable=False)
    tenant_id = Column(String(64), nullable=False, index=True)
    slo_type = Column(String(64), nullable=False)
    target_percentage = Column(Float, nullable=False)
    current_value = Column(Float, default=100.0)
    status = Column(String(32), default="HEALTHY")
    created_at = Column(DateTime(timezone=True), default=_now)


class IncidentModel(Base):
    __tablename__ = "operations_incidents"

    id = Column(String(64), primary_key=True)
    title = Column(String(256), nullable=False)
    tenant_id = Column(String(64), nullable=False, index=True)
    severity = Column(String(32), nullable=False)
    status = Column(String(32), nullable=False)
    primary_resource_id = Column(String(128), nullable=True)

    timeline = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=_now)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
