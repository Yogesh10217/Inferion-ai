from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class AIAssetModel(Base):
    """SQLAlchemy model for persistent AI Assets."""

    __tablename__ = "ai_assets"

    asset_id = Column(String, primary_key=True)
    tenant_id = Column(String, default="global", index=True)
    organization_id = Column(String, nullable=True)
    workspace_id = Column(String, nullable=True)

    name = Column(String, nullable=False, index=True)
    asset_type = Column(String, nullable=False, index=True)
    description = Column(Text, default="")

    current_version = Column(String, default="1.0.0")
    status = Column(String, default="DRAFT", index=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    versions = relationship("AIAssetVersionModel", back_populates="asset", cascade="all, delete-orphan", lazy="selectin")


class AIAssetVersionModel(Base):
    """SQLAlchemy model for persistent immutable AI Asset Versions."""

    __tablename__ = "ai_asset_versions"

    version_id = Column(String, primary_key=True)
    version_number = Column(String, nullable=False)
    asset_id = Column(String, ForeignKey("ai_assets.asset_id", ondelete="CASCADE"), nullable=False, index=True)

    tenant_id = Column(String, default="global")
    organization_id = Column(String, nullable=True)
    workspace_id = Column(String, nullable=True)

    creator = Column(String, default="system")
    configuration_json = Column(Text, default="{}")
    configuration_hash = Column(String, default="")
    dependencies_json = Column(Text, default="{}")
    parent_version = Column(String, nullable=True)
    changelog = Column(Text, default="")

    status = Column(String, default="DRAFT")
    approval_status = Column(String, default="NOT_REQUESTED")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    is_immutable = Column(Boolean, default=False)

    asset = relationship("AIAssetModel", back_populates="versions")

    __table_args__ = (
        Index("idx_asset_version_num", "asset_id", "version_number", unique=True),
    )
