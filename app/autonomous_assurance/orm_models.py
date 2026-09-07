"""
SQLAlchemy ORM Models for Autonomous Assurance Subsystem.
"""

from datetime import datetime, timezone
import uuid
from typing import Optional, Dict, Any

from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Integer, Float, Boolean, Text
from sqlalchemy.orm import mapped_column, Mapped

from app.core.database import Base


def _now():
    return datetime.now(timezone.utc)


class AutonomousWorkflowModel(Base):
    __tablename__ = "auto_workflows"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"wf_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    workflow_type: Mapped[str] = mapped_column(String, default="CROSS_DOMAIN_COORDINATION")
    status: Mapped[str] = mapped_column(String, default="PROPOSED")
    priority: Mapped[str] = mapped_column(String, default="MEDIUM")
    is_finalized: Mapped[bool] = mapped_column(Boolean, default=False)
    workflow_fingerprint: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class AutonomousEvidenceBundleModel(Base):
    __tablename__ = "auto_evidence"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"evb_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    workflow_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    is_sealed: Mapped[bool] = mapped_column(Boolean, default=False)
    evidence_hash: Mapped[Optional[str]] = mapped_column(String, nullable=True)
