"""SQLAlchemy ORM models for Operations Assurance entities."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, Integer, DateTime, JSON, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class OperationalServiceORM(Base):
    __tablename__ = "operational_services"

    service_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(64), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    service_type = Column(String(64), nullable=False)
    status = Column(String(64), nullable=False)
    tier = Column(String(64), nullable=False)
    criticality = Column(String(64), nullable=False)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ServiceHealthORM(Base):
    __tablename__ = "operational_service_health"

    assessment_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(64), nullable=False, index=True)
    service_id = Column(String(64), nullable=False, index=True)
    status = Column(String(64), nullable=False)
    availability_score = Column(Float, default=1.0)
    latency_p99_ms = Column(Float, default=0.0)
    error_rate = Column(Float, default=0.0)
    explanations_json = Column(JSON, nullable=True)
    assessed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ServiceDependencyORM(Base):
    __tablename__ = "operational_dependencies"

    dependency_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(64), nullable=False, index=True)
    source_service_id = Column(String(64), nullable=False, index=True)
    target_id = Column(String(64), nullable=False)
    dependency_type = Column(String(64), nullable=False)
    criticality = Column(String(64), nullable=False)
    is_hard_dependency = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class OperationalEventORM(Base):
    __tablename__ = "operational_events"

    event_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(64), nullable=False, index=True)
    service_id = Column(String(64), nullable=False, index=True)
    event_type = Column(String(64), nullable=False)
    severity = Column(String(64), nullable=False)
    summary = Column(Text, nullable=False)
    payload_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class OperationalAnomalyORM(Base):
    __tablename__ = "operational_anomalies"

    anomaly_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(64), nullable=False, index=True)
    service_id = Column(String(64), nullable=False, index=True)
    category = Column(String(64), nullable=False)
    severity = Column(String(64), nullable=False)
    metric_name = Column(String(128), nullable=False)
    observed_value = Column(Float, nullable=False)
    explanation = Column(Text, nullable=False)
    detected_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class OperationalIncidentORM(Base):
    __tablename__ = "operational_incidents"

    incident_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(64), nullable=False, index=True)
    service_id = Column(String(64), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    severity = Column(String(64), nullable=False)
    state = Column(String(64), nullable=False)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class RootCauseAssessmentORM(Base):
    __tablename__ = "operational_root_causes"

    assessment_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(64), nullable=False, index=True)
    service_id = Column(String(64), nullable=False, index=True)
    primary_category = Column(String(64), nullable=False)
    confidence_score = Column(Float, default=0.85)
    root_cause_summary = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class CapacityAssessmentORM(Base):
    __tablename__ = "operational_capacity_assessments"

    assessment_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(64), nullable=False, index=True)
    service_id = Column(String(64), nullable=False, index=True)
    resource_type = Column(String(64), nullable=False)
    current_utilization = Column(Float, nullable=False)
    projected_utilization = Column(Float, nullable=False)
    risk_level = Column(String(64), nullable=False)
    advisory_recommendation = Column(Text, nullable=False)
    auto_execute = Column(Boolean, default=False)
    assessed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class OperationalForecastORM(Base):
    __tablename__ = "operational_forecasts"

    forecast_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(64), nullable=False, index=True)
    service_id = Column(String(64), nullable=False, index=True)
    scenario = Column(String(64), nullable=False)
    horizon_days = Column(Integer, default=30)
    failure_probability = Column(Float, default=0.05)
    auto_execute = Column(Boolean, default=False)
    generated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class OperationalRecommendationORM(Base):
    __tablename__ = "operational_recommendations"

    recommendation_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(64), nullable=False, index=True)
    service_id = Column(String(64), nullable=False, index=True)
    recommendation_type = Column(String(64), nullable=False)
    title = Column(String(255), nullable=False)
    priority = Column(String(64), default="HIGH")
    auto_execute = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class OperationalPlanORM(Base):
    __tablename__ = "operational_plans"

    plan_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(64), nullable=False, index=True)
    service_id = Column(String(64), nullable=False, index=True)
    strategy = Column(String(64), nullable=False)
    status = Column(String(64), nullable=False)
    steps_json = Column(JSON, nullable=True)
    auto_execute = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class OperationalInvestigationORM(Base):
    __tablename__ = "operational_investigations"

    investigation_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(64), nullable=False, index=True)
    service_id = Column(String(64), nullable=False, index=True)
    status = Column(String(64), nullable=False)
    snapshot_id = Column(String(64), nullable=True)
    findings_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class OperationalEvidenceORM(Base):
    __tablename__ = "operational_evidence"

    evidence_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(64), nullable=False, index=True)
    service_id = Column(String(64), nullable=False, index=True)
    evidence_type = Column(String(64), nullable=False)
    sha256_hash = Column(String(128), nullable=False)
    is_finalized = Column(Boolean, default=True)
    content_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class OperationalLearningORM(Base):
    __tablename__ = "operational_learning_records"

    record_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(64), nullable=False, index=True)
    service_id = Column(String(64), nullable=False, index=True)
    event_summary = Column(Text, nullable=False)
    learned_insight = Column(Text, nullable=False)
    auto_execute = Column(Boolean, default=False)
    recorded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
