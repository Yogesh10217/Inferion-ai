"""SQLAlchemy Persistence Models for Governance Platform Domain Entities."""

from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, String, Text

from app.db.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class GovernanceFrameworkModel(Base):
    __tablename__ = "governance_frameworks"

    framework_id = Column(String(64), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    tenant_id = Column(String(64), index=True, nullable=False, default="global")
    description = Column(Text, nullable=True)
    controls = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)


class GovernanceViolationModel(Base):
    __tablename__ = "governance_violations"

    violation_id = Column(String(64), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    tenant_id = Column(String(64), index=True, nullable=False, default="global")
    violation_type = Column(String(64), nullable=False)
    severity = Column(String(32), nullable=False)
    status = Column(String(32), nullable=False)
    primary_resource_id = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    evidence_ids = Column(JSON, nullable=False, default=list)
    incident_id = Column(String(64), nullable=True)
    detected_at = Column(DateTime(timezone=True), default=_now, nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)


class GovernanceEvidenceModel(Base):
    __tablename__ = "governance_evidence"

    evidence_id = Column(String(64), primary_key=True, index=True)
    source_system = Column(String(64), nullable=False)
    evidence_type = Column(String(32), nullable=False)
    source_record_id = Column(String(128), nullable=False)
    tenant_id = Column(String(64), index=True, nullable=False, default="global")
    resource_id = Column(String(128), nullable=False)
    payload = Column(JSON, nullable=False, default=dict)
    content_hash = Column(String(128), nullable=False)
    previous_hash = Column(String(128), nullable=True)
    collected_at = Column(DateTime(timezone=True), default=_now, nullable=False)
