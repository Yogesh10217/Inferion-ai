"""Production SQLAlchemy ORM Models for Platform Resilience Subsystem (Phase 5.37)."""

from sqlalchemy import Column, String, DateTime, Float, Boolean, Integer, JSON, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone

Base = declarative_base()


class ResilienceServiceModel(Base):
    __tablename__ = "resilience_services"

    service_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    service_name = Column(String(255), nullable=False)
    tier = Column(String(64), nullable=False, default="TIER_2_STANDARD")
    region = Column(String(64), nullable=False, default="us-east-1")
    status = Column(String(64), nullable=False, default="ACTIVE")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class CapacityProfileModel(Base):
    __tablename__ = "capacity_profiles"

    profile_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    resource_id = Column(String(64), nullable=False, index=True)
    metrics_json = Column(JSON, nullable=True)
    status = Column(String(64), nullable=False, default="NORMAL")
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ScalingPlanModel(Base):
    __tablename__ = "scaling_plans"

    plan_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    resource_id = Column(String(64), nullable=False, index=True)
    direction = Column(String(64), nullable=False, default="SCALE_OUT")
    delegation_id = Column(String(64), nullable=True)
    status = Column(String(64), nullable=False, default="PLANNED")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class FailoverRequestModel(Base):
    __tablename__ = "failover_requests"

    plan_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    service_id = Column(String(64), nullable=False, index=True)
    source_region = Column(String(64), nullable=False)
    target_region = Column(String(64), nullable=False)
    delegation_id = Column(String(64), nullable=True)
    status = Column(String(64), nullable=False, default="REQUESTED")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class DisasterRecoveryPlanModel(Base):
    __tablename__ = "disaster_recovery_plans"

    dr_plan_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    scenario = Column(String(64), nullable=False)
    priority = Column(String(64), nullable=False, default="P0_CRITICAL")
    status = Column(String(64), nullable=False, default="PLANNED")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class RecoveryPlanModel(Base):
    __tablename__ = "recovery_plans"

    recovery_plan_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    incident_id = Column(String(64), nullable=False, index=True)
    affected_service_id = Column(String(64), nullable=False)
    delegation_id = Column(String(64), nullable=True)
    status = Column(String(64), nullable=False, default="DETECTED")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class OperationalRunbookModel(Base):
    __tablename__ = "operational_runbooks"

    runbook_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    trigger = Column(String(64), nullable=False)
    is_immutable = Column(Boolean, default=False)
    status = Column(String(64), nullable=False, default="DRAFT")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ReadinessAssessmentModel(Base):
    __tablename__ = "readiness_assessments"

    assessment_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    service_id = Column(String(64), nullable=False, index=True)
    status = Column(String(64), nullable=False, default="READY")
    score_pct = Column(Float, default=100.0)
    evaluated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ResilienceExperimentModel(Base):
    __tablename__ = "resilience_experiments"

    experiment_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    scenario = Column(String(64), nullable=False)
    target_service_id = Column(String(64), nullable=False)
    delegation_id = Column(String(64), nullable=True)
    status = Column(String(64), nullable=False, default="PLANNED")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ResilienceSnapshotModel(Base):
    __tablename__ = "resilience_snapshots"

    snapshot_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    resource_id = Column(String(64), nullable=False, index=True)
    fingerprint_sha256 = Column(String(64), nullable=False)
    platform_snapshot_id = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
