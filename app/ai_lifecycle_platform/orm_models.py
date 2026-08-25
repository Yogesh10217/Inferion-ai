"""SQLAlchemy Database ORM Models for AI Lifecycle Platform (Phase 5.33)."""

from sqlalchemy import Column, String, Float, DateTime, JSON, Text, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone

Base = declarative_base()


class AIAssetModel(Base):
    __tablename__ = "ai_lifecycle_assets"

    asset_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    name = Column(String(128), nullable=False)
    asset_type = Column(String(32), nullable=False)
    status = Column(String(32), nullable=False)
    lifecycle_stage = Column(String(32), nullable=False)
    metadata_json = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    contract_version = Column(String(16), default="1.0.0")


class DatasetModel(Base):
    __tablename__ = "ai_lifecycle_datasets"

    dataset_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    name = Column(String(128), nullable=False)
    classification = Column(String(32), nullable=False)
    status = Column(String(32), nullable=False)
    versions_json = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    contract_version = Column(String(16), default="1.0.0")


class AIModelModel(Base):
    __tablename__ = "ai_lifecycle_models"

    model_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    name = Column(String(128), nullable=False)
    model_type = Column(String(32), nullable=False)
    framework = Column(String(32), nullable=False)
    current_stage = Column(String(32), nullable=False)
    versions_json = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    contract_version = Column(String(16), default="1.0.0")


class AIAgentModel(Base):
    __tablename__ = "ai_lifecycle_agents"

    agent_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    name = Column(String(128), nullable=False)
    agent_type = Column(String(32), nullable=False)
    autonomy_level = Column(String(32), nullable=False)
    status = Column(String(32), nullable=False)
    versions_json = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    contract_version = Column(String(16), default="1.0.0")


class LineageGraphModel(Base):
    __tablename__ = "ai_lifecycle_lineages"

    graph_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    nodes_json = Column(JSON, nullable=False)
    edges_json = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    contract_version = Column(String(16), default="1.0.0")


class AIArtifactModel(Base):
    __tablename__ = "ai_lifecycle_artifacts"

    artifact_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    name = Column(String(128), nullable=False)
    artifact_type = Column(String(32), nullable=False)
    status = Column(String(32), nullable=False)
    reference_uri = Column(String(512), nullable=False)
    sha256_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    contract_version = Column(String(16), default="1.0.0")


class EvaluationRunModel(Base):
    __tablename__ = "ai_lifecycle_evaluations"

    run_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    target_asset_id = Column(String(64), nullable=False, index=True)
    suite_id = Column(String(64), nullable=False)
    status = Column(String(32), nullable=False)
    results_json = Column(JSON, nullable=False)
    overall_passed = Column(Boolean, nullable=False, default=True)
    executed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    contract_version = Column(String(16), default="1.0.0")


class LifecycleGateModel(Base):
    __tablename__ = "ai_lifecycle_gates"

    gate_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    name = Column(String(128), nullable=False)
    gate_type = Column(String(32), nullable=False)
    is_hard_gate = Column(Boolean, nullable=False, default=True)
    requirements_json = Column(JSON, nullable=False)
    contract_version = Column(String(16), default="1.0.0")


class PromotionRequestModel(Base):
    __tablename__ = "ai_lifecycle_promotions"

    request_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    asset_id = Column(String(64), nullable=False, index=True)
    target = Column(String(32), nullable=False)
    is_high_risk = Column(Boolean, nullable=False, default=False)
    status = Column(String(32), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    contract_version = Column(String(16), default="1.0.0")


class AIReleaseModel(Base):
    __tablename__ = "ai_lifecycle_releases"

    release_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    title = Column(String(256), nullable=False)
    status = Column(String(32), nullable=False)
    risk_level = Column(String(32), nullable=False)
    candidate_json = Column(JSON, nullable=False)
    fingerprint = Column(String(128), nullable=True)
    finalized_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    contract_version = Column(String(16), default="1.0.0")


class DeploymentPlanModel(Base):
    __tablename__ = "ai_lifecycle_deployments"

    plan_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    release_id = Column(String(64), nullable=False, index=True)
    idempotency_key = Column(String(128), nullable=False)
    target = Column(String(32), nullable=False)
    status = Column(String(32), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    contract_version = Column(String(16), default="1.0.0")


class DriftDetectionModel(Base):
    __tablename__ = "ai_lifecycle_drifts"

    drift_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    asset_id = Column(String(64), nullable=False, index=True)
    drift_type = Column(String(32), nullable=False)
    severity = Column(String(32), nullable=False)
    status = Column(String(32), nullable=False)
    evidence_json = Column(JSON, nullable=True)
    detected_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    contract_version = Column(String(16), default="1.0.0")


class RollbackRequestModel(Base):
    __tablename__ = "ai_lifecycle_rollbacks"

    request_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    asset_id = Column(String(64), nullable=False, index=True)
    target_version = Column(String(32), nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(String(32), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    contract_version = Column(String(16), default="1.0.0")


class RetirementRequestModel(Base):
    __tablename__ = "ai_lifecycle_retirements"

    retirement_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    asset_id = Column(String(64), nullable=False, index=True)
    reason = Column(String(64), nullable=False)
    status = Column(String(32), nullable=False)
    fingerprint = Column(String(128), nullable=True)
    finalized_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    contract_version = Column(String(16), default="1.0.0")


class LifecycleSnapshotModel(Base):
    __tablename__ = "ai_lifecycle_snapshots"

    snapshot_id = Column(String(64), primary_key=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    asset_id = Column(String(64), nullable=False, index=True)
    snapshot_json = Column(JSON, nullable=False)
    fingerprint = Column(String(128), nullable=True)
    finalized_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    contract_version = Column(String(16), default="1.0.0")
