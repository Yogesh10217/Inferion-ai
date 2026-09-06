"""SQLAlchemy Production Models for Data Intelligence (Phase 5.43)."""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, DateTime, Integer, JSON, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class DatasetReferenceModel(Base):
    __tablename__ = "data_intelligence_datasets"

    dataset_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    dataset_type = Column(String(64), default="TABLE")
    status = Column(String(64), default="ACTIVE")
    source_id = Column(String(64), nullable=True)
    external_uri = Column(String(512), nullable=True)
    classification_tier = Column(String(64), default="CONFIDENTIAL")
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class DataSourceModel(Base):
    __tablename__ = "data_intelligence_sources"

    source_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    source_type = Column(String(64), nullable=False)
    status = Column(String(64), default="CONNECTED")
    connection_endpoint = Column(String(512), nullable=False)
    sanitized_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class DataQualityResultModel(Base):
    __tablename__ = "data_intelligence_quality_results"

    result_id = Column(String(64), primary_key=True, index=True)
    dataset_id = Column(String(64), nullable=False, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    status = Column(String(64), default="PASSED")
    overall_quality_score = Column(Float, default=1.0)
    dimension_scores = Column(JSON, nullable=True)
    evaluated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class DataValidationResultModel(Base):
    __tablename__ = "data_intelligence_validation_results"

    validation_id = Column(String(64), primary_key=True, index=True)
    dataset_id = Column(String(64), nullable=False, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    status = Column(String(64), default="PASSED")
    failure_reasons = Column(JSON, nullable=True)
    validated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class DataAnomalyModel(Base):
    __tablename__ = "data_intelligence_anomalies"

    anomaly_id = Column(String(64), primary_key=True, index=True)
    dataset_id = Column(String(64), nullable=False, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    anomaly_type = Column(String(64), nullable=False)
    severity = Column(String(64), default="HIGH")
    status = Column(String(64), default="DETECTED")
    evidence_json = Column(JSON, nullable=True)
    detected_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class DataDriftModel(Base):
    __tablename__ = "data_intelligence_drifts"

    drift_id = Column(String(64), primary_key=True, index=True)
    dataset_id = Column(String(64), nullable=False, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    drift_type = Column(String(64), nullable=False)
    severity = Column(String(64), default="LOW")
    drift_score = Column(Float, default=0.0)
    detected_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class DataFreshnessModel(Base):
    __tablename__ = "data_intelligence_freshness"

    freshness_id = Column(String(64), primary_key=True, index=True)
    dataset_id = Column(String(64), nullable=False, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    status = Column(String(64), default="FRESH")
    age_minutes = Column(Float, default=0.0)
    last_updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class DataLineageNodeModel(Base):
    __tablename__ = "data_intelligence_lineage_nodes"

    node_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    node_type = Column(String(64), nullable=False)
    asset_reference_id = Column(String(64), nullable=False)


class DatasetSchemaModel(Base):
    __tablename__ = "data_intelligence_schemas"

    schema_id = Column(String(64), primary_key=True, index=True)
    dataset_id = Column(String(64), nullable=False, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    version_number = Column(String(32), default="1.0.0")
    fields_json = Column(JSON, nullable=False)


class DataPipelineModel(Base):
    __tablename__ = "data_intelligence_pipelines"

    pipeline_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    status = Column(String(64), default="ACTIVE")
    health = Column(String(64), default="HEALTHY")


class DataIncidentModel(Base):
    __tablename__ = "data_intelligence_incidents"

    incident_id = Column(String(64), primary_key=True, index=True)
    dataset_id = Column(String(64), nullable=False, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    severity = Column(String(64), default="P2_HIGH")
    status = Column(String(64), default="DETECTED")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class DataInvestigationModel(Base):
    __tablename__ = "data_intelligence_investigations"

    investigation_id = Column(String(64), primary_key=True, index=True)
    incident_id = Column(String(64), nullable=False)
    tenant_id = Column(String(64), nullable=False, index=True)
    dataset_id = Column(String(64), nullable=False)
    status = Column(String(64), default="OPEN")
    findings = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class DataRemediationPlanModel(Base):
    __tablename__ = "data_intelligence_remediation_plans"

    plan_id = Column(String(64), primary_key=True, index=True)
    incident_id = Column(String(64), nullable=False)
    tenant_id = Column(String(64), nullable=False, index=True)
    dataset_id = Column(String(64), nullable=False)
    status = Column(String(64), default="PROPOSED")
    actions_json = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class DataEvidenceBundleModel(Base):
    __tablename__ = "data_intelligence_evidence_bundles"

    bundle_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    dataset_id = Column(String(64), nullable=False)
    bundle_fingerprint = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class DataLearningRecordModel(Base):
    __tablename__ = "data_intelligence_learning_records"

    record_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    dataset_id = Column(String(64), nullable=False)
    observed_pattern = Column(Text, nullable=False)
    confidence_score = Column(Float, default=0.85)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
