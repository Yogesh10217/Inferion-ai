"""SQLAlchemy Database Models for Observability Persistence."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class TraceModel(Base):
    """Persistent database model for a Trace."""
    __tablename__ = "observability_traces"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    trace_id = Column(String(64), unique=True, nullable=False, index=True)
    execution_id = Column(String(64), index=True, nullable=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    organization_id = Column(String(64), nullable=False, index=True)
    workspace_id = Column(String(64), nullable=False, index=True)
    status = Column(String(32), default="OK", index=True)
    total_duration_ms = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    total_tokens = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    spans = relationship("SpanModel", back_populates="trace", cascade="all, delete-orphan")


class SpanModel(Base):
    """Persistent database model for an Execution Span."""
    __tablename__ = "observability_spans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    span_id = Column(String(64), unique=True, nullable=False, index=True)
    trace_id = Column(String(64), ForeignKey("observability_traces.trace_id", ondelete="CASCADE"), nullable=False, index=True)
    parent_span_id = Column(String(64), index=True, nullable=True)
    name = Column(String(128), nullable=False, index=True)
    component = Column(String(64), nullable=False, index=True)
    status = Column(String(32), default="OK", index=True)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=True)
    duration_ms = Column(Float, default=0.0)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    attributes = Column(JSON, default=dict)
    events = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    trace = relationship("TraceModel", back_populates="spans")


class ExecutionEventModel(Base):
    """Persistent model for discrete Execution Events."""
    __tablename__ = "observability_execution_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    trace_id = Column(String(64), nullable=False, index=True)
    span_id = Column(String(64), nullable=True, index=True)
    execution_id = Column(String(64), nullable=True, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    name = Column(String(128), nullable=False)
    event_type = Column(String(64), nullable=False, index=True)
    attributes = Column(JSON, default=dict)
    timestamp = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ExecutionSnapshotModel(Base):
    """Persistent model for Execution Replay Snapshots."""
    __tablename__ = "observability_snapshots"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    snapshot_id = Column(String(64), unique=True, nullable=False, index=True)
    execution_id = Column(String(64), unique=True, nullable=False, index=True)
    trace_id = Column(String(64), nullable=False, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    organization_id = Column(String(64), nullable=False)
    workspace_id = Column(String(64), nullable=False)
    component = Column(String(64), nullable=False)
    inputs = Column(JSON, default=dict)
    config = Column(JSON, default=dict)
    original_output = Column(JSON, nullable=True)
    original_status = Column(String(32), default="COMPLETED")
    is_high_risk = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class AlertModel(Base):
    """Persistent model for System Alerts."""
    __tablename__ = "observability_alerts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    alert_id = Column(String(64), unique=True, nullable=False, index=True)
    title = Column(String(128), nullable=False)
    condition_type = Column(String(64), nullable=False, index=True)
    level = Column(String(16), nullable=False, index=True)  # INFO, WARNING, CRITICAL
    status = Column(String(16), nullable=False, default="FIRING", index=True)  # FIRING, ACKNOWLEDGED, RESOLVED
    message = Column(Text, nullable=False)
    tenant_id = Column(String(64), nullable=False, index=True)
    organization_id = Column(String(64), nullable=False)
    workspace_id = Column(String(64), nullable=False)
    execution_id = Column(String(64), nullable=True)
    component = Column(String(64), nullable=True)
    attributes = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    acknowledged_by = Column(String(64), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)


class SLODefinitionModel(Base):
    """Persistent model for SLO Rule Definitions."""
    __tablename__ = "observability_slo_definitions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    slo_id = Column(String(64), unique=True, nullable=False, index=True)
    name = Column(String(128), nullable=False)
    target_component = Column(String(64), nullable=False, index=True)
    metric_name = Column(String(64), nullable=False)
    comparator = Column(String(8), nullable=False)  # <=, >=, <, >
    target_value = Column(Float, nullable=False)
    warning_threshold = Column(Float, nullable=True)
    window_seconds = Column(Integer, default=3600)
    tenant_id = Column(String(64), nullable=True, index=True)
    workspace_id = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class SLOViolationModel(Base):
    """Persistent model for SLO Violations."""
    __tablename__ = "observability_slo_violations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    slo_id = Column(String(64), ForeignKey("observability_slo_definitions.slo_id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(32), nullable=False)
    current_value = Column(Float, nullable=False)
    target_value = Column(Float, nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class AnomalyEventModel(Base):
    """Persistent model for Statistical Anomaly Events."""
    __tablename__ = "observability_anomaly_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    anomaly_id = Column(String(64), unique=True, nullable=False, index=True)
    metric_name = Column(String(64), nullable=False)
    anomaly_type = Column(String(64), nullable=False, index=True)
    severity = Column(String(16), nullable=False, index=True)
    current_value = Column(Float, nullable=False)
    baseline_value = Column(Float, nullable=False)
    threshold = Column(Float, nullable=False)
    component = Column(String(64), nullable=False, index=True)
    message = Column(Text, nullable=False)
    attributes = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class EvaluationResultModel(Base):
    """Persistent model for Quality Evaluation Metrics."""
    __tablename__ = "observability_evaluations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    execution_id = Column(String(64), nullable=False, index=True)
    agent_id = Column(String(64), nullable=True, index=True)
    workflow_id = Column(String(64), nullable=True, index=True)
    model_id = Column(String(64), nullable=True, index=True)
    task_completion_rate = Column(Float, default=0.0)
    planning_confidence = Column(Float, default=0.0)
    critique_score = Column(Float, default=0.0)
    user_feedback_score = Column(Float, nullable=True)
    hallucination_signal = Column(Float, nullable=True)
    overall_quality_score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
