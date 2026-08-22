"""SQLAlchemy Persistence Models for MLOps Platform."""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, JSON, Text, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def _now() -> datetime:
    return datetime.now(timezone.utc)


class AIAssetModel(Base):
    __tablename__ = "mlops_ai_assets"

    id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    organization_id = Column(String(64), nullable=True)
    workspace_id = Column(String(64), nullable=True)

    name = Column(String(128), nullable=False)
    asset_type = Column(String(64), nullable=False)
    description = Column(Text, nullable=True)

    current_version = Column(String(32), default="1.0.0")
    status = Column(String(32), default="DRAFT")

    created_at = Column(DateTime(timezone=True), default=_now)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)


class AIAssetVersionModel(Base):
    __tablename__ = "mlops_ai_asset_versions"

    id = Column(String(64), primary_key=True)
    version_number = Column(String(32), nullable=False)
    asset_id = Column(String(64), ForeignKey("mlops_ai_assets.id"), nullable=False, index=True)

    tenant_id = Column(String(64), nullable=False, index=True)
    creator = Column(String(128), default="system")

    configuration = Column(JSON, nullable=False)
    configuration_hash = Column(String(64), nullable=False)
    dependencies = Column(JSON, nullable=True)
    parent_version = Column(String(32), nullable=True)
    changelog = Column(Text, nullable=True)

    status = Column(String(32), default="DRAFT")
    approval_status = Column(String(32), default="NOT_REQUESTED")
    is_immutable = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=_now)


class DeploymentModel(Base):
    __tablename__ = "mlops_deployments"

    id = Column(String(64), primary_key=True)
    name = Column(String(128), nullable=False)
    tenant_id = Column(String(64), nullable=False, index=True)

    asset_id = Column(String(64), nullable=False)
    version_number = Column(String(32), nullable=False)
    environment = Column(String(32), default="DEVELOPMENT")
    status = Column(String(32), default="PENDING")

    active_traffic_percentage = Column(Float, default=100.0)
    created_at = Column(DateTime(timezone=True), default=_now)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)
