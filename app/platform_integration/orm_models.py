"""SQLAlchemy Persistence Models for Platform Integration (Phase 5.58)."""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, Text, JSON
from app.core.database import Base


class IntegrationContextORM(Base):
    __tablename__ = "platform_integration_contexts"

    context_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    fingerprint = Column(String(64), nullable=False)
    active_platforms = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class IntegrationCorrelationORM(Base):
    __tablename__ = "platform_integration_correlations"

    correlation_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    correlation_strength = Column(Float, nullable=False)
    source_platforms = Column(JSON, nullable=False)
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
