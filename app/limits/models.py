import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def _now():
    return datetime.now(timezone.utc)


class UsageRecord(Base):
    """Immutable log of inference usage."""
    __tablename__ = "usage_records"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    workspace_id: Mapped[Optional[str]] = mapped_column(String, index=True, nullable=True)
    user_id: Mapped[Optional[str]] = mapped_column(String, index=True, nullable=True)
    api_key_id: Mapped[Optional[str]] = mapped_column(String, index=True, nullable=True)

    provider: Mapped[str] = mapped_column(String, nullable=False, index=True)
    model: Mapped[str] = mapped_column(String, nullable=False, index=True)

    request_tokens: Mapped[int] = mapped_column(Integer, default=0)
    response_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    request_count: Mapped[int] = mapped_column(Integer, default=1)

    # Extended fields
    status_code: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    error_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_streaming: Mapped[bool] = mapped_column(Boolean, default=False)
    is_cached: Mapped[bool] = mapped_column(Boolean, default=False)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)


class QuotaPolicy(Base):
    """Hierarchical quota configurations supporting inheritance."""
    __tablename__ = "quota_policies"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False)

    organization_id: Mapped[Optional[str]] = mapped_column(String, index=True, nullable=True)
    workspace_id: Mapped[Optional[str]] = mapped_column(String, index=True, nullable=True)
    user_id: Mapped[Optional[str]] = mapped_column(String, index=True, nullable=True)
    api_key_id: Mapped[Optional[str]] = mapped_column(String, index=True, nullable=True)

    # For inheritance
    parent_policy_id: Mapped[Optional[str]] = mapped_column(ForeignKey("quota_policies.id"), nullable=True)

    requests_per_minute: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    requests_per_hour: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    requests_per_day: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    tokens_per_day: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    tokens_per_month: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    concurrent_requests: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class RateLimitPolicy(Base):
    """Specific rate limiting strategy rules for an entity."""
    __tablename__ = "rate_limit_policies"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    organization_id: Mapped[Optional[str]] = mapped_column(String, index=True, nullable=True)
    workspace_id: Mapped[Optional[str]] = mapped_column(String, index=True, nullable=True)
    api_key_id: Mapped[Optional[str]] = mapped_column(String, index=True, nullable=True)

    strategy: Mapped[str] = mapped_column(String, nullable=False, default="sliding_window")
    limit: Mapped[int] = mapped_column(Integer, nullable=False)
    window_seconds: Mapped[int] = mapped_column(Integer, nullable=False)


class QuotaWindow(Base):
    """Tracks current utilization for a rolling time window."""
    __tablename__ = "quota_windows"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Identifies the scope of this window (e.g., 'org:123', 'key:456')
    scope_id: Mapped[str] = mapped_column(String, index=True, nullable=False)

    # Metric being tracked (e.g., 'tokens', 'requests')
    metric_type: Mapped[str] = mapped_column(String, nullable=False)

    # Window period identifier (e.g., '2026-07', '2026-07-28')
    window_id: Mapped[str] = mapped_column(String, index=True, nullable=False)

    value: Mapped[int] = mapped_column(BigInteger, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class UsageSnapshot(Base):
    """Pre-aggregated usage for fast analytical querying."""
    __tablename__ = "usage_snapshots"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    workspace_id: Mapped[Optional[str]] = mapped_column(String, index=True, nullable=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=False), index=True, nullable=False)

    total_requests: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(BigInteger, default=0)
    total_errors: Mapped[int] = mapped_column(Integer, default=0)
    average_latency_ms: Mapped[int] = mapped_column(Integer, default=0)
