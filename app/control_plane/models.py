"""SQLAlchemy ORM Models for Control Plane Persistence."""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import JSON, Boolean, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def _now():
    return datetime.now(timezone.utc)


class TenantModel(Base):
    __tablename__ = "cp_tenants"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"tenant_{uuid.uuid4().hex[:10]}")
    name: Mapped[str] = mapped_column(String, nullable=False)
    slug: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String, default="ACTIVE")
    configuration: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)
    suspended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    suspended_by: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class OrganizationModel(Base):
    __tablename__ = "cp_organizations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"org_{uuid.uuid4().hex[:10]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    slug: Mapped[str] = mapped_column(String, index=True, nullable=False)
    limits: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    settings: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class WorkspaceModel(Base):
    __tablename__ = "cp_workspaces"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"ws_{uuid.uuid4().hex[:10]}")
    organization_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    environment: Mapped[str] = mapped_column(String, default="DEVELOPMENT")
    limits: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    settings: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class ResourceModel(Base):
    __tablename__ = "cp_resources"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    resource_type: Mapped[str] = mapped_column(String, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    organization_id: Mapped[Optional[str]] = mapped_column(String, index=True, nullable=True)
    workspace_id: Mapped[Optional[str]] = mapped_column(String, index=True, nullable=True)
    owner_id: Mapped[str] = mapped_column(String, default="system")
    status: Mapped[str] = mapped_column(String, default="ACTIVE")
    version: Mapped[str] = mapped_column(String, default="1.0.0")
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class ResourceDependencyModel(Base):
    __tablename__ = "cp_resource_dependencies"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    parent_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    child_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    dependency_type: Mapped[str] = mapped_column(String, default="REQUIRES")


class ConfigurationModel(Base):
    __tablename__ = "cp_configurations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    scope: Mapped[str] = mapped_column(String, index=True, nullable=False)
    target_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    active_version_number: Mapped[int] = mapped_column(Integer, default=1)
    settings: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class ConfigurationVersionModel(Base):
    __tablename__ = "cp_configuration_versions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"ver_{uuid.uuid4().hex[:10]}")
    scope: Mapped[str] = mapped_column(String, index=True, nullable=False)
    target_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    settings: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_by: Mapped[str] = mapped_column(String, default="admin")
    commit_message: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class PolicyModel(Base):
    __tablename__ = "cp_policies"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"pol_{uuid.uuid4().hex[:10]}")
    name: Mapped[str] = mapped_column(String, nullable=False)
    target_type: Mapped[str] = mapped_column(String, index=True, nullable=False)
    tenant_id: Mapped[str] = mapped_column(String, index=True, default="global")
    organization_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    workspace_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    rules: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    priority: Mapped[int] = mapped_column(Integer, default=10)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class PolicyAssignmentModel(Base):
    __tablename__ = "cp_policy_assignments"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    policy_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    target_id: Mapped[str] = mapped_column(String, index=True, nullable=False)


class FeatureRolloutModel(Base):
    __tablename__ = "cp_feature_rollouts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"flag_{uuid.uuid4().hex[:8]}")
    name: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    default_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    percentage: Mapped[float] = mapped_column(Float, default=100.0)
    allowed_tenant_ids: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class AdministrativeAuditModel(Base):
    __tablename__ = "cp_audit_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"audit_{uuid.uuid4().hex[:12]}")
    actor_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    tenant_id: Mapped[str] = mapped_column(String, index=True, default="global")
    organization_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    workspace_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    action: Mapped[str] = mapped_column(String, index=True, nullable=False)
    target_resource_id: Mapped[str] = mapped_column(String, nullable=False)
    previous_state: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    new_state: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    request_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    trace_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    approval_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class LifecycleEventModel(Base):
    __tablename__ = "cp_lifecycle_events"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    resource_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    previous_state: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    current_state: Mapped[str] = mapped_column(String, nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    actor_id: Mapped[str] = mapped_column(String, default="system")
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class UsageRecordModel(Base):
    __tablename__ = "cp_usage_records"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    organization_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    workspace_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    resource_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    total_requests: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_cost_dollars: Mapped[float] = mapped_column(Float, default=0.0)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
