"""SQLAlchemy Production Models for FinOps Intelligence (Phase 5.42)."""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, DateTime, Integer, JSON, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class CostRecordModel(Base):
    __tablename__ = "finops_cost_records"

    record_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    category = Column(String(64), nullable=False)
    amount_usd = Column(Float, nullable=False, default=0.0)
    dimensions = Column(JSON, nullable=True)
    recorded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class UsageRecordModel(Base):
    __tablename__ = "finops_usage_records"

    usage_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    resource_type = Column(String(64), nullable=False)
    resource_id = Column(String(64), nullable=False)
    metrics = Column(JSON, nullable=False)
    sanitized_metadata = Column(JSON, nullable=True)
    recorded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class CostAllocationModel(Base):
    __tablename__ = "finops_cost_allocations"

    allocation_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    cost_record_id = Column(String(64), nullable=False)
    rules = Column(JSON, nullable=False)
    allocated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class BudgetModel(Base):
    __tablename__ = "finops_budgets"

    budget_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    amount_usd = Column(Float, nullable=False)
    warning_threshold_pct = Column(Float, default=75.0)
    critical_threshold_pct = Column(Float, default=90.0)
    period = Column(String(64), default="MONTHLY")
    current_spend_usd = Column(Float, default=0.0)
    status = Column(String(64), default="NORMAL")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ForecastModel(Base):
    __tablename__ = "finops_forecasts"

    forecast_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    projected_spend_usd = Column(Float, nullable=False)
    confidence = Column(String(64), default="HIGH")
    scenario = Column(String(64), default="BASELINE")
    period = Column(String(64), default="MONTHLY")
    reasoning = Column(Text, nullable=False)
    generated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class CostAnomalyModel(Base):
    __tablename__ = "finops_anomalies"

    anomaly_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    anomaly_type = Column(String(64), nullable=False)
    severity = Column(String(64), default="HIGH")
    status = Column(String(64), default="DETECTED")
    expected_amount_usd = Column(Float, default=0.0)
    actual_amount_usd = Column(Float, default=0.0)
    deviation_pct = Column(Float, default=0.0)
    resource_id = Column(String(64), nullable=False)
    detected_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class OptimizationRecommendationModel(Base):
    __tablename__ = "finops_optimizations"

    optimization_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    target_resource_id = Column(String(64), nullable=False)
    optimization_type = Column(String(64), nullable=False)
    estimated_monthly_savings_usd = Column(Float, default=0.0)
    priority = Column(String(64), default="P2")
    impact = Column(String(64), default="MEDIUM")
    status = Column(String(64), default="PROPOSED")
    is_high_risk = Column(Boolean, default=False)
    action_summary = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class FinOpsInvestigationModel(Base):
    __tablename__ = "finops_investigations"

    investigation_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    target_anomaly_id = Column(String(64), nullable=True)
    status = Column(String(64), default="OPEN")
    findings = Column(JSON, nullable=True)
    is_concluded = Column(Boolean, default=False)
    snapshot_id = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    concluded_at = Column(DateTime(timezone=True), nullable=True)


class EvidenceBundleModel(Base):
    __tablename__ = "finops_evidence_bundles"

    bundle_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    items = Column(JSON, nullable=False)
    sha256_hash = Column(String(64), nullable=True)
    is_finalized = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class LearningRecordModel(Base):
    __tablename__ = "finops_learning_records"

    record_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    pattern_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    recommendations = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
