"""SQLAlchemy ORM Models for Architecture Platform (Phase 5.26)."""

from datetime import datetime, timezone
import uuid
from typing import Optional, Dict, Any

from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Integer, Float, Boolean, Text
from sqlalchemy.orm import mapped_column, Mapped

from app.core.database import Base


def _now():
    return datetime.now(timezone.utc)


class ArchitectureNodeModel(Base):
    __tablename__ = "arch_nodes"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"node_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    node_type: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default="ACTIVE")
    environment: Mapped[str] = mapped_column(String, default="production")
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class ArchitectureDependencyModel(Base):
    __tablename__ = "arch_dependencies"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"dep_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    source_node_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    target_node_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    dependency_type: Mapped[str] = mapped_column(String, default="DEPENDS_ON")
    strength: Mapped[str] = mapped_column(String, default="STRONG")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class ArchitectureTopologyModel(Base):
    __tablename__ = "arch_topologies"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"top_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    environment: Mapped[str] = mapped_column(String, default="production")
    version: Mapped[str] = mapped_column(String, default="1.0.0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class ArchitectureSnapshotModel(Base):
    __tablename__ = "arch_snapshots"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"snap_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    environment: Mapped[str] = mapped_column(String, default="production")
    architecture_fingerprint: Mapped[str] = mapped_column(String, nullable=False)
    is_finalized: Mapped[bool] = mapped_column(Boolean, default=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class ArchitectureChangeModel(Base):
    __tablename__ = "arch_changes"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"change_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    action_type: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default="DRAFT")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class ArchitectureDecisionModel(Base):
    __tablename__ = "arch_decisions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"adr_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default="DRAFT")
    context: Mapped[str] = mapped_column(Text, nullable=False)
    finalized_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class ArchitectureDriftModel(Base):
    __tablename__ = "arch_drifts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"drift_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    drift_type: Mapped[str] = mapped_column(String, nullable=False)
    severity: Mapped[str] = mapped_column(String, default="MEDIUM")
    status: Mapped[str] = mapped_column(String, default="OPEN")
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class ArchitectureImpactModel(Base):
    __tablename__ = "arch_impacts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"impact_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    target_node_id: Mapped[str] = mapped_column(String, nullable=False)
    estimated_cost_impact_usd: Mapped[float] = mapped_column(Float, default=0.0)
    analyzed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class ArchitectureTrustScoreModel(Base):
    __tablename__ = "arch_trust_scores"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"archtrust_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    overall_score: Mapped[float] = mapped_column(Float, default=100.0)
    trust_band: Mapped[str] = mapped_column(String, default="HIGH_TRUST")
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
