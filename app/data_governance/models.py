"""SQLAlchemy ORM Models for Data Governance Platform (Phase 5.25)."""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import JSON, Boolean, DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def _now():
    return datetime.now(timezone.utc)


class DataAssetModel(Base):
    __tablename__ = "gov_data_assets"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"asset_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    owner_id: Mapped[str] = mapped_column(String, nullable=False)
    classification: Mapped[str] = mapped_column(String, default="CONFIDENTIAL")
    domain: Mapped[str] = mapped_column(String, default="GENERAL")
    status: Mapped[str] = mapped_column(String, default="REGISTERED")
    source_reference: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class DataContractModel(Base):
    __tablename__ = "gov_data_contracts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"contract_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    asset_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    version: Mapped[str] = mapped_column(String, default="1.0.0")
    status: Mapped[str] = mapped_column(String, default="DRAFT")
    schema_spec: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class DataQualityResultModel(Base):
    __tablename__ = "gov_data_quality_results"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"qr_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    asset_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    overall_score: Mapped[float] = mapped_column(Float, default=100.0)
    has_critical_violation: Mapped[bool] = mapped_column(Boolean, default=False)
    metrics_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    evaluated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class DataLineageModel(Base):
    __tablename__ = "gov_data_lineage"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"lin_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    source_node: Mapped[str] = mapped_column(String, nullable=False)
    target_node: Mapped[str] = mapped_column(String, nullable=False)
    operation: Mapped[str] = mapped_column(String, nullable=False)
    correlation_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class DataConsentModel(Base):
    __tablename__ = "gov_data_consents"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"consent_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    subject_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String, default="GRANTED")
    purposes_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    granted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class DataAccessEventModel(Base):
    __tablename__ = "gov_data_access_events"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"access_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    principal_id: Mapped[str] = mapped_column(String, nullable=False)
    asset_id: Mapped[str] = mapped_column(String, nullable=False)
    action: Mapped[str] = mapped_column(String, nullable=False)
    decision: Mapped[str] = mapped_column(String, nullable=False)
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class DataRetentionPolicyModel(Base):
    __tablename__ = "gov_data_retention_policies"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"ret_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    rules_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class DataShareModel(Base):
    __tablename__ = "gov_data_shares"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"share_{uuid.uuid4().hex[:12]}")
    source_tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    target_tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    asset_id: Mapped[str] = mapped_column(String, nullable=False)
    approved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class DataTrustScoreModel(Base):
    __tablename__ = "gov_data_trust_scores"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"trust_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    asset_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    overall_score: Mapped[float] = mapped_column(Float, default=100.0)
    trust_band: Mapped[str] = mapped_column(String, default="HIGH_TRUST")
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
