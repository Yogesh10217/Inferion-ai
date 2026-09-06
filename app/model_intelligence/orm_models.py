"""SQLAlchemy Production Models for Model Intelligence Platform (Phase 5.44)."""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, DateTime, Integer, JSON, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ModelReferenceORM(Base):
    __tablename__ = "model_intelligence_references"

    model_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    model_type = Column(String(64), nullable=False)
    status = Column(String(64), default="ACTIVE")
    provider_id = Column(String(64), nullable=False)
    current_version_tag = Column(String(64), default="1.0.0")
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ModelEvaluationORM(Base):
    __tablename__ = "model_intelligence_evaluations"

    evaluation_id = Column(String(64), primary_key=True, index=True)
    model_id = Column(String(64), nullable=False, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    version_tag = Column(String(64), nullable=False)
    eval_type = Column(String(64), nullable=False)
    overall_score = Column(Float, nullable=False)
    passed = Column(Boolean, default=True)
    evidence_fingerprint = Column(String(128), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ModelBenchmarkORM(Base):
    __tablename__ = "model_intelligence_benchmarks"

    benchmark_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    suite_name = Column(String(255), nullable=False)
    results_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ModelPerformanceORM(Base):
    __tablename__ = "model_intelligence_performance"

    performance_id = Column(String(64), primary_key=True, index=True)
    model_id = Column(String(64), nullable=False, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    latency_p95_ms = Column(Float, default=0.0)
    throughput_rps = Column(Float, default=0.0)
    error_rate_percentage = Column(Float, default=0.0)
    availability_percentage = Column(Float, default=100.0)
    trend = Column(String(64), default="STABLE")
    recorded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ModelDriftORM(Base):
    __tablename__ = "model_intelligence_drifts"

    drift_id = Column(String(64), primary_key=True, index=True)
    model_id = Column(String(64), nullable=False, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    drift_type = Column(String(64), nullable=False)
    severity = Column(String(64), nullable=False)
    drift_score = Column(Float, nullable=False)
    evidence_fingerprint = Column(String(128), nullable=False)
    detected_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ModelIncidentORM(Base):
    __tablename__ = "model_intelligence_incidents"

    incident_id = Column(String(64), primary_key=True, index=True)
    model_id = Column(String(64), nullable=False, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    severity = Column(String(64), nullable=False)
    status = Column(String(64), default="DETECTED")
    impact_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    closed_at = Column(DateTime(timezone=True), nullable=True)


class ModelInvestigationORM(Base):
    __tablename__ = "model_intelligence_investigations"

    investigation_id = Column(String(64), primary_key=True, index=True)
    incident_id = Column(String(64), nullable=False, index=True)
    model_id = Column(String(64), nullable=False, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    status = Column(String(64), default="OPEN")
    findings_json = Column(JSON, nullable=True)
    snapshot_id = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ModelRemediationPlanORM(Base):
    __tablename__ = "model_intelligence_remediation_plans"

    plan_id = Column(String(64), primary_key=True, index=True)
    model_id = Column(String(64), nullable=False, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    priority = Column(String(64), nullable=False)
    status = Column(String(64), default="DRAFT")
    actions_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ModelEvidenceBundleORM(Base):
    __tablename__ = "model_intelligence_evidence_bundles"

    bundle_id = Column(String(64), primary_key=True, index=True)
    model_id = Column(String(64), nullable=False, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    fingerprint = Column(String(128), nullable=False)
    finalized = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ModelAssuranceORM(Base):
    __tablename__ = "model_intelligence_assurance"

    assessment_id = Column(String(64), primary_key=True, index=True)
    model_id = Column(String(64), nullable=False, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    overall_assurance_score = Column(Float, nullable=False)
    status = Column(String(64), default="ASSURED")
    scores_json = Column(JSON, nullable=True)
    assessed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ModelLearningRecordORM(Base):
    __tablename__ = "model_intelligence_learning_records"

    record_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    target_model_id = Column(String(64), nullable=False)
    recommendation_text = Column(Text, nullable=False)
    auto_execute = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
