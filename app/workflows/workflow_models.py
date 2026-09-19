"""
Workflow Database Persistence Models (SQLAlchemy)
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class WorkflowModel(Base):
    __tablename__ = "workflows"

    id = Column(String(64), primary_key=True, default=lambda: f"wf_{uuid.uuid4().hex[:12]}")
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    organization_id = Column(String(64), nullable=False, index=True)
    workspace_id = Column(String(64), nullable=True, index=True)
    version = Column(Integer, default=1)
    status = Column(String(32), nullable=False, default="READY")
    graph_json = Column(JSON, nullable=True)
    config_json = Column(JSON, nullable=True)
    created_by = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    runs = relationship("WorkflowRunModel", back_populates="workflow", cascade="all, delete-orphan")


class WorkflowVersionModel(Base):
    __tablename__ = "workflow_versions"

    id = Column(String(64), primary_key=True, default=lambda: f"wfv_{uuid.uuid4().hex[:12]}")
    workflow_id = Column(String(64), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True)
    version = Column(Integer, nullable=False)
    graph_data = Column(JSON, nullable=False)
    config_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class WorkflowRunModel(Base):
    __tablename__ = "workflow_runs"

    id = Column(String(64), primary_key=True, default=lambda: f"run_{uuid.uuid4().hex[:12]}")
    workflow_id = Column(String(64), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(String(64), nullable=False, index=True)
    workspace_id = Column(String(64), nullable=True, index=True)
    status = Column(String(32), nullable=False, default="PENDING")
    input_params = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    current_node_id = Column(String(64), nullable=True)
    error = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    workflow = relationship("WorkflowModel", back_populates="runs")
    steps = relationship("WorkflowStepModel", back_populates="run", cascade="all, delete-orphan")
    checkpoints = relationship("WorkflowCheckpointModel", back_populates="run", cascade="all, delete-orphan")
    approvals = relationship("WorkflowApprovalModel", back_populates="run", cascade="all, delete-orphan")


class WorkflowStepModel(Base):
    __tablename__ = "workflow_steps"

    id = Column(String(64), primary_key=True, default=lambda: f"step_{uuid.uuid4().hex[:12]}")
    run_id = Column(String(64), ForeignKey("workflow_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    node_id = Column(String(64), nullable=False)
    node_type = Column(String(32), nullable=False)
    status = Column(String(32), nullable=False, default="PENDING")
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    run = relationship("WorkflowRunModel", back_populates="steps")


class WorkflowCheckpointModel(Base):
    __tablename__ = "workflow_checkpoints"

    id = Column(String(64), primary_key=True, default=lambda: f"chk_{uuid.uuid4().hex[:12]}")
    run_id = Column(String(64), ForeignKey("workflow_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    step_id = Column(String(64), nullable=True)
    node_id = Column(String(64), nullable=False)
    state_snapshot = Column(JSON, nullable=False)
    completed_nodes = Column(JSON, nullable=True)
    memory_state = Column(JSON, nullable=True)
    agent_outputs = Column(JSON, nullable=True)
    tool_outputs = Column(JSON, nullable=True)
    artifacts = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    run = relationship("WorkflowRunModel", back_populates="checkpoints")


class WorkflowApprovalModel(Base):
    __tablename__ = "workflow_approvals"

    id = Column(String(64), primary_key=True, default=lambda: f"appr_{uuid.uuid4().hex[:12]}")
    run_id = Column(String(64), ForeignKey("workflow_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    node_id = Column(String(64), nullable=False)
    status = Column(String(32), nullable=False, default="PENDING")
    prompt = Column(Text, nullable=False)
    requested_to = Column(String(64), nullable=True)
    decision = Column(String(32), nullable=True)
    feedback = Column(Text, nullable=True)
    decided_by = Column(String(64), nullable=True)
    requested_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    decided_at = Column(DateTime, nullable=True)

    run = relationship("WorkflowRunModel", back_populates="approvals")


class WorkflowArtifactModel(Base):
    __tablename__ = "workflow_artifacts"

    id = Column(String(64), primary_key=True, default=lambda: f"art_{uuid.uuid4().hex[:12]}")
    run_id = Column(String(64), ForeignKey("workflow_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    step_id = Column(String(64), nullable=True)
    name = Column(String(255), nullable=False)
    artifact_type = Column(String(64), nullable=False)
    storage_path = Column(Text, nullable=False)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
