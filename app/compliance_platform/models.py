"""SQLAlchemy ORM Models for Compliance Platform (Phase 5.27)."""

from datetime import datetime, timezone
import uuid
from typing import Optional, Dict, Any

from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Integer, Float, Boolean, Text
from sqlalchemy.orm import mapped_column, Mapped

from app.core.database import Base


def _now():
    return datetime.now(timezone.utc)


class ComplianceFrameworkModel(Base):
    __tablename__ = "comp_frameworks"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"fw_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    framework_type: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default="ACTIVE")
    version: Mapped[str] = mapped_column(String, default="1.0.0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class ComplianceRequirementModel(Base):
    __tablename__ = "comp_requirements"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"req_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    framework_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    code: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    scope: Mapped[str] = mapped_column(String, default="TENANT")
    priority: Mapped[str] = mapped_column(String, default="HIGH")


class ComplianceControlModel(Base):
    __tablename__ = "comp_controls"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"ctrl_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    code: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    control_type: Mapped[str] = mapped_column(String, default="PREVENTIVE")
    category: Mapped[str] = mapped_column(String, default="SECURITY")
    status: Mapped[str] = mapped_column(String, default="ACTIVE")


class RequirementControlMappingModel(Base):
    __tablename__ = "comp_mappings"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"map_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    requirement_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    control_id: Mapped[str] = mapped_column(String, index=True, nullable=False)


class EvidenceModel(Base):
    __tablename__ = "comp_evidence"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"ev_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    subject_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    evidence_type: Mapped[str] = mapped_column(String, nullable=False)
    source_system: Mapped[str] = mapped_column(String, nullable=False)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class EvidenceBundleModel(Base):
    __tablename__ = "comp_evidence_bundles"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"bundle_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    bundle_fingerprint: Mapped[str] = mapped_column(String, nullable=False)
    is_finalized: Mapped[bool] = mapped_column(Boolean, default=True)


class ComplianceAssessmentModel(Base):
    __tablename__ = "comp_assessments"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"assess_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    framework_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    overall_result: Mapped[str] = mapped_column(String, default="INSUFFICIENT_EVIDENCE")
    assessed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class ComplianceFindingModel(Base):
    __tablename__ = "comp_findings"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"find_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    severity: Mapped[str] = mapped_column(String, default="MEDIUM")
    status: Mapped[str] = mapped_column(String, default="OPEN")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class ComplianceRemediationModel(Base):
    __tablename__ = "comp_remediations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"rem_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    finding_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String, default="PROPOSED")


class ComplianceAttestationModel(Base):
    __tablename__ = "comp_attestations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"attest_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    control_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String, default="APPROVED")


class ComplianceExceptionModel(Base):
    __tablename__ = "comp_exceptions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"exc_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    requirement_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String, default="ACTIVE")


class CompliancePostureModel(Base):
    __tablename__ = "comp_posture"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"posture_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    overall_score: Mapped[float] = mapped_column(Float, default=90.0)
    posture_band: Mapped[str] = mapped_column(String, default="ASSURED")


class ComplianceAssuranceReportModel(Base):
    __tablename__ = "comp_assurance_reports"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"assure_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    conclusion: Mapped[str] = mapped_column(String, default="ASSURED")
    report_fingerprint: Mapped[str] = mapped_column(String, nullable=False)


class AuditPackageModel(Base):
    __tablename__ = "comp_audit_packages"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"audpkg_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    package_fingerprint: Mapped[str] = mapped_column(String, nullable=False)
