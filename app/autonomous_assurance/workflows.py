"""
Autonomous Workflows Core Domain Subsystem.
Defines workflow data structures, status enums, types, priorities, and metadata.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class WorkflowType(str, Enum):
    SECURITY_REMEDIATION = "SECURITY_REMEDIATION"
    INCIDENT_RESPONSE = "INCIDENT_RESPONSE"
    IDENTITY_GOVERNANCE = "IDENTITY_GOVERNANCE"
    OPERATIONS_ASSURANCE = "OPERATIONS_ASSURANCE"
    POLICY_ENFORCEMENT = "POLICY_ENFORCEMENT"
    KNOWLEDGE_SYNC = "KNOWLEDGE_SYNC"
    DECISION_ORCHESTRATION = "DECISION_ORCHESTRATION"
    CROSS_DOMAIN_COORDINATION = "CROSS_DOMAIN_COORDINATION"


class WorkflowStatus(str, Enum):
    PROPOSED = "PROPOSED"
    ANALYZING = "ANALYZING"
    PLANNED = "PLANNED"
    GOVERNANCE_EVALUATED = "GOVERNANCE_EVALUATED"
    REQUIRES_APPROVAL = "REQUIRES_APPROVAL"
    APPROVED = "APPROVED"
    COORDINATING = "COORDINATING"
    DELEGATED = "DELEGATED"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"
    DENIED = "DENIED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    COMPENSATING = "COMPENSATING"
    RECOVERING = "RECOVERING"
    PARTIALLY_COMPLETED = "PARTIALLY_COMPLETED"


WorkflowState = WorkflowStatus


class WorkflowPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    EMERGENCY = "EMERGENCY"


class WorkflowMetadata(BaseModel):
    source_system: str = "UNIFIED_INTELLIGENCE"
    target_resource_id: str = "res_001"
    risk_level: str = "MEDIUM"
    trust_band: str = "HIGH_TRUST"
    confidence_score: float = 0.95
    tags: List[str] = Field(default_factory=list)
    custom: Dict[str, Any] = Field(default_factory=dict)


class AutonomousWorkflow(BaseModel):
    workflow_id: str = Field(default_factory=lambda: f"wf_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    title: str
    description: Optional[str] = None
    workflow_type: WorkflowType = WorkflowType.CROSS_DOMAIN_COORDINATION
    status: WorkflowStatus = WorkflowStatus.PROPOSED
    priority: WorkflowPriority = WorkflowPriority.MEDIUM
    plan_id: Optional[str] = None
    delegation_id: Optional[str] = None
    verification_id: Optional[str] = None
    evidence_id: Optional[str] = None
    is_finalized: bool = False
    workflow_fingerprint: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    metadata: WorkflowMetadata = Field(default_factory=WorkflowMetadata)

    @property
    def state(self) -> WorkflowStatus:
        return self.status
