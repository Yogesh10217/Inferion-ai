"""SQLAlchemy Persistence Models for Orchestration Platform Domain Entities."""

from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, String

from app.db.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class WorkflowDefinitionModel(Base):
    __tablename__ = "orchestration_workflow_definitions"

    workflow_id = Column(String(64), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    version = Column(String(32), nullable=False, default="1.0.0")
    tenant_id = Column(String(64), index=True, nullable=False, default="global")
    lifecycle_state = Column(String(32), nullable=False)
    steps = Column(JSON, nullable=False, default=list)
    variables = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)


class WorkflowExecutionModel(Base):
    __tablename__ = "orchestration_workflow_executions"

    execution_id = Column(String(64), primary_key=True, index=True)
    workflow_id = Column(String(64), index=True, nullable=False)
    version = Column(String(32), nullable=False)
    tenant_id = Column(String(64), index=True, nullable=False, default="global")
    case_id = Column(String(64), index=True, nullable=True)
    status = Column(String(32), nullable=False)
    inputs = Column(JSON, nullable=False, default=dict)
    outputs = Column(JSON, nullable=False, default=dict)
    current_step_id = Column(String(64), nullable=True)
    started_at = Column(DateTime(timezone=True), default=_now, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)


class HumanTaskModel(Base):
    __tablename__ = "orchestration_human_tasks"

    task_id = Column(String(64), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    tenant_id = Column(String(64), index=True, nullable=False, default="global")
    case_id = Column(String(64), index=True, nullable=True)
    execution_id = Column(String(64), index=True, nullable=True)
    assigned_user_id = Column(String(64), nullable=True)
    assigned_role = Column(String(64), nullable=True)
    status = Column(String(32), nullable=False)
    priority = Column(String(32), nullable=False)
    inputs = Column(JSON, nullable=False, default=dict)
    outputs = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)


class CaseModel(Base):
    __tablename__ = "orchestration_cases"

    case_id = Column(String(64), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    case_type = Column(String(64), nullable=False)
    tenant_id = Column(String(64), index=True, nullable=False, default="global")
    status = Column(String(32), nullable=False)
    priority = Column(String(32), nullable=False)
    extra_metadata = Column("metadata", JSON, nullable=False, default=dict)
    timeline = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)
