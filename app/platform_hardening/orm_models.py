"""
SQLAlchemy ORM models for Platform Hardening persistence.
"""

from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class PlatformAuditRecordORM(Base):
    __tablename__ = "platform_audit_records"

    audit_id = Column(String(128), primary_key=True, index=True)
    tenant_id = Column(String(128), primary_key=True, index=True)
    status = Column(String(64), nullable=False, default="PENDING")
    readiness_score = Column(Float, nullable=False, default=0.0)
    release_decision = Column(String(64), nullable=False, default="BLOCKED")
    certification_status = Column(String(64), nullable=False, default="FAILED")
    findings_count = Column(Integer, nullable=False, default=0)
    critical_findings_count = Column(Integer, nullable=False, default=0)
    started_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)
    payload_json = Column(JSON, nullable=True)


class PlatformAuditFindingORM(Base):
    __tablename__ = "platform_audit_findings"

    finding_id = Column(String(128), primary_key=True, index=True)
    audit_id = Column(String(128), nullable=False, index=True)
    tenant_id = Column(String(128), nullable=False, index=True)
    rule_id = Column(String(128), nullable=False)
    title = Column(String(256), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(32), nullable=False)
    subsystem = Column(String(128), nullable=False)
    affected_component = Column(String(256), nullable=False)
    file_path = Column(String(512), nullable=True)
    line_number = Column(Integer, nullable=True)
    root_cause_hypothesis = Column(Text, nullable=True)
    remediation_suggestion = Column(Text, nullable=True)
    evidence_reference = Column(String(128), nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    metadata_json = Column(JSON, nullable=True)


class PlatformCertificationORM(Base):
    __tablename__ = "platform_certifications"

    certification_id = Column(String(128), primary_key=True, index=True)
    tenant_id = Column(String(128), primary_key=True, index=True)
    status = Column(String(64), nullable=False)
    release_decision = Column(String(64), nullable=False)
    overall_score = Column(Float, nullable=False)
    sha256_hash = Column(String(128), nullable=False)
    previous_hash = Column(String(128), nullable=True)
    audited_phases_count = Column(Integer, nullable=False, default=8)
    certified_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    details_json = Column(JSON, nullable=True)


class PlatformHardeningSnapshotORM(Base):
    __tablename__ = "platform_hardening_snapshots"

    snapshot_id = Column(String(128), primary_key=True, index=True)
    tenant_id = Column(String(128), primary_key=True, index=True)
    sha256_hash = Column(String(128), nullable=False)
    snapshot_data = Column(JSON, nullable=False)
    captured_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
