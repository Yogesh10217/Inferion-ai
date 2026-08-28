"""SQLAlchemy Production ORM Models for Agent Orchestration Persistence (Phase 5.36)."""

from datetime import datetime, timezone
import uuid
from typing import Optional

from sqlalchemy import Column, String, DateTime, JSON, Float, Boolean, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def _now():
    return datetime.now(timezone.utc)


class EnterpriseAgentModel(Base):
    __tablename__ = "agent_orchestration_agents"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"agent_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    agent_type: Mapped[str] = mapped_column(String, default="GENERAL")
    status: Mapped[str] = mapped_column(String, default="ACTIVE")
    role: Mapped[str] = mapped_column(String, default="TASK_EXECUTOR")
    capabilities_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    autonomy_policy_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class AgentCapabilityModel(Base):
    __tablename__ = "agent_orchestration_capabilities"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"cap_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    scopes_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    permissions_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    constraints_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class AgentAutonomyPolicyModel(Base):
    __tablename__ = "agent_orchestration_autonomy_policies"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"autopoly_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    agent_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    autonomy_level: Mapped[str] = mapped_column(String, default="SUPERVISED")
    boundary_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class AgentTaskModel(Base):
    __tablename__ = "agent_orchestration_tasks"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"task_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    agent_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    task_type: Mapped[str] = mapped_column(String, default="EXECUTION")
    priority: Mapped[str] = mapped_column(String, default="MEDIUM")
    status: Mapped[str] = mapped_column(String, default="CREATED")
    input_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    context_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    result_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class AgentPlanModel(Base):
    __tablename__ = "agent_orchestration_plans"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"plan_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    task_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    agent_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    version: Mapped[str] = mapped_column(String, default="1.0.0")
    status: Mapped[str] = mapped_column(String, default="DRAFT")
    steps_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    decision_analysis_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class AgentExecutionModel(Base):
    __tablename__ = "agent_orchestration_executions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"exec_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    agent_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    task_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    plan_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String, default="PENDING")
    steps_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    trace_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class AgentRuntimeSessionModel(Base):
    __tablename__ = "agent_orchestration_runtime_sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"rtsess_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    agent_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    execution_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String, default="ACTIVE")
    step_count: Mapped[int] = mapped_column(Integer, default=0)
    consumed_cost: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class AgentCollaborationModel(Base):
    __tablename__ = "agent_orchestration_collaborations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"collab_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    collaboration_type: Mapped[str] = mapped_column(String, default="SUPERVISOR_WORKER")
    status: Mapped[str] = mapped_column(String, default="INITIATED")
    participants_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    messages_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class AgentTraceModel(Base):
    __tablename__ = "agent_orchestration_traces"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"trace_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    agent_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    task_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String, default="RECORDING")
    fingerprint: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    snapshot_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class AgentFailureModel(Base):
    __tablename__ = "agent_orchestration_failures"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"agentfail_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    agent_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    task_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    failure_type: Mapped[str] = mapped_column(String, nullable=False)
    severity: Mapped[str] = mapped_column(String, default="MEDIUM")
    error_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class AgentLearningModel(Base):
    __tablename__ = "agent_orchestration_learnings"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"learn_{uuid.uuid4().hex[:12]}")
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    agent_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    source_execution_id: Mapped[str] = mapped_column(String, nullable=False)
    learnings_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
