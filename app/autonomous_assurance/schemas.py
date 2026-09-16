"""
Pydantic API Schemas for Phase 5.53 Autonomous Assurance Platform.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class WorkflowCreateRequest(BaseModel):
    title: str = Field(..., description="Title of the workflow request")
    description: Optional[str] = Field(None, description="Detailed description")
    workflow_type: str = Field("CROSS_DOMAIN_COORDINATION", description="Workflow type")
    priority: str = Field("MEDIUM", description="Workflow priority")
    risk_level: str = Field("MEDIUM", description="Assessed risk level")
    target_resource_id: str = Field("res_001", description="Target resource ID")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PlanCreateRequest(BaseModel):
    risk_score: float = Field(20.0, description="Risk score")
    trust_score: float = Field(90.0, description="Trust score")


class WorkflowApprovalRequest(BaseModel):
    approved_by: str = Field(..., description="Approver identity")
    approved: bool = Field(..., description="Approved or rejected")
    comments: Optional[str] = Field(None, description="Approval comments")


class WorkflowResponse(BaseModel):
    workflow_id: str
    tenant_id: str
    title: str
    description: Optional[str] = None
    workflow_type: str
    status: str
    priority: str
    plan_id: Optional[str] = None
    delegation_id: Optional[str] = None
    verification_id: Optional[str] = None
    evidence_id: Optional[str] = None
    is_finalized: bool
    created_at: str
    updated_at: str


class PlanResponse(BaseModel):
    plan_id: str
    workflow_id: str
    tenant_id: str
    plan_steps: List[Dict[str, Any]]
    risk_score: float
    trust_score: float
    requires_approval: bool
    created_at: str


class DelegationResponse(BaseModel):
    delegation_id: str
    workflow_id: str
    tenant_id: str
    target_subsystem: str
    action_type: str
    delegation_request: Dict[str, Any]
    created_at: str


class VerificationResponse(BaseModel):
    verification_id: str
    workflow_id: str
    tenant_id: str
    delegation_id: str
    status: str
    passed_checks: List[str]
    metrics_summary: Dict[str, Any]
    verified_at: str


class RecoveryResponse(BaseModel):
    recovery_id: str
    workflow_id: str
    tenant_id: str
    failure_reason: str
    recovery_steps: List[Dict[str, Any]]
    created_at: str


class AssuranceResponse(BaseModel):
    score_id: str
    workflow_id: str
    tenant_id: str
    overall_assurance_score: float
    assurance_rating: str
    evaluated_at: str
